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
}

/// Applies the active theme to eligible folders and can undo everything it has done.
/// All work happens on one serial queue; public methods are safe to call from any thread.
public final class Engine {
    public let paths: AppPaths
    public let home: URL
    public let journal: Journal
    public var onStatus: ((EngineStatus) -> Void)?

    private let themeStore: ThemeStore
    private let setter: IconSetter
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
                home: URL = FileManager.default.homeDirectoryForCurrentUser) {
        self.paths = paths
        self.home = home.standardizedFileURL
        self.themeStore = themeStore
        self.setter = setter
        paths.ensure()
        journal = Journal(url: paths.journal)
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
        guard let context = makeContext() else { return }
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
        if currentGeneration == started {
            // Folders that were deleted or moved no longer need an entry; folders that fell out of scope get their icon back.
            for entry in journal.all where !seen.contains(entry.path) {
                restore(entry)
            }
        }
        setStatus {
            $0.activity = .idle
            $0.lastScan = Date()
        }
    }

    /// Re-evaluates folders reported by the file-system watcher, plus any new subfolders inside them.
    public func handleChanges(in changedPaths: [String]) {
        queue.async {
            guard let context = self.makeContext() else { return }
            var candidates = Set<String>()
            for path in changedPaths {
                let url = URL(fileURLWithPath: path, isDirectory: true).standardizedFileURL
                candidates.insert(url.path)
                let children = (try? FileManager.default.contentsOfDirectory(at: url, includingPropertiesForKeys: nil, options: [.skipsHiddenFiles])) ?? []
                for child in children.prefix(500) where self.journal[child.path] == nil {
                    candidates.insert(child.standardizedFileURL.path)
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

    /// Returns true if the folder's icon was changed.
    @discardableResult
    private func apply(to folder: URL, context: Context) -> Bool {
        let category = resolveCategory(for: folder, context: context)
        let existing = journal[folder.path]
        let hasIcon = setter.hasCustomIcon(folder)
        if let existing, existing.themeID == context.theme.id, existing.category == category, hasIcon { return false }
        guard let icon = context.theme.iconURL(for: category) else { return false }

        var entry = existing ?? JournalEntry(path: folder.path, category: category, themeID: context.theme.id)
        entry.category = category
        entry.themeID = context.theme.id
        entry.date = Date()

        if existing == nil, hasIcon, !Xattr.has(appliedAttribute, on: folder) {
            // The user gave this folder its own icon.
            guard context.settings.overrideCustomIcons else { return false }
            let name = UUID().uuidString + ".tiff"
            guard setter.backUpIcon(of: folder, to: paths.backups.appendingPathComponent(name)) else { return false }
            entry.backup = name
        }
        if FolderScanner.isGitRepository(folder), !entry.gitExclude {
            entry.gitExclude = GitExclude.add(to: folder)
        }

        journal.record(entry)
        guard setter.setIcon(icon, for: folder) else {
            if existing == nil { undoBookkeeping(entry) }
            return false
        }
        Xattr.set(appliedAttribute, value: "\(context.theme.id)/\(category.rawValue)", on: folder)
        return true
    }

    // MARK: restoring

    private func undoBookkeeping(_ entry: JournalEntry) {
        let folder = URL(fileURLWithPath: entry.path, isDirectory: true)
        if entry.gitExclude { GitExclude.remove(from: folder) }
        if let backup = entry.backup { try? FileManager.default.removeItem(at: paths.backups.appendingPathComponent(backup)) }
        journal.remove(entry.path)
    }

    /// Puts one folder back exactly as HyperIcon found it. Returns false if the folder no longer exists.
    @discardableResult
    private func restore(_ entry: JournalEntry) -> Bool {
        let folder = URL(fileURLWithPath: entry.path, isDirectory: true)
        var isDir: ObjCBool = false
        let exists = FileManager.default.fileExists(atPath: entry.path, isDirectory: &isDir) && isDir.boolValue
        if exists {
            setter.setIcon(nil, for: folder)
            Xattr.remove(appliedAttribute, from: folder)
            if let backup = entry.backup {
                setter.setIcon(paths.backups.appendingPathComponent(backup), for: folder)
            }
        }
        undoBookkeeping(entry)
        return exists
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
        var report = RestoreReport()
        for entry in journal.all {
            if restore(entry) { report.restored += 1 } else { report.missing += 1 }
        }
        if deep { report.restored += sweep() }
        setStatus { $0.activity = .idle }
        return report
    }

    private func sweep() -> Int {
        var count = 0
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
