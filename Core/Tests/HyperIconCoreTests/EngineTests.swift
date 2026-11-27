import XCTest
@testable import HyperIconCore

final class EngineTests: TempDirTestCase {
    private var home: URL!
    private var setter: FakeIconSetter!

    private func makeEngine(iconSetter: IconSetter? = nil, system: SystemPlaces = .none) -> Engine {
        let engine = Engine(paths: AppPaths(base: root.appendingPathComponent("support", isDirectory: true)),
                            themeStore: ThemeStore(directories: [Self.bundledThemes]),
                            setter: iconSetter ?? setter, home: home, system: system)
        home = engine.home
        return engine
    }

    override func setUpWithError() throws {
        try super.setUpWithError()
        home = root.appendingPathComponent("home", isDirectory: true)
        setter = FakeIconSetter()
        make([
            "Projects/api/.git/HEAD", "Projects/api/go.mod", "Projects/api/LICENSE", "Projects/api/internal/x.go",
            "Projects/notes/.git/HEAD", "Projects/notes/todo.md", "Projects/notes/Makefile",
            "Documents/Reports/a.pdf", "Documents/Reports/b.pdf",
            "Music/Album/1.mp3", "Music/Album/2.mp3",
            "Desktop/shots/a.png", "Desktop/shots/b.png", "Desktop/shots/c.txt",
            "Library/Preferences/a.plist",
        ], in: home)
    }

    private func folder(_ path: String) -> URL { home.appendingPathComponent(path, isDirectory: true) }

    private func iconFiles() -> [String] {
        let walker = FileManager.default.enumerator(at: home, includingPropertiesForKeys: nil)
        return (walker?.allObjects as? [URL] ?? []).filter { $0.lastPathComponent == iconFileName }.map(\.path)
    }

    func testBundledThemesAreComplete() {
        let themes = ThemeStore(directories: [Self.bundledThemes]).load()
        XCTAssertGreaterThanOrEqual(themes.count, 13)
        for color in FolderColor.allCases {
            XCTAssertEqual(themes.first?.baseFolderURL(for: color)?.lastPathComponent, "\(color.rawValue).png")
        }
        for theme in themes {
            for category in FolderCategory.allCases {
                XCTAssertEqual(theme.iconURL(for: category)?.lastPathComponent, "\(category.rawValue).png", "\(theme.id) is missing \(category)")
            }
            for place in Place.allCases {
                XCTAssertEqual(theme.placeIconURL(for: place)?.lastPathComponent, "\(place.rawValue).png", "\(theme.id) is missing \(place)")
            }
        }
    }

    func testNothingHappensUntilAThemeIsChosen() {
        let engine = makeEngine()
        engine.applyAllNow()
        XCTAssertEqual(iconFiles(), [])
        XCTAssertEqual(engine.journal.count, 0)
    }

    func testApplyThenRestoreLeavesNoTrace() throws {
        let engine = makeEngine()
        engine.update { $0.themeID = "scifi-hud" }
        engine.applyAllNow()

        XCTAssertEqual(setter.iconName(folder("Projects/api")), "go")
        XCTAssertEqual(setter.iconName(folder("Projects/notes")), "git")
        XCTAssertEqual(setter.iconName(folder("Projects")), "folder")
        XCTAssertEqual(setter.iconName(folder("Documents")), "documents")
        XCTAssertEqual(setter.iconName(folder("Documents/Reports")), "pdf")
        XCTAssertEqual(setter.iconName(folder("Music/Album")), "music")
        XCTAssertEqual(setter.iconName(folder("Desktop/shots")), "images")
        XCTAssertNil(setter.iconName(folder("Projects/api/internal")), "the inside of a repository is left alone")
        XCTAssertNil(setter.iconName(folder("Library")))
        XCTAssertEqual(setter.iconName(home), "home", "the home folder gets the theme's own artwork")
        XCTAssertEqual(engine.journal.count, 10)
        XCTAssertTrue(Xattr.has(appliedAttribute, on: folder("Projects/api")))

        let exclude = folder("Projects/api/.git/info/exclude")
        XCTAssertTrue(try String(contentsOf: exclude, encoding: .utf8).contains(GitExclude.pattern))

        // A second pass changes nothing.
        let before = engine.journal.all
        engine.applyAllNow()
        XCTAssertEqual(engine.journal.all, before)

        let report = engine.restoreAllNow()
        XCTAssertEqual(report.restored, 10)
        XCTAssertEqual(iconFiles(), [])
        XCTAssertEqual(engine.journal.count, 0)
        XCTAssertFalse(Xattr.has(appliedAttribute, on: folder("Projects/api")))
        XCTAssertFalse(try String(contentsOf: exclude, encoding: .utf8).contains("Icon"))
        XCTAssertNil(engine.settings.themeID)

        // Restoring pauses theming until the user picks a theme again.
        engine.applyAllNow()
        XCTAssertEqual(iconFiles(), [])
    }

