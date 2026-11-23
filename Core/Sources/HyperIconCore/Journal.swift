import Foundation

/// One folder HyperIcon has changed, and what is needed to undo it.
public struct JournalEntry: Codable, Equatable, Sendable {
    public var path: String
    public var category: FolderCategory
    public var themeID: String
    /// File name in the backups directory holding the icon the user had before, if any.
    public var backup: String?
    /// True if HyperIcon added the ignore lines to this repository's `.git/info/exclude`.
    public var gitExclude: Bool
    public var date: Date

    public init(path: String, category: FolderCategory, themeID: String, backup: String? = nil, gitExclude: Bool = false, date: Date = Date()) {
        self.path = path
        self.category = category
        self.themeID = themeID
        self.backup = backup
        self.gitExclude = gitExclude
        self.date = date
    }
}

/// Append-only record of every folder touched. An entry is written *before* its icon is changed, so a
/// crash can never leave a themed folder that restore does not know about.
public final class Journal {
    private struct Line: Codable {
        var set: JournalEntry?
        var remove: String?
    }

    private let url: URL
    private var entries: [String: JournalEntry] = [:]
    private var lineCount = 0
    private let lock = NSLock()
    private let encoder = JSONEncoder()

    public init(url: URL) {
        self.url = url
        let decoder = JSONDecoder()
        if let text = try? String(contentsOf: url, encoding: .utf8) {
            for raw in text.split(separator: "\n") {
                guard let line = try? decoder.decode(Line.self, from: Data(raw.utf8)) else { continue }
                lineCount += 1
                if let entry = line.set { entries[entry.path] = entry }
                if let path = line.remove { entries[path] = nil }
            }
        }
        if lineCount > max(200, entries.count * 3) { compact() }
    }

    public var all: [JournalEntry] {
        lock.lock()
        defer { lock.unlock() }
        return entries.values.sorted { $0.path < $1.path }
    }

    public var count: Int {
        lock.lock()
        defer { lock.unlock() }
        return entries.count
    }

    public subscript(path: String) -> JournalEntry? {
        lock.lock()
        defer { lock.unlock() }
        return entries[path]
    }

    public func record(_ entry: JournalEntry) {
        lock.lock()
        defer { lock.unlock() }
        entries[entry.path] = entry
        append(Line(set: entry, remove: nil))
    }

    public func remove(_ path: String) {
        lock.lock()
        defer { lock.unlock() }
        guard entries.removeValue(forKey: path) != nil else { return }
        append(Line(set: nil, remove: path))
    }

    private func append(_ line: Line) {
        guard var data = try? encoder.encode(line) else { return }
        data.append(0x0A)
        let fm = FileManager.default
        if !fm.fileExists(atPath: url.path) {
            try? fm.createDirectory(at: url.deletingLastPathComponent(), withIntermediateDirectories: true)
            fm.createFile(atPath: url.path, contents: nil)
        }
        guard let handle = try? FileHandle(forWritingTo: url) else { return }
        defer { try? handle.close() }
        _ = try? handle.seekToEnd()
        try? handle.write(contentsOf: data)
        lineCount += 1
    }

    private func compact() {
        var data = Data()
        for entry in entries.values {
            guard let line = try? encoder.encode(Line(set: entry, remove: nil)) else { continue }
            data.append(line)
            data.append(0x0A)
        }
        if (try? data.write(to: url, options: .atomic)) != nil { lineCount = entries.count }
    }
}
