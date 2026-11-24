import Foundation
import ImageIO
import UniformTypeIdentifiers

/// Sets the icon of the startup disk ("Macintosh HD").
///
/// The system volume is sealed and read-only, so the icon goes on the writable Data volume that Finder
/// shows as the startup disk: an `.icns` at its root plus the custom-icon bit in its Finder info. Both are
/// root-owned, so each change runs one shell step with administrator privileges, which shows the standard
/// password prompt. HyperIcon only does this when the user turns the setting on, picks a new theme, or restores.
public final class BootVolumeIcon: BootDiskIconSetting {
    let root: URL
    private var iconFile: URL { root.appendingPathComponent(volumeIconFileName) }

    public init(root: URL = URL(fileURLWithPath: "/System/Volumes/Data", isDirectory: true)) {
        self.root = root
    }

    public func hasCustomIcon() -> Bool {
        FileManager.default.fileExists(atPath: iconFile.path)
    }

    public func backUpIcon(to destination: URL) -> Bool {
        (try? FileManager.default.copyItem(at: iconFile, to: destination)) != nil
    }

    public func setIcon(_ imageURL: URL?, restoring backup: URL?) -> Bool {
        let staging = FileManager.default.temporaryDirectory.appendingPathComponent("hypericon-boot-\(UUID().uuidString).icns")
        defer { try? FileManager.default.removeItem(at: staging) }

        var source: URL?
        if let imageURL {
            guard Self.writeICNS(from: imageURL, to: staging) else { return false }
            source = staging
        } else if let backup, FileManager.default.fileExists(atPath: backup.path) {
            source = backup
        }

        var info = Self.finderInfo(of: root)
        let script: String
        if let source {
            info[8] |= 0x04                     // kHasCustomIcon
            script = "/bin/cp \(Self.quote(source.path)) \(Self.quote(iconFile.path)) && "
                + "/usr/sbin/chown root:wheel \(Self.quote(iconFile.path)) && "
                + "/usr/bin/xattr -wx com.apple.FinderInfo \(Self.hex(info)) \(Self.quote(root.path))"
        } else {
            info[8] &= ~0x04
            script = "/bin/rm -f \(Self.quote(iconFile.path)) && "
                + "/usr/bin/xattr -wx com.apple.FinderInfo \(Self.hex(info)) \(Self.quote(root.path))"
        }
        return Self.runAsAdministrator(script)
    }

    // MARK: helpers

    /// Converts a PNG to a multi-resolution `.icns`.
    static func writeICNS(from png: URL, to destination: URL) -> Bool {
        guard let source = CGImageSourceCreateWithURL(png as CFURL, nil),
              let image = CGImageSourceCreateImageAtIndex(source, 0, nil),
              let output = CGImageDestinationCreateWithURL(destination as CFURL, UTType.icns.identifier as CFString, 5, nil),
              let space = CGColorSpace(name: CGColorSpace.sRGB) else { return false }
        for size in [16, 32, 128, 256, 512] {
            guard let context = CGContext(data: nil, width: size, height: size, bitsPerComponent: 8, bytesPerRow: 0, space: space,
                                          bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue) else { return false }
            context.interpolationQuality = .high
            context.draw(image, in: CGRect(x: 0, y: 0, width: size, height: size))
            guard let scaled = context.makeImage() else { return false }
            CGImageDestinationAddImage(output, scaled, nil)
        }
        return CGImageDestinationFinalize(output)
    }

    /// The folder's 32-byte Finder info, or zeros if it has none.
    static func finderInfo(of url: URL) -> [UInt8] {
        var bytes = [UInt8](repeating: 0, count: 32)
        _ = url.withUnsafeFileSystemRepresentation { path in
            getxattr(path, "com.apple.FinderInfo", &bytes, 32, 0, 0)
        }
        return bytes
    }

    static func hex(_ bytes: [UInt8]) -> String {
        bytes.map { String(format: "%02x", $0) }.joined()
    }

    /// Single-quotes a string for the shell.
    static func quote(_ s: String) -> String {
        "'" + s.replacingOccurrences(of: "'", with: "'\\''") + "'"
    }

    /// Runs a shell command through `osascript` with administrator privileges. Returns false if the user
    /// cancels the password prompt or the command fails.
    static func runAsAdministrator(_ command: String) -> Bool {
        let literal = command.replacingOccurrences(of: "\\", with: "\\\\").replacingOccurrences(of: "\"", with: "\\\"")
        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/usr/bin/osascript")
        process.arguments = ["-e", "do shell script \"\(literal)\" with administrator privileges "
            + "with prompt \"HyperIcon wants to change the icon of your startup disk.\""]
        process.standardOutput = FileHandle.nullDevice
        process.standardError = FileHandle.nullDevice
        do {
            try process.run()
        } catch {
            return false
        }
        process.waitUntilExit()
        return process.terminationStatus == 0
    }
}