    func testSwitchingThemeReplacesIcons() throws {
        let engine = makeEngine()
        engine.update { $0.themeID = "halloween" }
        engine.applyAllNow()
        engine.update { $0.themeID = "aqua-gloss" }
        engine.applyAllNow()
        let icon = try String(contentsOf: folder("Music/Album").appendingPathComponent(iconFileName), encoding: .utf8)
        XCTAssertTrue(icon.contains("aqua-gloss/blue/music.png"), icon)
        XCTAssertEqual(Set(engine.journal.all.map(\.themeID)), ["aqua-gloss"])
    }

    func testUserIconsAreKeptUnlessOverrideIsOnAndComeBackOnRestore() throws {
        let custom = folder("Music/Album").appendingPathComponent(iconFileName)
        try Data("mine".utf8).write(to: custom)

        let engine = makeEngine()
        engine.update { $0.themeID = "harvest" }
        engine.applyAllNow()
        XCTAssertEqual(try String(contentsOf: custom, encoding: .utf8), "mine")
        XCTAssertNil(engine.journal[folder("Music/Album").path])

        engine.update { $0.overrideCustomIcons = true }
        engine.applyAllNow()
        XCTAssertEqual(setter.iconName(folder("Music/Album")), "music")
        XCTAssertNotNil(engine.journal[folder("Music/Album").path]?.backup)

        engine.restoreAllNow()
        XCTAssertTrue(FileManager.default.fileExists(atPath: custom.path), "the user's own icon is put back")
        XCTAssertEqual(iconFiles(), [custom.path])
    }

    func testFoldersThatLeaveScopeAreRestoredAndDeepRestoreFindsOrphans() {
        var engine = makeEngine()
        engine.update { $0.themeID = "neon-arcade" }
        engine.applyAllNow()
        engine.update { $0.excludedPaths = [self.folder("Desktop").path] }
        engine.applyAllNow()
        XCTAssertNil(setter.iconName(folder("Desktop/shots")))
        XCTAssertNotNil(setter.iconName(folder("Music")))

        // Lose the journal, then make sure a deep restore still cleans up.
        try? FileManager.default.removeItem(at: engine.paths.journal)
        engine = makeEngine()
        XCTAssertEqual(engine.journal.count, 0)
        let report = engine.restoreAllNow(deep: true)
        XCTAssertGreaterThan(report.restored, 0)
        XCTAssertEqual(iconFiles(), [])
    }

    func testWatcherChangesReclassifyFolders() {
        let engine = makeEngine()
        engine.update { $0.themeID = "valentine" }
        engine.applyAllNow()
        XCTAssertEqual(setter.iconName(folder("Projects")), "folder")

        make(["Projects/site/package.json", "Desktop/shots/d.mp4", "Desktop/shots/e.mp4", "Desktop/shots/f.mp4", "Desktop/shots/g.mp4"], in: home)
        let done = expectation(description: "status update")
        engine.onStatus = { _ in done.fulfill() }
        done.assertForOverFulfill = false
        engine.handleChanges(in: [folder("Projects").path, folder("Desktop/shots").path])
        wait(for: [done], timeout: 10)
        XCTAssertEqual(setter.iconName(folder("Projects/site")), "node")
        XCTAssertEqual(setter.iconName(folder("Desktop/shots")), "video")
    }

    private func iconPath(_ folder: URL) -> String {
        (try? String(contentsOf: folder.appendingPathComponent(iconFileName), encoding: .utf8)) ?? ""
    }

    private func tag(_ folder: URL, label: Int) throws {
        var url = folder
        var values = URLResourceValues()
        values.labelNumber = label
        try url.setResourceValues(values)
    }

