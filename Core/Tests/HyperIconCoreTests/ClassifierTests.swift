import XCTest
@testable import HyperIconCore

final class ClassifierTests: TempDirTestCase {
    private func classify(_ items: [String], preferGit: Bool = false) -> FolderCategory {
        let folder = root.appendingPathComponent(UUID().uuidString, isDirectory: true)
        make(["./"] + items, in: folder)
        return Classifier(preferGit: preferGit).classify(folder)
    }

    func testEmptyFolderIsGeneric() {
        XCTAssertEqual(classify([]), .folder)
    }

    func testGitRepository() {
        XCTAssertEqual(classify([".git/HEAD", "README.md", "notes.txt"]), .git)
    }

    func testLanguageMarkerBeatsGitUnlessPreferred() {
        let items = [".git/HEAD", "package.json", "index.js"]
        XCTAssertEqual(classify(items), .node)
        XCTAssertEqual(classify(items, preferGit: true), .git)
    }

    func testToolingMarkers() {
        XCTAssertEqual(classify(["main.tf", "variables.tf"]), .terraform)
        XCTAssertEqual(classify(["Chart.yaml", "values.yaml"]), .kubernetes)
        XCTAssertEqual(classify(["Dockerfile", "app.conf"]), .docker)
        XCTAssertEqual(classify(["Jenkinsfile"]), .ci)
        XCTAssertEqual(classify(["App.xcodeproj/project.pbxproj"]), .xcode)
        XCTAssertEqual(classify(["Service.sln"]), .dotnet)
        XCTAssertEqual(classify(["go.mod", "Dockerfile"]), .go)
    }

    func testMajorityOfDocuments() {
        XCTAssertEqual(classify(["a.docx", "b.docx", "c.txt", "d.png"]), .documents)
    }

    func testMajorityOfImagesIgnoresHiddenFiles() {
        XCTAssertEqual(classify(["a.jpg", "b.PNG", "c.heic", ".DS_Store", ".hidden.txt"]), .images)
    }

    func testNoMajorityIsGeneric() {
        XCTAssertEqual(classify(["a.docx", "b.png", "c.mp3", "d.zip", "e.unknown"]), .folder)
    }

    func testFolderOfSubfoldersIsJudgedByTheirContents() {
        XCTAssertEqual(classify(["2023/a.mp3", "2023/b.mp3", "2024/c.flac", "2024/cover.jpg"]), .music)
    }

    func testCustomRules() throws {
        var rules = RuleSet.standard
        rules.markers.insert(MarkerRule(.data, ["dataset.yaml"]), at: 0)
        let folder = root.appendingPathComponent("custom", isDirectory: true)
        make(["dataset.yaml", "package.json"], in: folder)
        XCTAssertEqual(Classifier(rules: rules).classify(folder), .data)
        let decoded = try JSONDecoder().decode(RuleSet.self, from: JSONEncoder().encode(rules))
        XCTAssertEqual(decoded, rules)
    }
}
