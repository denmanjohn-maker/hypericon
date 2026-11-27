import Foundation

public struct EngineStatus: Equatable, Sendable {
    public enum Activity: String, Sendable { case idle, scanning, restoring }
    public var activity: Activity = .idle
    public var themedFolders = 0
    public var lastScan: Date?
}

public struct RestoreReport: Equatable, Sendable {
    public var restored = 0
    public var missing = 0
    /// Disks that could not be put back yet: unplugged (they are restored when connected again), or the
    /// startup disk when the password prompt was cancelled.
    public var pending = 0
}

/// Applies the active theme to eligible folders, favorites, the home folder and disks, and can undo
/// everything it has done.
/// All work happens on one serial queue; public methods are safe to call from any thread.
public final class Engine {
    public let paths: AppPaths
    public let home: URL
    public let journal: Journal
    public var onStatus: ((EngineStatus) -> Void)?

    private let themeStore: ThemeStore
    private let setter: IconSetter
    private let system: SystemPlaces
    /// Disks whose icon could not be set (for example a read-only network share), by UUID, with the settings
    /// generation they failed in. They are not tried again until settings change or a disk is mounted.
    private var failedVolumes: [String: Int] = [:]
    private let queue = DispatchQueue(label: "com.hypericon.engine", qos: .utility)
    private let stateLock = NSLock()
    private var _settings: Preferences
    private var _status = EngineStatus()
    private var generation = 0

    /// Home-level folders whose purpose is fixed regardless of what is in them.
    private static let wellKnown: [String: FolderCategory] = [
        "Documents": .documents, "Pictures": .images, "Music": .music, "Movies": .video,
    ]

    public init(paths: AppPaths = AppPaths(), themeStore: ThemeStore, setter: IconSetter = WorkspaceIconSetter(),
                home: URL = FileManager.default.homeDirectoryForCurrentUser, system: SystemPlaces = .none) {
        self.paths = paths
        self.home = home.canonicalFolder
        self.themeStore = themeStore
        self.setter = setter
        self.system = system
        paths.ensure()
        journal = Journal(url: paths.journal)
        // Finished icons are cheap to rebuild; start clean so edited themes are picked up.
        try? FileManager.default.removeItem(at: paths.cache)
        _settings = Preferences.load(from: paths.settings)
        _status.themedFolders = journal.count
    }

    // MARK: state

    public var settings: Preferences {
        stateLock.lock()
        defer { stateLock.unlock() }
        return _settings
    }

    public var status: EngineStatus {
        stateLock.lock()
        defer { stateLock.unlock() }
        return _status
    }

    public var themes: [Theme] { themeStore.load() }

    /// Saves new settings. Call `applyAll()` afterwards if they change what should be themed.
    public func update(_ change: (inout Preferences) -> Void) {
        stateLock.lock()
        change(&_settings)
        let snapshot = _settings
        generation += 1
        stateLock.unlock()
        snapshot.save(to: paths.settings)
    }

    /// Saves a change HyperIcon makes on its own, without counting as a settings change (which would stop a
    /// scan in progress and retry disks that failed).
    private func record(_ change: (inout Preferences) -> Void) {
        stateLock.lock()
        change(&_settings)
        let snapshot = _settings
        stateLock.unlock()
        snapshot.save(to: paths.settings)
    }

    private func setStatus(_ change: (inout EngineStatus) -> Void) {
        stateLock.lock()
        change(&_status)
        _status.themedFolders = journal.count
        let snapshot = _status
        stateLock.unlock()
        onStatus?(snapshot)
    }

    private var currentGeneration: Int {
        stateLock.lock()
        defer { stateLock.unlock() }
        return generation
    }

    private struct Context {
        let settings: Preferences
        let theme: Theme
        let classifier: Classifier
        let scanner: FolderScanner
    }

    private func makeContext() -> Context? {
        let settings = self.settings
        guard !settings.paused, let id = settings.themeID, let theme = themes.first(where: { $0.id == id }) else { return nil }
        let rules = RuleSet.load(overridesAt: paths.rules)
        return Context(settings: settings, theme: theme,
                       classifier: Classifier(rules: rules, preferGit: settings.preferGit),
                       scanner: FolderScanner(home: home, maxDepth: settings.maxDepth, skipNames: Set(rules.skipNames),
                                        excludedPaths: settings.excludedPaths))
    }

