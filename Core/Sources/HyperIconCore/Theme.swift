import Foundation

public struct Theme: Identifiable, Equatable, Sendable {
    public let id: String
    public let name: String
    public let group: String
    public let summary: String
    public let accent: String
    public let directory: URL

    /// The icon for `category`, falling back to the theme's generic folder.
    public func iconURL(for category: FolderCategory) -> URL? {
        let fm = FileManager.default
        for name in [category.rawValue, FolderCategory.folder.rawValue] {
            let url = directory.appendingPathComponent("\(name).png")
            if fm.fileExists(atPath: url.path) { return url }
        }
        return nil
    }

    public var previewURL: URL { directory.appendingPathComponent("preview.png") }

    /// The plain folder drawn under every theme's artwork, from the `_base` directory next to the themes.
    public func baseFolderURL(for color: FolderColor) -> URL? {
        let fm = FileManager.default
        for name in [color.rawValue, FolderColor.blue.rawValue] {
            let url = directory.deletingLastPathComponent().appendingPathComponent("_base/\(name).png")
            if fm.fileExists(atPath: url.path) { return url }
        }
        return nil
    }
}

public struct ThemeStore: Sendable {
    public static let groupOrder = ["Holidays", "Sci-Fi", "80s", "Computer Retro", "OS Classics"]

    public let directories: [URL]

    public init(directories: [URL]) {
        self.directories = directories
    }

    private struct Manifest: Decodable {
        let id: String
        let name: String
        let group: String?
        let description: String?
        let accent: String?
    }

    /// Every valid theme found, grouped in a stable order. Later directories override earlier ones by id.
    public func load() -> [Theme] {
        let fm = FileManager.default
        var byID: [String: Theme] = [:]
        for root in directories {
            let children = (try? fm.contentsOfDirectory(at: root, includingPropertiesForKeys: nil, options: [.skipsHiddenFiles])) ?? []
            for dir in children {
                guard let data = try? Data(contentsOf: dir.appendingPathComponent("theme.json")),
                      let manifest = try? JSONDecoder().decode(Manifest.self, from: data),
                      fm.fileExists(atPath: dir.appendingPathComponent("folder.png").path) else { continue }
                byID[manifest.id] = Theme(id: manifest.id, name: manifest.name, group: manifest.group ?? "Custom",
                                          summary: manifest.description ?? "", accent: manifest.accent ?? "#888888", directory: dir)
            }
        }
        func rank(_ group: String) -> Int { Self.groupOrder.firstIndex(of: group) ?? Self.groupOrder.count }
        return byID.values.sorted { (rank($0.group), $0.group, $0.name) < (rank($1.group), $1.group, $1.name) }
    }
}