    func testFoldersAreDrawnInTheirTagColour() throws {
        try tag(folder("Music/Album"), label: 3)      // purple
        let engine = makeEngine()
        engine.update { $0.themeID = "halloween" }
        engine.applyAllNow()

        let purple = iconPath(folder("Music/Album"))
        XCTAssertTrue(purple.contains("/halloween/purple/music.png"), purple)
        XCTAssertTrue(iconPath(folder("Projects/api")).contains("/halloween/blue/go.png"), "untagged folders are blue")
        XCTAssertTrue(FileManager.default.fileExists(atPath: purple), "the finished icon is written to the cache")
        XCTAssertEqual(engine.journal[folder("Music/Album").path]?.color, .purple)

        // Re-tagging the folder is picked up by the watcher path.
        try tag(folder("Music/Album"), label: 6)      // red
        let done = expectation(description: "status update")
        done.assertForOverFulfill = false
        engine.onStatus = { _ in done.fulfill() }
        engine.handleChanges(in: [folder("Music/Album").path])
        wait(for: [done], timeout: 10)
        XCTAssertTrue(iconPath(folder("Music/Album")).contains("/halloween/red/music.png"))

        // With tag colours turned off, everything is blue.
        engine.update { $0.matchTagColor = false }
        engine.applyAllNow()
        XCTAssertTrue(iconPath(folder("Music/Album")).contains("/halloween/blue/music.png"))

        // Restoring removes the icon but leaves the user's tag alone.
        engine.restoreAllNow()
        XCTAssertEqual(iconFiles(), [])
        XCTAssertEqual(FolderColor.of(folder("Music/Album")), .red)
    }

    func testLabelNumbersMapToColours() {
        XCTAssertEqual(FolderColor(labelNumber: 0), .blue)
        XCTAssertEqual(FolderColor(labelNumber: 1), .gray)
        XCTAssertEqual(FolderColor(labelNumber: 2), .green)
        XCTAssertEqual(FolderColor(labelNumber: 3), .purple)
        XCTAssertEqual(FolderColor(labelNumber: 4), .blue)
        XCTAssertEqual(FolderColor(labelNumber: 5), .yellow)
        XCTAssertEqual(FolderColor(labelNumber: 6), .red)
        XCTAssertEqual(FolderColor(labelNumber: 7), .orange)
    }

    // MARK: places

    func testFavoritesAndHomeGetTheirOwnArtwork() {
        let engine = makeEngine()
        engine.update { $0.themeID = "halloween" }
        engine.applyAllNow()

        XCTAssertTrue(iconPath(folder("Documents")).hasSuffix("/halloween/places/documents.png"), iconPath(folder("Documents")))
        XCTAssertTrue(iconPath(folder("Desktop")).hasSuffix("/halloween/places/desktop.png"))
        XCTAssertTrue(iconPath(home).hasSuffix("/halloween/places/home.png"))
        XCTAssertEqual(engine.journal[folder("Music").path]?.place, .music)
        XCTAssertNil(engine.journal[folder("Music").path]?.color, "place artwork is not tag-coloured")
        XCTAssertTrue(iconPath(folder("Documents/Reports")).contains("/halloween/blue/pdf.png"), "folders inside favorites keep content icons")

        // Turned off, favorites go back to content icons and the home folder is restored.
        engine.update {
            $0.themeFavorites = false
            $0.themeHome = false
        }
        engine.applyAllNow()
        XCTAssertTrue(iconPath(folder("Documents")).contains("/halloween/blue/documents.png"))
        XCTAssertNil(engine.journal[folder("Documents").path]?.place)
        XCTAssertNil(setter.iconName(home))
        XCTAssertNil(engine.journal[home.path])
    }