    // MARK: applying

    /// Scans the home folder and themes every eligible folder. Returns immediately; work continues in the background.
    public func applyAll() {
        queue.async { self.applyAllNow() }
    }

    /// Synchronous variant of `applyAll()`, used by the command line and tests.
    public func applyAllNow() {
        guard let context = makeContext() else {
            // Paused or no theme: nothing is themed, but unplugged disks waiting to be restored still are.
            syncDisks(context: nil, includeBootDisk: false)
            return
        }
        let started = currentGeneration
        setStatus { $0.activity = .scanning }
        var seen = Set<String>()
        var processed = 0
        context.scanner.walk { folder in
            seen.insert(folder.path)
            self.apply(to: folder, context: context)
            processed += 1
            if processed % 50 == 0 { self.setStatus { _ in } }
            return self.currentGeneration == started
        }
        applyFixedPlaces(context: context, seen: &seen)
        if currentGeneration == started {
            // Folders that were deleted or moved no longer need an entry; folders that fell out of scope get their icon back.
            // Disks are handled by `syncDisks`, because an unplugged disk is not gone.
            for entry in journal.all where entry.volumeUUID == nil && entry.place != .bootDisk && !seen.contains(entry.path) {
                restore(entry)
            }
            syncDisks(context: context, includeBootDisk: true)
        }
        setStatus {
            $0.activity = .idle
            $0.lastScan = Date()
        }
    }

    /// Themes disks that were just connected and restores ones that were waiting to be. Call when a disk is mounted.
    public func handleVolumesChanged() {
        queue.async {
            // A disk that was just plugged in (or plugged in again) gets a fresh try.
            self.failedVolumes.removeAll()
            self.syncDisks(context: self.makeContext(), includeBootDisk: false)
            self.setStatus { _ in }
        }
    }

    /// Re-evaluates folders reported by the file-system watcher, plus any new subfolders inside them.
    public func handleChanges(in changedPaths: [String]) {
        queue.async {
            guard let context = self.makeContext() else { return }
            var candidates = Set<String>()
            for path in changedPaths {
                let url = URL(fileURLWithPath: path, isDirectory: true).canonicalFolder
                // The changed item itself (a folder whose tag colour changed) and the folder it is in
                // (whose contents changed).
                candidates.insert(url.path)
                candidates.insert(url.deletingLastPathComponent().path)
                let children = (try? FileManager.default.contentsOfDirectory(at: url, includingPropertiesForKeys: nil, options: [.skipsHiddenFiles])) ?? []
                for child in children.prefix(500) where self.journal[child.path] == nil {
                    candidates.insert(child.path)
                }
            }
            var changed = false
            for path in candidates.sorted() {
                let url = URL(fileURLWithPath: path, isDirectory: true)
                guard context.scanner.isEligible(url) else { continue }
                if self.apply(to: url, context: context) { changed = true }
            }
            if changed { self.setStatus { _ in } }
        }
    }

    private func resolveCategory(for folder: URL, context: Context) -> FolderCategory {
        if folder.deletingLastPathComponent().path == home.path, let fixed = Self.wellKnown[folder.lastPathComponent] {
            return fixed
        }
        return context.classifier.classify(folder)
    }

    /// A favorite folder directly in the home folder, when favorites are themed.
    private func favoritePlace(for folder: URL, context: Context) -> Place? {
        guard context.settings.themeFavorites, folder.deletingLastPathComponent().path == home.path else { return nil }
        return Place.homeFolders[folder.lastPathComponent]
    }

    /// Returns true if the folder's icon was changed.
    @discardableResult
    private func apply(to folder: URL, context: Context) -> Bool {
        if let place = favoritePlace(for: folder, context: context), let icon = context.theme.placeIconURL(for: place) {
            return set({ icon }, on: .folder(folder), category: .folder, place: place, color: nil, context: context)
        }
        let category = resolveCategory(for: folder, context: context)
        let color = context.settings.matchTagColor ? FolderColor.of(folder) : .blue
        return set({ self.finishedIcon(for: category, color: color, theme: context.theme) }, on: .folder(folder),
                   category: category, place: nil, color: color, context: context)
    }

    /// Something that gets an icon: a folder (keyed by its path) or a disk (keyed by its UUID).
    private struct Target {
        let url: URL
        let key: String
        let volumeUUID: String?

