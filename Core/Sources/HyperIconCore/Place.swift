import Foundation

/// A special location that gets its own standalone theme artwork instead of a folder with artwork on it:
/// the Finder favorites, the home folder and disks. Raw values match file names in a theme's `places/` folder.
public enum Place: String, Codable, CaseIterable, Sendable {
    case home, desktop, documents, downloads, applications, pictures, music, movies
    case bootDisk = "boot-disk"
    case externalDisk = "external-disk"
    case networkDisk = "network-disk"

    /// Favorite folders directly inside the home folder, by name.
    static let homeFolders: [String: Place] = [
        "Desktop": .desktop, "Documents": .documents, "Downloads": .downloads,
        "Pictures": .pictures, "Music": .music, "Movies": .movies,
    ]

    public var isDisk: Bool { self == .bootDisk || self == .externalDisk || self == .networkDisk }

    /// Favorites are themed by the "Theme favorite folders" setting; Home and disks have their own settings.
    public var isFavorite: Bool { !isDisk && self != .home }
}
