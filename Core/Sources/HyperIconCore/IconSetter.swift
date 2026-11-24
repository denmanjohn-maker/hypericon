import AppKit

/// The file a disk's custom icon is stored in, at the root of the disk.
public let volumeIconFileName = ".VolumeIcon.icns"

/// The only code that touches Finder icons. Abstracted so the engine can be tested without Finder.
public protocol IconSetter: AnyObject {
    /// Sets the folder's custom icon from an image file, or removes it when `imageURL` is nil.
    @discardableResult func setIcon(_ imageURL: URL?, for folder: URL) -> Bool
    func hasCustomIcon(_ folder: URL) -> Bool
    /// Saves the folder's current custom icon so it can be put back later.
    func backUpIcon(of folder: URL, to destination: URL) -> Bool
}

public final class WorkspaceIconSetter: IconSetter {
    private var cache: [URL: NSImage] = [:]
    private let lock = NSLock()

    public init() {}

    private func image(at url: URL) -> NSImage? {
        lock.lock()
        defer { lock.unlock() }
        if let cached = cache[url] { return cached }
        guard let image = NSImage(contentsOf: url) else { return nil }
        cache[url] = image
        return image
    }

    @discardableResult
    public func setIcon(_ imageURL: URL?, for folder: URL) -> Bool {
        guard let imageURL else {
            return NSWorkspace.shared.setIcon(nil, forFile: folder.path, options: [])
        }
        guard let image = image(at: imageURL) else { return false }
        return NSWorkspace.shared.setIcon(image, forFile: folder.path, options: [])
    }

    public func hasCustomIcon(_ folder: URL) -> Bool {
        // Folders keep their icon in a hidden `Icon\r` file; disks keep it in `.VolumeIcon.icns` at their root.
        let fm = FileManager.default
        return fm.fileExists(atPath: folder.appendingPathComponent(iconFileName).path)
            || fm.fileExists(atPath: folder.appendingPathComponent(volumeIconFileName).path)
    }

    public func backUpIcon(of folder: URL, to destination: URL) -> Bool {
        let icon = NSWorkspace.shared.icon(forFile: folder.path)
        guard let data = icon.tiffRepresentation else { return false }
        return (try? data.write(to: destination, options: .atomic)) != nil
    }
}