        static func folder(_ url: URL) -> Target { Target(url: url, key: url.path, volumeUUID: nil) }
        static func volume(_ volume: MountedVolume) -> Target { Target(url: volume.url, key: volume.journalKey, volumeUUID: volume.uuid) }
    }

    /// Gives `target` an icon, journaling it first. `makeIcon` is only called when the icon needs to change.
    /// Returns true if the icon was changed.
    @discardableResult
    private func set(_ makeIcon: () -> URL?, on target: Target, category: FolderCategory, place: Place?, color: FolderColor?,
                     context: Context) -> Bool {
        let existing = journal[target.key]
        let hasIcon = setter.hasCustomIcon(target.url)
        let mountPath = target.volumeUUID == nil ? nil : target.url.path
        if let existing, existing.themeID == context.theme.id, existing.category == category, existing.place == place,
           existing.color == color, existing.mountPath == mountPath, existing.pendingRestore != true, hasIcon {
            return false
        }
        if let uuid = target.volumeUUID {
            if failedVolumes[uuid] == currentGeneration { return false }
            guard FileManager.default.isWritableFile(atPath: target.url.path) else {
                failedVolumes[uuid] = currentGeneration
                return false
            }
        }
        guard let icon = makeIcon() else { return false }

        var entry = existing ?? JournalEntry(path: target.key, category: category, themeID: context.theme.id)
        entry.category = category
        entry.themeID = context.theme.id
        entry.color = color
        entry.place = place
        entry.volumeUUID = target.volumeUUID
        entry.mountPath = mountPath
        entry.pendingRestore = nil
        entry.date = Date()

        if existing == nil, hasIcon, !Xattr.has(appliedAttribute, on: target.url) {
            // The user gave this folder or disk its own icon.
            guard context.settings.overrideCustomIcons else { return false }
            let name = UUID().uuidString + ".tiff"
            guard setter.backUpIcon(of: target.url, to: paths.backups.appendingPathComponent(name)) else { return false }
            entry.backup = name
        }
        if target.volumeUUID == nil, FolderScanner.isGitRepository(target.url), !entry.gitExclude {
            entry.gitExclude = GitExclude.add(to: target.url)
        }

        journal.record(entry)
        guard setter.setIcon(icon, for: target.url) else {
            if existing == nil { undoBookkeeping(entry) }
            if let uuid = target.volumeUUID { failedVolumes[uuid] = currentGeneration }
            return false
        }
        Xattr.set(appliedAttribute, value: "\(context.theme.id)/\(place?.rawValue ?? category.rawValue)", on: target.url)
        return true
    }

    // MARK: places outside the scan

    /// The home folder and /Applications, which the scanner never visits. Adds the ones that are themed to `seen`.
    private func applyFixedPlaces(context: Context, seen: inout Set<String>) {
        var places: [(URL, Place, Bool)] = [(home, .home, context.settings.themeHome)]
        if let applications = system.applications {
            places.append((applications.canonicalFolder, .applications, context.settings.themeFavorites))
        }
        for (url, place, enabled) in places where enabled && !context.scanner.isExcluded(url.path) {
            guard let icon = context.theme.placeIconURL(for: place) else { continue }
            // /Applications is only writable by administrators; for anyone else this quietly does nothing.
            set({ icon }, on: .folder(url), category: .folder, place: place, color: nil, context: context)
            if journal[url.path] != nil { seen.insert(url.path) }
        }
    }

    /// The artwork a disk of this kind should get, or nil if it should not be themed.
    private func diskIcon(for place: Place, at url: URL?, context: Context) -> URL? {
        let settings = context.settings
        let enabled: Bool
        switch place {
        case .externalDisk: enabled = settings.themeExternalDisks
        case .networkDisk: enabled = settings.themeNetworkDisks
        case .bootDisk: enabled = settings.themeBootDisk
        default: enabled = false
        }
        if let url, context.scanner.isExcluded(url.canonicalFolder.path) { return nil }
        return enabled ? context.theme.placeIconURL(for: place) : nil
    }

    /// The kinds of disk that are themed in `settings`.
    private static func enabledDiskKinds(_ settings: Preferences) -> Set<Place> {
        var kinds = Set<Place>()
        if settings.themeExternalDisks { kinds.insert(.externalDisk) }
        if settings.themeNetworkDisks { kinds.insert(.networkDisk) }
        return kinds
    }

