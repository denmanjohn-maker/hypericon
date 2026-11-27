import HyperIconCore
import SwiftUI

struct SettingsView: View {
    @EnvironmentObject private var model: AppModel

    private var version: String {
        Bundle.main.object(forInfoDictionaryKey: "CFBundleShortVersionString") as? String ?? "dev"
    }

    var body: some View {
        Form {
            Section("General") {
                Toggle("Open HyperIcon at login", isOn: $model.launchAtLogin)
                Stepper("Theme folders up to \(model.preferences.maxDepth) levels below your home folder",
                        value: Binding(get: { model.preferences.maxDepth }, set: { model.setMaxDepth($0) }), in: 1...8)
            }
            Section("Colour") {
                Toggle("Use each folder's tag colour", isOn: Binding(get: { model.preferences.matchTagColor },
                                                                     set: { model.setMatchTagColor($0) }))
                Text("To change a folder's colour, right-click it in Finder and choose a tag colour. "
                     + "Untagged folders are blue. Turn this off to make every folder blue.")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
            Section("Icons") {
                Toggle("Replace icons I set myself", isOn: Binding(get: { model.preferences.overrideCustomIcons },
                                                                    set: { model.setOverrideCustomIcons($0) }))
                Text("Your own icons are backed up and put back when you restore.")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                Toggle("Always use the Git icon for repositories", isOn: Binding(get: { model.preferences.preferGit },
                                                                                  set: { model.setPreferGit($0) }))
                Text("When off, a repository shows its language or tool, such as Node or Terraform.")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
            Section("Disks & favorites") {
                placeToggle("Theme favorite folders", \.themeFavorites)
                Text("Desktop, Documents, Downloads, Pictures, Music, Movies and Applications get the theme's own artwork. "
                     + "The Finder sidebar always shows its own small symbols, so the new icons appear in Finder windows, "
                     + "the path bar, Get Info and the Dock.")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                placeToggle("Theme my home folder", \.themeHome)
                placeToggle("Theme external and USB drives", \.themeExternalDisks)
                placeToggle("Theme network shares", \.themeNetworkDisks)
                Text("A network share's icon is saved on the server, so other people who use it may see it too.")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                placeToggle("Theme Macintosh HD", \.themeBootDisk)
                Text("Asks for your password once to set up the startup disk's icon. Changing themes after that doesn't ask again; "
                     + "restoring the original icon may ask once more.")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
            Section("Excluded folders") {
                if model.preferences.excludedPaths.isEmpty {
                    Text("No folders excluded.").foregroundStyle(.secondary)
                }
                ForEach(model.preferences.excludedPaths, id: \.self) { path in
                    HStack {
                        Text((path as NSString).abbreviatingWithTildeInPath)
                            .lineLimit(1)
                            .truncationMode(.middle)
                        Spacer()
                        Button("Remove") { model.removeExcludedFolder(path) }
                    }
                }
                Button("Exclude a Folder…") { model.addExcludedFolder() }
            }
            Section("Themes") {
                Button("Open My Themes Folder") { model.openThemesFolder() }
                Text("Drop a theme folder there, then choose Rescan Folders from the menu.")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
            Section {
                Button("Restore Original Icons…") { model.restoreOriginalIcons() }
                Text("HyperIcon \(version)")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
        }
        .formStyle(.grouped)
        .frame(width: 480, height: 640)
    }

    private func placeToggle(_ title: String, _ option: WritableKeyPath<Preferences, Bool>) -> some View {
        Toggle(title, isOn: Binding(get: { model.preferences[keyPath: option] }, set: { model.setPlaceOption(option, $0) }))
    }
}
