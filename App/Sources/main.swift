import Foundation
import HyperIconCore

// `HyperIcon.app/Contents/MacOS/HyperIcon restore` works without launching the menu bar app.
let arguments = Array(CommandLine.arguments.dropFirst())
if let command = arguments.first, CommandLineTool.commands.contains(command) {
    exit(CommandLineTool.run(arguments, themeDirectories: [AppModel.bundledThemes]))
}
HyperIconApp.main()
