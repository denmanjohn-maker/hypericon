import XCTest
@testable import HyperIconCore

/// Runs `BootVolumeIcon` against a temporary folder. The "administrator" step runs the same shell command as
/// the current user (which can do everything in a folder it owns) and counts how often a password would be asked.
final class BootVolumeIconTests: TempDirTestCase {
    private var prompts = 0

    private func makeIcon() -> BootVolumeIcon {
        BootVolumeIcon(root: root, administrator: { [unowned self] command in
            self.prompts += 1
            let process = Process()
            process.executableURL = URL(fileURLWithPath: "/bin/sh")
            process.arguments = ["-c", command]
            guard (try? process.run()) != nil else { return false }
            process.waitUntilExit()
            return process.terminationStatus == 0
        })
    }

    private func artwork(_ theme: String) -> URL {
        Self.bundledThemes.appendingPathComponent("\(theme)/places/boot-disk.png")
    }

    private var iconFile: URL { root.appendingPathComponent(volumeIconFileName) }

    private func hasCustomIconBit() -> Bool {
        BootVolumeIcon.finderInfo(of: root)[8] & 0x04 != 0
    }

    func testOnlyTheFirstChangeAndAPlainRemovalAskForAPassword() throws {
        let boot = makeIcon()
        XCTAssertFalse(boot.hasCustomIcon())

        XCTAssertTrue(boot.setIcon(artwork("harvest"), restoring: nil))
        XCTAssertEqual(prompts, 1)
        XCTAssertTrue(boot.hasCustomIcon())
        XCTAssertTrue(hasCustomIconBit())
        XCTAssertTrue(FileManager.default.isWritableFile(atPath: iconFile.path))
        let first = try Data(contentsOf: iconFile)

        // A new theme rewrites the file in place: no password.
        XCTAssertTrue(boot.setIcon(artwork("valentine"), restoring: nil))
        XCTAssertEqual(prompts, 1)
        XCTAssertNotEqual(try Data(contentsOf: iconFile), first)

        // Putting back an earlier icon is also a rewrite.
        let backup = root.appendingPathComponent("backup.icns")
        try first.write(to: backup)
        XCTAssertTrue(boot.setIcon(nil, restoring: backup))
        XCTAssertEqual(prompts, 1)
        XCTAssertEqual(try Data(contentsOf: iconFile), first)

        // Removing the icon altogether needs the folder itself, so it asks.
        XCTAssertTrue(boot.setIcon(nil, restoring: nil))
        XCTAssertEqual(prompts, 2)
        XCTAssertFalse(boot.hasCustomIcon())
        XCTAssertFalse(hasCustomIconBit())
    }

    func testAnIconFileTheUserCannotWriteFallsBackToOnePrompt() throws {
        let boot = makeIcon()
        XCTAssertTrue(boot.setIcon(artwork("harvest"), restoring: nil))
        // As left by an older HyperIcon, which kept the file owned by root.
        try FileManager.default.setAttributes([.posixPermissions: 0o444], ofItemAtPath: iconFile.path)
        XCTAssertTrue(boot.setIcon(artwork("valentine"), restoring: nil))
        XCTAssertEqual(prompts, 2)
        XCTAssertTrue(FileManager.default.isWritableFile(atPath: iconFile.path), "the prompt hands the file back to the user")
    }
}
