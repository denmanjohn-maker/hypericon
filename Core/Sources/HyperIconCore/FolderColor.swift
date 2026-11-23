import Foundation

/// The colour a folder is drawn in: the colour of its Finder tag, or blue when it has none.
/// Raw values match the base folder images in `Themes/_base/`.
public enum FolderColor: String, Codable, CaseIterable, Sendable {
    case blue, gray, green, purple, yellow, red, orange

    /// Maps Finder's label number (the colour of the folder's first coloured tag).
    public init(labelNumber: Int) {
        switch labelNumber {
        case 1: self = .gray
        case 2: self = .green
        case 3: self = .purple
        case 5: self = .yellow
        case 6: self = .red
        case 7: self = .orange
        default: self = .blue
        }
    }

    /// Reads the folder's current tag colour from disk, bypassing any cached resource values.
    public static func of(_ folder: URL) -> FolderColor {
        var url = folder
        url.removeAllCachedResourceValues()
        let label = (try? url.resourceValues(forKeys: [.labelNumberKey]))?.labelNumber ?? 0
        return FolderColor(labelNumber: label)
    }
}
