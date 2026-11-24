import Foundation
import XCTest
@testable import HyperIconCore

/// Stands in for Finder: a custom icon is represented by an `Icon\r` file holding the image path.
final class FakeIconSetter: IconSetter {
    @discardableResult
    func setIcon(_ imageURL: URL?, for folder: URL) -> Bool {
        let file = folder.appendingPathComponent(iconFileName)
        try? FileManager.default.removeItem(at: file)
        guard let imageURL else { return true }
        return (try? Data(imageURL.path.utf8).write(to: file)) != nil
    }

    func hasCustomIcon(_ folder: URL) -> Bool {
        FileManager.default.fileExists(atPath: folder.appendingPathComponent(iconFileName).path)
    }

    func backUpIcon(of folder: URL, to destination: URL) -> Bool {
        (try? FileManager.default.copyItem(at: folder.appendingPathComponent(iconFileName), to: destination)) != nil
    }

    func iconName(_ folder: URL) -> String? {
        guard let data = try? Data(contentsOf: folder.appendingPathComponent(iconFileName)) else { return nil }
        return URL(fileURLWithPath: String(decoding: data, as: UTF8.self)).deletingPathExtension().lastPathComponent
    }
}

class TempDirTestCase: XCTestCase {
    var root: URL!

    override func setUpWithError() throws {
        root = FileManager.default.temporaryDirectory.appendingPathComponent("hypericon-" + UUID().uuidString, isDirectory: true)
        try FileManager.default.createDirectory(at: root, withIntermediateDirectories: true)
        root = root.canonicalFolder
    }

    override func tearDownWithError() throws {
        try? FileManager.default.removeItem(at: root)
    }

    /// Creates files (and their parent folders) relative to `base`. A trailing slash creates a folder.
    func make(_ items: [String], in base: URL) {
        let fm = FileManager.default
        for item in items {
            let url = base.appendingPathComponent(item)
            if item.hasSuffix("/") {
                try? fm.createDirectory(at: url, withIntermediateDirectories: true)
            } else {
                try? fm.createDirectory(at: url.deletingLastPathComponent(), withIntermediateDirectories: true)
                fm.createFile(atPath: url.path, contents: Data("x".utf8))
            }
        }
    }

    static var bundledThemes: URL {
        URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent()
            .deletingLastPathComponent().deletingLastPathComponent().appendingPathComponent("Themes", isDirectory: true)
    }
}

/// Stands in for mounted disks: whatever is in `volumes` is "plugged in".
final class FakeVolumes: VolumeListing {
    var volumes: [MountedVolume] = []
    func mounted() -> [MountedVolume] { volumes }
}

/// Stands in for the startup disk. Records each change instead of asking for a password.
final class FakeBootDisk: BootDiskIconSetting {
    /// Icons set, in order; nil means removed.
    var calls: [URL?] = []
    /// Set to false to act as if the user cancelled the password prompt.
    var succeeds = true
    var current: URL?

    func setIcon(_ imageURL: URL?, restoring backup: URL?) -> Bool {
        calls.append(imageURL)
        guard succeeds else { return false }
        current = imageURL ?? backup
        return true
    }

    func hasCustomIcon() -> Bool { current != nil }

    func backUpIcon(to destination: URL) -> Bool { current != nil }
}
