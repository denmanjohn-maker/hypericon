import AppKit
import Foundation
import ImageIO
import UniformTypeIdentifiers

/// Sets the icon of the startup disk ("Macintosh HD").
///
/// The system volume is sealed and read-only, so the icon goes on the writable Data volume that Finder
/// shows as the startup disk: an `.icns` at its root plus the custom-icon bit in its Finder info. Both live in
/// a root-owned folder, so the first change runs one shell step with administrator privileges, which shows
/// the standard password prompt. That step hands the icon file to the current user, so later theme changes
/// rewrite it in place without asking again. Only removing the icon (restoring with no earlier icon to put
/// back) needs the password a second time.
public final class BootVolumeIcon: BootDiskIconSetting {
    let root: URL
    private let administrator: (String) -> Bool
    private let owner: uid_t
    private var iconFile: URL { root.appendingPathComponent(volumeIconFileName) }

    /// `administrator` runs a shell command as root and returns false if it was cancelled or failed.
    public init(root: URL = URL(fileURLWithPath: "/System/Volumes/Data", isDirectory: true),
                owner: uid_t = getuid(),
                administrator: @escaping (String) -> Bool = BootVolumeIcon.runAsAdministrator) {
        self.root = root
        self.owner = owner
        self.administrator = administrator
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
            // Already set up by an earlier change: swap the artwork without a password.
            if info[8] & 0x04 != 0, rewriteInPlace(from: source) { return true }
            info[8] |= 0x04                     // kHasCustomIcon
            // Remove first, so an older root-owned, read-only file is replaced rather than written through.
            script = "/bin/rm -f \(Self.quote(iconFile.path)) && /bin/cp \(Self.quote(source.path)) \(Self.quote(iconFile.path)) && "
                + "/usr/sbin/chown \(owner) \(Self.quote(iconFile.path)) && "
                + "/bin/chmod 644 \(Self.quote(iconFile.path)) && "
                + "/usr/bin/xattr -wx com.apple.FinderInfo \(Self.hex(info)) \(Self.quote(root.path))"
        } else {
            info[8] &= ~0x04
            script = "/bin/rm -f \(Self.quote(iconFile.path)) && "
                + "/usr/bin/xattr -wx com.apple.FinderInfo \(Self.hex(info)) \(Self.quote(root.path))"
        }
        guard administrator(script) else { return false }
        Self.refreshFinder(root)
        return true
    }

    /// Overwrites the existing icon file's contents. The file is opened and truncated rather than replaced,
    /// so only the file (which the first change gave to the user) has to be writable, not the root-owned folder.
    private func rewriteInPlace(from source: URL) -> Bool {
        guard FileManager.default.isWritableFile(atPath: iconFile.path),
              let data = try? Data(contentsOf: source),
              let handle = try? FileHandle(forWritingTo: iconFile) else { return false }
        defer { try? handle.close() }
        do {
            try handle.truncate(atOffset: 0)
            try handle.write(contentsOf: data)
        } catch {
            return false
        }
        Self.refreshFinder(root)
        return true
    }

    /// Tells Finder the startup disk's icon changed.
    static func refreshFinder(_ root: URL) {
        NSWorkspace.shared.noteFileSystemChanged(root.path)
        NSWorkspace.shared.noteFileSystemChanged("/")
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

    /// Runs a shell command with administrator privileges, showing the standard password prompt. Returns false
    /// if the user cancels or the command fails. The script runs inside HyperIcon rather than in a separate
    /// `osascript` process so macOS can reuse the authorization for a few minutes instead of asking again.
    public static func runAsAdministrator(_ command: String) -> Bool {
        let literal = command.replacingOccurrences(of: "\\", with: "\\\\").replacingOccurrences(of: "\"", with: "\\\"")
        let source = "do shell script \"\(literal)\" with administrator privileges "
            + "with prompt \"HyperIcon wants to change the icon of your startup disk.\""
        let run = { () -> Bool in
            guard let script = NSAppleScript(source: source) else { return false }
            var error: NSDictionary?
            script.executeAndReturnError(&error)
            return error == nil
        }
        // NSAppleScript is only safe on the main thread. The engine calls this from its own queue.
        return Thread.isMainThread ? run() : DispatchQueue.main.sync(execute: run)
    }
}
