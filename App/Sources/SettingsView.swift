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
        .frame(width: 480, height: 560)
    }
}
