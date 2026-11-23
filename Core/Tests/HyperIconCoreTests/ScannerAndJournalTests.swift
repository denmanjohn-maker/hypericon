import XCTest
@testable import HyperIconCore

final class ScannerAndJournalTests: TempDirTestCase {
    func testWalkSkipsWhatItShould() {
        make([
            "Projects/app/.git/HEAD", "Projects/app/src/main.swift", "Projects/web/node_modules/x/index.js",
            "Documents/Reports/2024/Q1/deep/a.txt", "Library/Caches/a", ".config/tool/a", "Applications/",
            "Tool.app/Contents/Resources/a",
        ], in: root)
        let scanner = FolderScanner(home: root, maxDepth: 3, skipNames: ["node_modules"], excludedPaths: [])
        var visited: [String] = []
        scanner.walk { url in
            visited.append(String(url.path.dropFirst(root.path.count + 1)))
            return true
        }
        XCTAssertEqual(visited.sorted(), ["Documents", "Documents/Reports", "Documents/Reports/2024", "Projects", "Projects/app", "Projects/web"])
        for path in visited {
            XCTAssertTrue(scanner.isEligible(root.appendingPathComponent(path)), path)
        }
        for path in ["Projects/app/src", "Library/Caches", ".config", "Documents/Reports/2024/Q1", "Projects/web/node_modules", "Applications"] {
            XCTAssertFalse(scanner.isEligible(root.appendingPathComponent(path)), path)
        }
        XCTAssertFalse(scanner.isEligible(root))
        XCTAssertFalse(scanner.isEligible(URL(fileURLWithPath: "/usr/lib")))
    }

    func testExcludedPaths() {
        make(["Work/secret/a.txt", "Work/open/a.txt"], in: root)
        let scanner = FolderScanner(home: root, maxDepth: 4, skipNames: [], excludedPaths: [root.appendingPathComponent("Work/secret").path])
        var visited: [String] = []
        scanner.walk { visited.append($0.lastPathComponent); return true }
        XCTAssertEqual(visited.sorted(), ["Work", "open"])
    }

    func testJournalPersistsAndCompacts() {
        let url = root.appendingPathComponent("journal.jsonl")
        var journal = Journal(url: url)
        journal.record(JournalEntry(path: "/a", category: .git, themeID: "one"))
        journal.record(JournalEntry(path: "/b", category: .music, themeID: "one", backup: "x.tiff", gitExclude: true))
        journal.record(JournalEntry(path: "/a", category: .node, themeID: "two"))
        journal.remove("/b")
        journal.remove("/never-added")

        journal = Journal(url: url)
        XCTAssertEqual(journal.count, 1)
        XCTAssertEqual(journal["/a"]?.category, .node)
        XCTAssertEqual(journal["/a"]?.themeID, "two")
        XCTAssertNil(journal["/b"])

        for index in 0..<400 { journal.record(JournalEntry(path: "/a", category: .git, themeID: "t\(index)")) }
        journal = Journal(url: url)
        XCTAssertEqual(journal["/a"]?.themeID, "t399")
        let lines = (try? String(contentsOf: url, encoding: .utf8))?.split(separator: "\n").count
        XCTAssertEqual(lines, 1)
    }
}
