import AppKit
import HyperIconCore
import ServiceManagement
import SwiftUI

struct ThemeGroup: Identifiable {
    let id: String
    let themes: [Theme]
}

@MainActor
final class AppModel: ObservableObject {
    nonisolated static var bundledThemes: URL {
        (Bundle.main.resourceURL ?? Bundle.main.bundleURL).appendingPathComponent("Themes", isDirectory: true)
    }

    @Published private(set) var themes: [Theme] = []
    @Published private(set) var preferences: Preferences
    @Published private(set) var status: EngineStatus
    @Published var launchAtLogin: Bool {
        didSet { setLaunchAtLogin(launchAtLogin) }
    }

    private let engine: Engine
    private var watcher: FolderWatcher?
    private var volumeObservers: [NSObjectProtocol] = []

    init() {
        let paths = AppPaths()
        let engine = Engine(paths: paths, themeStore: ThemeStore(directories: [Self.bundledThemes, paths.userThemes]), system: .live)
        self.engine = engine
        preferences = engine.settings
        status = engine.status
        launchAtLogin = SMAppService.mainApp.status == .enabled

        themes = engine.themes
        engine.onStatus = { [weak self] status in
            Task { @MainActor in self?.status = status }
        }
        let watcher = FolderWatcher(path: engine.home.path) { [weak engine] paths in
            engine?.handleChanges(in: paths)
        }
        self.watcher = watcher
        watcher.start()
        // Theme disks as they are plugged in, and finish restoring ones that were unplugged during a restore.
        let center = NSWorkspace.shared.notificationCenter
        for name in [NSWorkspace.didMountNotification, NSWorkspace.didRenameVolumeNotification] {
            volumeObservers.append(center.addObserver(forName: name, object: nil, queue: nil) { [weak engine] _ in
                engine?.handleVolumesChanged()
            })
        }
        engine.applyAll()
    }

    var groupedThemes: [ThemeGroup] {
        var order: [String] = []
        var groups: [String: [Theme]] = [:]
        for theme in themes {
            if groups[theme.group] == nil { order.append(theme.group) }
            groups[theme.group, default: []].append(theme)
        }
        return order.map { ThemeGroup(id: $0, themes: groups[$0] ?? []) }
    }

    var activeTheme: Theme? { themes.first { $0.id == preferences.themeID } }

    var statusLine: String {
        switch status.activity {
        case .scanning: return "Applying icons… \(status.themedFolders) folders so far"
        case .restoring: return "Restoring original icons…"
        case .idle:
            if preferences.themeID == nil { return "Pick a theme to get started" }
            if preferences.paused { return "Paused · \(status.themedFolders) folders themed" }
            return "\(status.themedFolders) folders themed"
        }
    }

    // MARK: actions

    private func change(rescan: Bool = true, _ body: (inout Preferences) -> Void) {
        engine.update(body)
        preferences = engine.settings
        if rescan { engine.applyAll() }
    }

    func select(_ theme: Theme) {
        change {
            $0.themeID = theme.id
            $0.paused = false
            // Picking a theme is a deliberate choice, so a startup-disk prompt cancelled earlier may be shown again.
            $0.declinedBootDiskChange = nil
        }
    }

    func setPaused(_ paused: Bool) { change { $0.paused = paused } }
    func setMaxDepth(_ depth: Int) { change { $0.maxDepth = min(8, max(1, depth)) } }
    func setOverrideCustomIcons(_ value: Bool) { change { $0.overrideCustomIcons = value } }
    func setPreferGit(_ value: Bool) { change { $0.preferGit = value } }
    func setMatchTagColor(_ value: Bool) { change { $0.matchTagColor = value } }
    /// Changes one of the "Disks & favorites" settings and rescans.
    func setPlaceOption(_ option: WritableKeyPath<Preferences, Bool>, _ value: Bool) {
        change {
            $0[keyPath: option] = value
            if option == \.themeBootDisk { $0.declinedBootDiskChange = nil }
        }
    }

    func addExcludedFolder() {
        let panel = NSOpenPanel()
        panel.canChooseFiles = false
        panel.canChooseDirectories = true
        panel.allowsMultipleSelection = true
        panel.prompt = "Exclude"
        NSApp.activate(ignoringOtherApps: true)
        guard panel.runModal() == .OK else { return }
        let added = panel.urls.map(\.path)
        change { $0.excludedPaths = Array(Set($0.excludedPaths + added)).sorted() }
    }

    func removeExcludedFolder(_ path: String) {
        change { $0.excludedPaths.removeAll { $0 == path } }
    }

    func rescan() {
        themes = engine.themes
        engine.applyAll()
    }

    func openThemesFolder() {
        NSWorkspace.shared.open(engine.paths.userThemes)
    }

    func restoreOriginalIcons() {
        let alert = NSAlert()
        alert.messageText = "Restore original icons?"
        alert.informativeText = "HyperIcon will remove every icon it applied to folders, favorites, your home folder and disks, "
            + "and put back any custom icons you had before. "
            + "Theming stays off until you pick a theme again."
        alert.addButton(withTitle: "Restore")
        alert.addButton(withTitle: "Cancel")
        NSApp.activate(ignoringOtherApps: true)
        guard alert.runModal() == .alertFirstButtonReturn else { return }
        engine.restoreAll(deep: true) { [weak self] report in
            Task { @MainActor in
                guard let self else { return }
                self.preferences = self.engine.settings
                let done = NSAlert()
                done.messageText = "Original icons restored"
                var text = "\(report.restored) folders and disks were returned to how HyperIcon found them."
                if report.pending > 0 {
                    text += " \(report.pending) disks are not connected right now (or the password prompt was cancelled). "
                        + "HyperIcon will put them back the next time it sees them."
                }
                done.informativeText = text
                NSApp.activate(ignoringOtherApps: true)
                done.runModal()
            }
        }
        preferences = engine.settings
    }

    private func setLaunchAtLogin(_ enabled: Bool) {
        let service = SMAppService.mainApp
        do {
            if enabled, service.status != .enabled {
                try service.register()
            } else if !enabled, service.status == .enabled {
                try service.unregister()
            }
        } catch {
            NSLog("HyperIcon: could not change the login item: \(error.localizedDescription)")
        }
    }
}
