import SwiftUI

struct HyperIconApp: App {
    @StateObject private var model = AppModel()

    var body: some Scene {
        MenuBarExtra("HyperIcon", systemImage: "folder.fill.badge.gearshape") {
            MenuPanel()
                .environmentObject(model)
        }
        .menuBarExtraStyle(.window)

        Settings {
            SettingsView()
                .environmentObject(model)
        }
    }
}
