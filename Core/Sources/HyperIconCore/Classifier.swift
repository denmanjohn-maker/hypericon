import Foundation

/// The name Finder uses for a folder's custom icon file.
public let iconFileName = "Icon\r"

public struct Classifier: Sendable {
    public var rules: RuleSet
    /// When true a `.git` folder wins over language and tooling markers.
    public var preferGit: Bool

    private let extensionIndex: [String: FolderCategory]

    public init(rules: RuleSet = .standard, preferGit: Bool = false) {
        self.rules = rules
        self.preferGit = preferGit
        var index: [String: FolderCategory] = [:]
        for (raw, exts) in rules.extensions {
            guard let category = FolderCategory(rawValue: raw) else { continue }
            for ext in exts { index[ext.lowercased()] = category }
        }
        extensionIndex = index
    }

    public func classify(_ folder: URL, fileManager fm: FileManager = .default) -> FolderCategory {
        guard let names = try? fm.contentsOfDirectory(atPath: folder.path) else { return .folder }
        if let marker = markerCategory(names: names, folder: folder, fm: fm) { return marker }
        return majorityCategory(folder: folder, fm: fm) ?? .folder
    }

    // MARK: markers

    private func markerCategory(names: [String], folder: URL, fm: FileManager) -> FolderCategory? {
        let nameSet = Set(names)
        if preferGit, nameSet.contains(".git") { return .git }
        let lowered = names.map { $0.lowercased() }
        for rule in rules.markers {
            for pattern in rule.names {
                if pattern.hasPrefix("*.") {
                    let suffix = String(pattern.dropFirst()).lowercased()
                    if lowered.contains(where: { $0.hasSuffix(suffix) && $0.count > suffix.count }) { return rule.category }
                } else if pattern.contains("/") {
                    if fm.fileExists(atPath: folder.appendingPathComponent(pattern).path) { return rule.category }
                } else if nameSet.contains(pattern) {
                    return rule.category
                }
            }
        }
        return nil
    }

    // MARK: majority

    private struct Tally {
        var counts: [FolderCategory: Int] = [:]
        var total = 0
        var subfolders: [URL] = []
    }

    private func tally(_ folder: URL, into tally: inout Tally, fm: FileManager) {
        let keys: [URLResourceKey] = [.isDirectoryKey, .isPackageKey]
        guard let items = try? fm.contentsOfDirectory(at: folder, includingPropertiesForKeys: keys, options: [.skipsHiddenFiles]) else {
            return
        }
        for item in items where item.lastPathComponent != iconFileName {
            let values = try? item.resourceValues(forKeys: Set(keys))
            if values?.isDirectory == true, values?.isPackage != true {
                tally.subfolders.append(item)
                continue
            }
            tally.total += 1
            if let category = extensionIndex[item.pathExtension.lowercased()] {
                tally.counts[category, default: 0] += 1
            }
        }
    }

    private func majorityCategory(folder: URL, fm: FileManager) -> FolderCategory? {
        var result = Tally()
        tally(folder, into: &result, fm: fm)
        // A folder that only organises subfolders is judged by what those subfolders hold.
        if result.total < 3 {
            var nested = Tally()
            for sub in result.subfolders.prefix(24) { tally(sub, into: &nested, fm: fm) }
            result.total += nested.total
            for (category, count) in nested.counts { result.counts[category, default: 0] += count }
        }
        guard result.total > 0 else { return nil }
        // Sorted for a stable answer when two categories tie.
        let best = result.counts.sorted { ($0.value, $1.key.rawValue) > ($1.value, $0.key.rawValue) }.first
        guard let best, Double(best.value) / Double(result.total) >= rules.majorityThreshold else { return nil }
        return best.key
    }
}
