import Foundation
import HyperIconCore

// Development build of the command line. Themes are read from ./Themes or HYPERICON_THEMES.
let themes = ProcessInfo.processInfo.environment["HYPERICON_THEMES"] ?? "Themes"
exit(CommandLineTool.run(Array(CommandLine.arguments.dropFirst()), themeDirectories: [URL(fileURLWithPath: themes, isDirectory: true)]))
