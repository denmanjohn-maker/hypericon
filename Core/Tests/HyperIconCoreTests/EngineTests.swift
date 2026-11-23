import XCTest
@testable import HyperIconCore

final class EngineTests: TempDirTestCase {
    private var home: URL!
    private var setter: FakeIconSetter!

    private func makeEngine(iconSetter: IconSetter? = nil) -> Engine {
        let engine = Engine(paths: AppPaths(base: root.appendingPathComponent("support", isDirectory: true)),
                            themeStore: ThemeStore(directories: [Self.bundledThemes]),
                            setter: iconSetter ?? setter, home: home)
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
        XCTAssertEqual(engine.journal.count, 9)
        XCTAssertTrue(Xattr.has(appliedAttribute, on: folder("Projects/api")))

        let exclude = folder("Projects/api/.git/info/exclude")
        XCTAssertTrue(try String(contentsOf: exclude, encoding: .utf8).contains(GitExclude.pattern))

        // A second pass changes nothing.
        let before = engine.journal.all
        engine.applyAllNow()
        XCTAssertEqual(engine.journal.all, before)

        let report = engine.restoreAllNow()
        XCTAssertEqual(report.restored, 9)
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
