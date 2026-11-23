import Foundation

/// Where HyperIcon keeps its state. Nothing is stored outside this directory except the icons themselves.
public struct AppPaths: Sendable {
    public let base: URL

    public init(base: URL? = nil) {
        self.base = base ?? FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask)[0]
            .appendingPathComponent("HyperIcon", isDirectory: true)
    }

    public var journal: URL { base.appendingPathComponent("journal.jsonl") }
    public var backups: URL { base.appendingPathComponent("Backups", isDirectory: true) }
    public var settings: URL { base.appendingPathComponent("settings.json") }
    public var rules: URL { base.appendingPathComponent("rules.json") }
    public var userThemes: URL { base.appendingPathComponent("Themes", isDirectory: true) }
    /// Finished icons (folder plus artwork), rebuilt on demand.
    public var cache: URL { base.appendingPathComponent("Cache", isDirectory: true) }

    public func ensure() {
        for dir in [base, backups, userThemes] {
            try? FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
        }
    }
}

public struct Preferences: Codable, Equatable, Sendable {
    /// The active theme, or nil until the user picks one. Nothing is changed before that.
    public var themeID: String?
    public var paused = false
    /// How many folder levels below the home folder are themed.
    public var maxDepth = 4
    /// Replace icons the user set by hand (they are backed up and put back on restore).
    public var overrideCustomIcons = false
    public var preferGit = false
    /// Draw each folder in the colour of its Finder tag. When off, every folder is blue.
    public var matchTagColor = true
    /// Absolute paths that are never themed, along with everything inside them.
    public var excludedPaths: [String] = []

    public init() {}

    public init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        themeID = try c.decodeIfPresent(String.self, forKey: .themeID)
        paused = try c.decodeIfPresent(Bool.self, forKey: .paused) ?? false
        maxDepth = try c.decodeIfPresent(Int.self, forKey: .maxDepth) ?? 4
        overrideCustomIcons = try c.decodeIfPresent(Bool.self, forKey: .overrideCustomIcons) ?? false
        preferGit = try c.decodeIfPresent(Bool.self, forKey: .preferGit) ?? false
        matchTagColor = try c.decodeIfPresent(Bool.self, forKey: .matchTagColor) ?? true
        excludedPaths = try c.decodeIfPresent([String].self, forKey: .excludedPaths) ?? []
    }

    public static func load(from url: URL) -> Preferences {
        guard let data = try? Data(contentsOf: url), let settings = try? JSONDecoder().decode(Preferences.self, from: data) else {
            return Preferences()
        }
        return settings
    }

    public func save(to url: URL) {
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        guard let data = try? encoder.encode(self) else { return }
        try? FileManager.default.createDirectory(at: url.deletingLastPathComponent(), withIntermediateDirectories: true)
        try? data.write(to: url, options: .atomic)
    }
}