    /// The kinds of disk HyperIcon has an icon on (or is waiting to restore).
    private var journaledDiskKinds: Set<Place> {
        var kinds = Set<Place>()
        for entry in journal.all where entry.volumeUUID != nil {
            if let place = entry.place, place != .bootDisk {
                kinds.insert(place)
            } else {
                kinds.formUnion([.externalDisk, .networkDisk])
            }
        }
        return kinds
    }

    /// Brings mounted disks in line with the settings. Without a context (paused, or no theme) it only finishes
    /// restoring disks that were unplugged during a restore.
    private func syncDisks(context: Context?, includeBootDisk: Bool) {
        // Disks are only looked at when some kind is themed or HyperIcon still has an icon on one, so macOS
        // does not ask for access to removable and network volumes for nothing.
        let kinds = (context.map { Self.enabledDiskKinds($0.settings) } ?? []).union(journaledDiskKinds)
        if let volumes = system.volumes, !kinds.isEmpty {
            let mounted = volumes.mounted(kinds: kinds)
            let byUUID = Dictionary(mounted.map { ($0.uuid, $0) }, uniquingKeysWith: { first, _ in first })
            for entry in journal.all {
                guard let uuid = entry.volumeUUID, let volume = byUUID[uuid] else { continue }
                if let context {
                    if diskIcon(for: volume.place, at: volume.url, context: context) == nil { restore(entry) }
                } else if entry.pendingRestore == true {
                    restore(entry)
                }
            }
            if let context {
                for volume in mounted {
                    guard let icon = diskIcon(for: volume.place, at: volume.url, context: context) else { continue }
                    set({ icon }, on: .volume(volume), category: .folder, place: volume.place, color: nil, context: context)
                }
            }
        }
        if includeBootDisk, let context { syncBootDisk(context: context) }
    }

    private static let bootDiskKey = "volume:boot"

    /// Themes or restores the startup disk. Each change asks for a password, so it only happens when the wanted
    /// icon differs from what was applied, and a cancelled prompt is not repeated until settings change.
    private func syncBootDisk(context: Context) {
        guard let boot = system.bootDisk else { return }
        let existing = journal[Self.bootDiskKey]
        let icon = diskIcon(for: .bootDisk, at: nil, context: context)
        let wanted = icon == nil ? "off" : context.theme.id
        if icon == nil, existing == nil { return }
        if let existing, icon != nil, existing.themeID == context.theme.id, boot.hasCustomIcon() { return }
        // A prompt the user cancelled is not shown again until they pick another theme or turn the setting back on.
        guard context.settings.declinedBootDiskChange != wanted else { return }

        guard let icon else {
            if let existing, restore(existing) == .pending { record { $0.declinedBootDiskChange = wanted } }
            return
        }
        var entry = existing ?? JournalEntry(path: Self.bootDiskKey, category: .folder, themeID: context.theme.id, place: .bootDisk)
        if existing == nil, boot.hasCustomIcon() {
            guard context.settings.overrideCustomIcons else { return }
            let name = UUID().uuidString + ".icns"
            guard boot.backUpIcon(to: paths.backups.appendingPathComponent(name)) else { return }
            entry.backup = name
        }
        entry.themeID = context.theme.id
        entry.date = Date()
        journal.record(entry)
        guard boot.setIcon(icon, restoring: nil) else {
            if let existing { journal.record(existing) } else { undoBookkeeping(entry) }
            record { $0.declinedBootDiskChange = wanted }
            return
        }
    }

    /// The finished icon: the theme's artwork drawn on a plain folder in `color`.
    private func finishedIcon(for category: FolderCategory, color: FolderColor, theme: Theme) -> URL? {
        guard let artwork = theme.iconURL(for: category) else { return nil }
        let destination = paths.cache.appendingPathComponent("\(theme.id)/\(color.rawValue)/\(artwork.lastPathComponent)")
        return IconComposer.compose(base: theme.baseFolderURL(for: color), artwork: artwork, to: destination)
    }

    // MARK: restoring

    private func undoBookkeeping(_ entry: JournalEntry) {
        let folder = URL(fileURLWithPath: entry.path, isDirectory: true)
        if entry.gitExclude { GitExclude.remove(from: folder) }
        if let backup = entry.backup { try? FileManager.default.removeItem(at: paths.backups.appendingPathComponent(backup)) }
        journal.remove(entry.path)
    }

