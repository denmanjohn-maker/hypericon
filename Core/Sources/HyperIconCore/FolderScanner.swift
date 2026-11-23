import Foundation

/// Decides which folders under the home folder are eligible for theming.
public struct FolderScanner: Sendable {
    public let home: URL
    public var maxDepth: Int
    public var skipNames: Set<String>
    public var excludedPaths: [String]

    /// Top-level folders that are never themed or entered.
    static let topLevelSkips: Set<String> = ["Library", "Applications"]
    private static let keys: [URLResourceKey] = [.isDirectoryKey, .isPackageKey, .isSymbolicLinkKey]

    public init(home: URL, maxDepth: Int, skipNames: Set<String>, excludedPaths: [String] = []) {
        self.home = home.standardizedFileURL
        self.maxDepth = max(1, maxDepth)
        self.skipNames = skipNames
        self.excludedPaths = excludedPaths.map { URL(fileURLWithPath: $0).standardizedFileURL.path }
    }

    static func isGitRepository(_ folder: URL) -> Bool {
        FileManager.default.fileExists(atPath: folder.appendingPathComponent(".git").path)
    }

    private func isExcluded(_ path: String) -> Bool {
        excludedPaths.contains { path == $0 || path.hasPrefix($0 + "/") }
    }

    private func nameAllowed(_ name: String, depth: Int) -> Bool {
        if name.hasPrefix(".") || skipNames.contains(name) { return false }
        if depth == 1, Self.topLevelSkips.contains(name) { return false }
        return true
    }

    private func isPlainFolder(_ url: URL) -> Bool {
        guard let values = try? url.resourceValues(forKeys: Set(Self.keys)) else { return false }
        return values.isDirectory == true && values.isPackage != true && values.isSymbolicLink != true
    }

    /// Calls `visit` for every eligible folder, parents before children. Stops early if `visit` returns false.
    public func walk(_ visit: (URL) -> Bool) {
        _ = walk(home, depth: 1, visit)
    }

    private func walk(_ directory: URL, depth: Int, _ visit: (URL) -> Bool) -> Bool {
        let children = (try? FileManager.default.contentsOfDirectory(at: directory, includingPropertiesForKeys: Self.keys, options: [])) ?? []
        for child in children.sorted(by: { $0.lastPathComponent < $1.lastPathComponent }) {
            guard nameAllowed(child.lastPathComponent, depth: depth), isPlainFolder(child), !isExcluded(child.path) else { continue }
            guard visit(child) else { return false }
            // Repositories get one icon at their root; their insides are left untouched.
            if depth < maxDepth, !Self.isGitRepository(child) {
                guard walk(child, depth: depth + 1, visit) else { return false }
            }
        }
        return true
    }

    /// Whether a single folder (reported by the file-system watcher) would be reached by `walk`.
    public func isEligible(_ folder: URL) -> Bool {
        let folder = folder.standardizedFileURL
        let homeParts = home.pathComponents
        let parts = folder.pathComponents
        guard parts.count > homeParts.count, Array(parts.prefix(homeParts.count)) == homeParts else { return false }
        let relative = Array(parts.dropFirst(homeParts.count))
        guard relative.count <= maxDepth, !isExcluded(folder.path) else { return false }
        var current = home
        for (index, name) in relative.enumerated() {
            guard nameAllowed(name, depth: index + 1) else { return false }
            current.appendPathComponent(name, isDirectory: true)
            guard isPlainFolder(current) else { return false }
            if index < relative.count - 1, Self.isGitRepository(current) { return false }
        }
        return true
    }
}
