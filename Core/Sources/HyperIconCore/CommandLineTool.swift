import Foundation

/// The `hypericon` command line, also reachable as `HyperIcon.app/Contents/MacOS/HyperIcon <command>`.
public enum CommandLineTool {
    public static let commands: Set<String> = ["restore", "status", "apply", "themes", "classify", "help"]

    static let usage = """
    Usage: hypericon <command>

      themes            List available themes
      apply <theme-id>  Apply a theme to the home folder
      status            Show the active theme and how many folders are themed
      classify <path>   Show which icon a folder would get
      restore [--deep]  Remove every HyperIcon icon (folders, favorites, Home and disks) and put originals back.
                        --deep also searches the home folder for icons the journal does not list.
    """

    public static func run(_ arguments: [String], themeDirectories: [URL]) -> Int32 {
        let paths = AppPaths()
        let engine = Engine(paths: paths, themeStore: ThemeStore(directories: themeDirectories + [paths.userThemes]), system: .live)
        switch arguments.first {
        case "themes":
            for theme in engine.themes { print("\(theme.id)\t\(theme.name) (\(theme.group))") }
        case "apply":
            guard arguments.count > 1, engine.themes.contains(where: { $0.id == arguments[1] }) else {
                print("Unknown theme. Run `hypericon themes` to list them.")
                return 2
            }
            engine.update {
                $0.themeID = arguments[1]
                $0.paused = false
                $0.declinedBootDiskChange = nil
            }
            engine.applyAllNow()
            print("Themed \(engine.journal.count) folders with \(arguments[1]).")
        case "status":
            let settings = engine.settings
            print("Theme: \(settings.themeID ?? "none")\(settings.paused ? " (paused)" : "")")
            print("Themed folders: \(engine.journal.count)")
        case "classify":
            guard arguments.count > 1 else { print(usage); return 2 }
            let classifier = Classifier(rules: .load(overridesAt: paths.rules), preferGit: engine.settings.preferGit)
            print(classifier.classify(URL(fileURLWithPath: arguments[1], isDirectory: true)).rawValue)
        case "restore":
            let report = engine.restoreAllNow(deep: arguments.contains("--deep"))
            print("Restored \(report.restored) folders and disks. \(report.missing) no longer exist.")
            if report.pending > 0 {
                print("\(report.pending) disks are not connected (or the password prompt was cancelled); they are restored when HyperIcon next sees them.")
            }
        default:
            print(usage)
            return arguments.first == "help" ? 0 : 2
        }
        return 0
    }
}
