import Foundation

/// Extended attribute that marks a folder as themed by HyperIcon, so icons can be found and removed
/// even if the journal is lost.
public let appliedAttribute = "com.hypericon.applied"

extension URL {
    /// The folder's real on-disk location with symlinks resolved, in the same form the file system reports
    /// for its children (for example `/private/var/...` rather than `/var/...`).
    var canonicalFolder: URL {
        guard let resolved = realpath(path, nil) else { return standardizedFileURL }
        defer { free(resolved) }
        return URL(fileURLWithPath: String(cString: resolved), isDirectory: true)
    }
}

enum Xattr {
    static func set(_ name: String, value: String, on url: URL) {
        let bytes = Array(value.utf8)
        _ = url.withUnsafeFileSystemRepresentation { path in
            setxattr(path, name, bytes, bytes.count, 0, 0)
        }
    }

    static func has(_ name: String, on url: URL) -> Bool {
        url.withUnsafeFileSystemRepresentation { path in
            getxattr(path, name, nil, 0, 0, 0) >= 0
        }
    }

    static func remove(_ name: String, from url: URL) {
        _ = url.withUnsafeFileSystemRepresentation { path in
            removexattr(path, name, 0)
        }
    }
}

/// Keeps Finder's hidden icon file out of `git status` using the repository's local, uncommitted exclude file.
enum GitExclude {
    static let marker = "# HyperIcon: ignore Finder folder icons"
    static let pattern = "Icon?"

    private static func excludeFile(_ repo: URL) -> URL? {
        let info = repo.appendingPathComponent(".git/info", isDirectory: true)
        var isDir: ObjCBool = false
        // `.git` is a plain file in worktrees and submodules; those are left alone.
        guard FileManager.default.fileExists(atPath: repo.appendingPathComponent(".git").path, isDirectory: &isDir), isDir.boolValue else {
            return nil
        }
        try? FileManager.default.createDirectory(at: info, withIntermediateDirectories: true)
        return info.appendingPathComponent("exclude")
    }

    /// Returns true if HyperIcon added the lines (and so must remove them on restore).
    static func add(to repo: URL) -> Bool {
        guard let file = excludeFile(repo) else { return false }
        let existing = (try? String(contentsOf: file, encoding: .utf8)) ?? ""
        if existing.contains(marker) { return true }
        let separator = existing.isEmpty || existing.hasSuffix("\n") ? "" : "\n"
        let updated = existing + separator + marker + "\n" + pattern + "\n"
        return (try? updated.write(to: file, atomically: true, encoding: .utf8)) != nil
    }

    static func remove(from repo: URL) {
        guard let file = excludeFile(repo), let existing = try? String(contentsOf: file, encoding: .utf8),
              existing.contains(marker) else { return }
        var lines = existing.components(separatedBy: "\n")
        if let index = lines.firstIndex(of: marker) {
            lines.remove(at: index)
            if index < lines.count, lines[index] == pattern { lines.remove(at: index) }
        }
        try? lines.joined(separator: "\n").write(to: file, atomically: true, encoding: .utf8)
    }
}
