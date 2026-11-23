import Foundation

/// A folder containing any of `names` is classified as `category`.
/// A name is an exact file name (`Cargo.toml`), a suffix glob (`*.tf`) or a relative path (`a/b`).
public struct MarkerRule: Codable, Equatable, Sendable {
    public var category: FolderCategory
    public var names: [String]

    public init(_ category: FolderCategory, _ names: [String]) {
        self.category = category
        self.names = names
    }
}

public struct RuleSet: Codable, Equatable, Sendable {
    /// Checked in order; the first match wins.
    public var markers: [MarkerRule]
    /// File extensions (lowercase, no dot) per category, used for the majority rule.
    public var extensions: [String: [String]]
    /// Share of files that must belong to one category for it to win.
    public var majorityThreshold: Double
    /// Folder names that are never themed or descended into.
    public var skipNames: [String]

    public init(markers: [MarkerRule], extensions: [String: [String]], majorityThreshold: Double, skipNames: [String]) {
        self.markers = markers
        self.extensions = extensions
        self.majorityThreshold = majorityThreshold
        self.skipNames = skipNames
    }

    public static let standard = RuleSet(
        markers: [
            MarkerRule(.xcode, ["*.xcodeproj", "*.xcworkspace", "Package.swift"]),
            MarkerRule(.rust, ["Cargo.toml"]),
            MarkerRule(.go, ["go.mod"]),
            MarkerRule(.dotnet, ["*.sln", "*.csproj", "*.fsproj", "*.vbproj"]),
            MarkerRule(.java, ["pom.xml", "build.gradle", "build.gradle.kts"]),
            MarkerRule(.python, ["pyproject.toml", "requirements.txt", "setup.py", "Pipfile"]),
            MarkerRule(.node, ["package.json"]),
            MarkerRule(.kubernetes, ["Chart.yaml", "kustomization.yaml", "kustomization.yml", "helmfile.yaml"]),
            MarkerRule(.terraform, ["*.tf", "terragrunt.hcl"]),
            MarkerRule(.docker, ["Dockerfile", "docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"]),
            MarkerRule(.ci, ["Jenkinsfile", "azure-pipelines.yml", "azure-pipelines.yaml", ".gitlab-ci.yml"]),
            MarkerRule(.git, [".git"]),
        ],
        extensions: [
            "documents": ["doc", "docx", "pages", "txt", "rtf", "rtfd", "md", "odt", "tex"],
            "spreadsheets": ["xls", "xlsx", "xlsm", "numbers", "ods"],
            "presentations": ["ppt", "pptx", "key", "odp"],
            "pdf": ["pdf"],
            "images": ["png", "jpg", "jpeg", "gif", "heic", "tif", "tiff", "bmp", "webp", "svg", "raw", "cr2", "nef", "dng"],
            "music": ["mp3", "m4a", "wav", "flac", "aac", "aif", "aiff", "ogg", "opus"],
            "video": ["mp4", "mov", "mkv", "avi", "m4v", "webm", "wmv"],
            "code": ["swift", "c", "h", "cc", "cpp", "hpp", "m", "mm", "py", "js", "jsx", "ts", "tsx", "rb", "sh", "bash",
                     "zsh", "ps1", "go", "rs", "java", "kt", "cs", "php", "pl", "lua", "r", "scala", "groovy"],
            "archives": ["zip", "tar", "gz", "tgz", "bz2", "xz", "7z", "rar", "dmg", "pkg", "iso"],
            "fonts": ["ttf", "otf", "ttc", "woff", "woff2"],
            "books": ["epub", "mobi", "azw3", "ibooks"],
            "design": ["psd", "ai", "sketch", "fig", "xd", "afdesign", "afphoto", "indd", "blend", "obj", "stl", "fbx", "usdz"],
            "data": ["csv", "tsv", "json", "xml", "yaml", "yml", "sql", "sqlite", "db", "parquet", "log"],
            "web": ["html", "htm", "css", "scss", "less"],
        ],
        majorityThreshold: 0.5,
        skipNames: ["node_modules", "build", "dist", "target", "vendor", "Pods", "DerivedData", "venv", "__pycache__",
                    "bower_components", "Carthage"]
    )

    /// Loads user rules from `url` if present and valid, otherwise the built-in rules.
    public static func load(overridesAt url: URL) -> RuleSet {
        guard let data = try? Data(contentsOf: url), let rules = try? JSONDecoder().decode(RuleSet.self, from: data) else {
            return .standard
        }
        return rules
    }
}