    private enum RestoreOutcome { case restored, missing, pending }

    /// Puts one folder or disk back exactly as HyperIcon found it.
    @discardableResult
    private func restore(_ entry: JournalEntry) -> RestoreOutcome {
        if entry.place == .bootDisk {
            guard let boot = system.bootDisk,
                  boot.setIcon(nil, restoring: entry.backup.map { paths.backups.appendingPathComponent($0) }) else { return .pending }
            undoBookkeeping(entry)
            return .restored
        }
        let folder: URL
        if let uuid = entry.volumeUUID {
            let kinds: Set<Place> = entry.place.map { Set([$0]) } ?? [.externalDisk, .networkDisk]
            guard let volume = system.volumes?.mounted(kinds: kinds).first(where: { $0.uuid == uuid }) else {
                // Unplugged. Keep the entry so the disk is put back the next time it is connected.
                if entry.pendingRestore != true {
                    var pending = entry
                    pending.pendingRestore = true
                    journal.record(pending)
                }
                return .pending
            }
            folder = volume.url
        } else {
            folder = URL(fileURLWithPath: entry.path, isDirectory: true)
        }
        var isDir: ObjCBool = false
        let exists = FileManager.default.fileExists(atPath: folder.path, isDirectory: &isDir) && isDir.boolValue
        if exists {
            setter.setIcon(nil, for: folder)
            Xattr.remove(appliedAttribute, from: folder)
            if let backup = entry.backup {
                setter.setIcon(paths.backups.appendingPathComponent(backup), for: folder)
            }
        }
        undoBookkeeping(entry)
        return exists ? .restored : .missing
    }

    /// Removes every icon HyperIcon applied and pauses theming. Returns immediately.
    public func restoreAll(deep: Bool = false, completion: ((RestoreReport) -> Void)? = nil) {
        // Bump the generation first so a scan in progress stops at its next folder.
        update { $0.paused = true }
        queue.async { completion?(self.restoreAllNow(deep: deep)) }
    }

    /// Synchronous variant of `restoreAll`. With `deep`, also sweeps the home folder for themed folders the
    /// journal does not know about (for example after the journal was deleted).
    @discardableResult
    public func restoreAllNow(deep: Bool = false) -> RestoreReport {
        update {
            $0.paused = true
            $0.themeID = nil
        }
        setStatus { $0.activity = .restoring }
        // Taken before the journal empties, so the sweep only opens disks HyperIcon themed or may have themed.
        let sweepKinds = Self.enabledDiskKinds(settings).union(journaledDiskKinds)
        var report = RestoreReport()
        for entry in journal.all {
            switch restore(entry) {
            case .restored: report.restored += 1
            case .missing: report.missing += 1
            case .pending: report.pending += 1
            }
        }
        if deep { report.restored += sweep(diskKinds: sweepKinds) }
        setStatus { $0.activity = .idle }
        return report
    }

    private func sweep(diskKinds: Set<Place>) -> Int {
        var count = 0
        // Places outside the walk below: the home folder itself, /Applications and mounted disks.
        var roots = [home]
        if let applications = system.applications { roots.append(applications) }
        if !diskKinds.isEmpty { roots += system.volumes?.mounted(kinds: diskKinds).map(\.url) ?? [] }
        for url in roots where Xattr.has(appliedAttribute, on: url) {
            setter.setIcon(nil, for: url)
            Xattr.remove(appliedAttribute, from: url)
            count += 1
        }
        let keys: [URLResourceKey] = [.isDirectoryKey]
        guard let walker = FileManager.default.enumerator(at: home, includingPropertiesForKeys: keys, options: [.skipsPackageDescendants]) else {
            return 0
        }
        for case let url as URL in walker {
            let name = url.lastPathComponent
            if name == "Library" && url.deletingLastPathComponent().path == home.path || name == ".git" || name == "node_modules" {
                walker.skipDescendants()
                continue
            }
            guard (try? url.resourceValues(forKeys: Set(keys)))?.isDirectory == true, Xattr.has(appliedAttribute, on: url) else { continue }
            setter.setIcon(nil, for: url)
            Xattr.remove(appliedAttribute, from: url)
            GitExclude.remove(from: url)
            count += 1
        }
        return count
    }
}