    func testThemesWithoutPlacesLeavePlacesAlone() throws {
        let custom = root.appendingPathComponent("custom/plain", isDirectory: true)
        try FileManager.default.createDirectory(at: custom, withIntermediateDirectories: true)
        try FileManager.default.copyItem(at: Self.bundledThemes.appendingPathComponent("aqua-gloss/folder.png"),
                                         to: custom.appendingPathComponent("folder.png"))
        try Data(#"{"id": "plain", "name": "Plain"}"#.utf8).write(to: custom.appendingPathComponent("theme.json"))
        let engine = Engine(paths: AppPaths(base: root.appendingPathComponent("support", isDirectory: true)),
                            themeStore: ThemeStore(directories: [Self.bundledThemes, custom.deletingLastPathComponent()]),
                            setter: setter, home: home)
        engine.update { $0.themeID = "plain" }
        engine.applyAllNow()
        XCTAssertNil(setter.iconName(home))
        XCTAssertEqual(setter.iconName(folder("Documents")), "folder", "falls back to the theme's folder artwork")
    }

    func testApplicationsFolderIsThemedAndRestored() {
        let applications = root.appendingPathComponent("Applications", isDirectory: true)
        make(["Applications/Editor.app/Contents/Info.plist"], in: root)
        let engine = makeEngine(system: SystemPlaces(applications: applications))
        engine.update { $0.themeID = "aqua-gloss" }
        engine.applyAllNow()
        XCTAssertTrue(iconPath(applications).hasSuffix("/aqua-gloss/places/applications.png"))
        XCTAssertNil(setter.iconName(applications.appendingPathComponent("Editor.app")), "apps inside are left alone")

        engine.restoreAllNow()
        XCTAssertNil(setter.iconName(applications))
        XCTAssertEqual(engine.journal.count, 0)
    }

    func testDisksAreThemedAndRestoredEvenAfterBeingUnplugged() {
        make(["Volumes/USB/", "Volumes/Share/"], in: root)
        let usb = MountedVolume(url: root.appendingPathComponent("Volumes/USB", isDirectory: true), uuid: "U1", place: .externalDisk)
        let share = MountedVolume(url: root.appendingPathComponent("Volumes/Share", isDirectory: true), uuid: "N1", place: .networkDisk)
        let volumes = FakeVolumes()
        volumes.volumes = [usb, share]
        let engine = makeEngine(system: SystemPlaces(volumes: volumes))
        engine.update { $0.themeID = "synthwave-84" }
        engine.applyAllNow()

        XCTAssertTrue(iconPath(usb.url).hasSuffix("/synthwave-84/places/external-disk.png"))
        XCTAssertNil(setter.iconName(share.url), "network shares are off by default")
        XCTAssertEqual(engine.journal["volume:U1"]?.mountPath, usb.url.path)

        engine.update { $0.themeNetworkDisks = true }
        engine.applyAllNow()
        XCTAssertTrue(iconPath(share.url).hasSuffix("/synthwave-84/places/network-disk.png"))

        // Unplugging is not deleting: the entry survives a rescan.
        volumes.volumes = [share]
        engine.applyAllNow()
        XCTAssertNotNil(engine.journal["volume:U1"])

        // Restoring while it is unplugged finishes when it comes back.
        let report = engine.restoreAllNow()
        XCTAssertEqual(report.pending, 1)
        XCTAssertNil(setter.iconName(share.url))
        XCTAssertEqual(engine.journal["volume:U1"]?.pendingRestore, true)
        XCTAssertNotNil(setter.iconName(usb.url))

        volumes.volumes = [usb, share]
        engine.applyAllNow()
        XCTAssertNil(setter.iconName(usb.url))
        XCTAssertEqual(engine.journal.count, 0)
    }

    func testDisksAreNotLookedAtUnlessThemed() {
        make(["Volumes/USB/", "Volumes/Share/"], in: root)
        let volumes = FakeVolumes()
        volumes.volumes = [
            MountedVolume(url: root.appendingPathComponent("Volumes/USB", isDirectory: true), uuid: "U1", place: .externalDisk),
            MountedVolume(url: root.appendingPathComponent("Volumes/Share", isDirectory: true), uuid: "N1", place: .networkDisk),
        ]
        let engine = makeEngine(system: SystemPlaces(volumes: volumes))
        engine.update {
            $0.themeID = "harvest"
            $0.themeExternalDisks = false
        }
        engine.applyAllNow()
        engine.restoreAllNow(deep: true)
        engine.applyAllNow()
        XCTAssertEqual(volumes.requests, [], "no disk kinds are themed, so no disk is opened")

        engine.update {
            $0.themeID = "harvest"
            $0.paused = false
            $0.themeExternalDisks = true
        }
        engine.applyAllNow()
        XCTAssertFalse(volumes.requests.isEmpty)
        XCTAssertTrue(volumes.requests.allSatisfy { !$0.contains(.networkDisk) }, "network shares are off, so they are never opened")
    }

    func testAFailingDiskIsNotRetriedOnEveryScan() {
        make(["Volumes/Share/"], in: root)
        let share = MountedVolume(url: root.appendingPathComponent("Volumes/Share", isDirectory: true), uuid: "N1", place: .networkDisk)
        let volumes = FakeVolumes()
        volumes.volumes = [share]
        setter.failing = [share.url]
        let engine = makeEngine(system: SystemPlaces(volumes: volumes))
        engine.update {
            $0.themeID = "harvest"
            $0.themeNetworkDisks = true
        }
        engine.applyAllNow()
        engine.applyAllNow()
        engine.applyAllNow()
        XCTAssertEqual(setter.setCounts[share.url], 1)
        XCTAssertNil(engine.journal["volume:N1"])

        // A settings change gives it another try.
        engine.update { $0.maxDepth = 3 }
        engine.applyAllNow()
        XCTAssertEqual(setter.setCounts[share.url], 2)
    }

    func testBootDiskOnlyChangesWhenAskedAndDoesNotRepeatACancelledPrompt() {
        let boot = FakeBootDisk()
        var engine = makeEngine(system: SystemPlaces(bootDisk: boot))
        engine.update { $0.themeID = "harvest" }
        engine.applyAllNow()
        XCTAssertEqual(boot.calls, [], "off by default")

        engine.update { $0.themeBootDisk = true }
        engine.applyAllNow()
        XCTAssertEqual(boot.calls.count, 1)
        XCTAssertTrue(boot.calls[0]?.path.hasSuffix("/harvest/places/boot-disk.png") == true)
        engine.applyAllNow()
        XCTAssertEqual(boot.calls.count, 1, "no new prompt when nothing changed")

        // A cancelled prompt for a new theme is not repeated on rescans, unrelated settings changes or relaunches.
        boot.succeeds = false
        engine.update { $0.themeID = "valentine" }
        engine.applyAllNow()
        engine.applyAllNow()
        engine.update { $0.maxDepth = 3 }
        engine.applyAllNow()
        engine = makeEngine(system: SystemPlaces(bootDisk: boot))
        engine.applyAllNow()
        XCTAssertEqual(boot.calls.count, 2)
        XCTAssertEqual(engine.journal["volume:boot"]?.themeID, "harvest")
        XCTAssertEqual(engine.settings.declinedBootDiskChange, "valentine")

        // Choosing again (the app clears the marker when a theme is picked) asks again.
        boot.succeeds = true
        engine.update {
            $0.themeID = "valentine"
            $0.declinedBootDiskChange = nil
        }
        engine.applyAllNow()
        XCTAssertEqual(boot.calls.count, 3)
        XCTAssertEqual(engine.journal["volume:boot"]?.themeID, "valentine")

        let report = engine.restoreAllNow()
        XCTAssertEqual(report.pending, 0)
        XCTAssertNil(boot.calls.last!)
        XCTAssertNil(engine.journal["volume:boot"])
    }

    func testOlderJournalAndSettingsStillLoad() throws {
        let support = root.appendingPathComponent("support", isDirectory: true)
        try FileManager.default.createDirectory(at: support, withIntermediateDirectories: true)
        let line = #"{"set":{"path":"/tmp/x","category":"git","themeID":"halloween","gitExclude":false,"color":"red","date":0}}"#
        try Data((line + "\n").utf8).write(to: support.appendingPathComponent("journal.jsonl"))
        try Data(#"{"themeID":"halloween","paused":false}"#.utf8).write(to: support.appendingPathComponent("settings.json"))
        let engine = makeEngine()
        XCTAssertEqual(engine.journal["/tmp/x"]?.category, .git)
        XCTAssertNil(engine.journal["/tmp/x"]?.place)
        XCTAssertTrue(engine.settings.themeFavorites)
        XCTAssertFalse(engine.settings.themeBootDisk)
    }

    /// Exercises the real Finder icon API. Skipped where the machine cannot set icons (some headless CI hosts).
    func testRealFinderIconRoundTrip() throws {
        let engine = makeEngine(iconSetter: WorkspaceIconSetter())
        engine.update { $0.themeID = "synthwave-84" }
        engine.applyAllNow()
        let icon = folder("Projects/api").appendingPathComponent(iconFileName)
        try XCTSkipUnless(FileManager.default.fileExists(atPath: icon.path), "NSWorkspace could not set icons on this host")
        XCTAssertGreaterThan(engine.journal.count, 0)
        engine.restoreAllNow()
        XCTAssertEqual(iconFiles(), [])
        XCTAssertEqual(engine.journal.count, 0)
    }
}
