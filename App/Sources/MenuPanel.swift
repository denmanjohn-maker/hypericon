import HyperIconCore
import SwiftUI

struct MenuPanel: View {
    @EnvironmentObject private var model: AppModel

    private let columns = [GridItem(.adaptive(minimum: 104), spacing: 10)]

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            header
            Divider()
            ScrollView {
                VStack(alignment: .leading, spacing: 14) {
                    ForEach(model.groupedThemes) { section in
                        Text(section.id.uppercased())
                            .font(.caption2.weight(.semibold))
                            .foregroundStyle(.secondary)
                        LazyVGrid(columns: columns, spacing: 10) {
                            ForEach(section.themes) { theme in
                                ThemeCard(theme: theme, isActive: theme.id == model.preferences.themeID) {
                                    model.select(theme)
                                }
                            }
                        }
                    }
                }
                .padding(14)
            }
            .frame(height: 380)
            Divider()
            footer
        }
        .frame(width: 372)
    }

    private var header: some View {
        HStack(spacing: 10) {
            VStack(alignment: .leading, spacing: 2) {
                Text(model.activeTheme?.name ?? "HyperIcon")
                    .font(.headline)
                Text(model.statusLine)
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
            Spacer()
            if model.status.activity != .idle {
                ProgressView().controlSize(.small)
            }
            if model.preferences.themeID != nil {
                Toggle("Active", isOn: Binding(get: { !model.preferences.paused }, set: { model.setPaused(!$0) }))
                    .toggleStyle(.switch)
                    .labelsHidden()
                    .help("Pause or resume theming")
            }
        }
        .padding(.horizontal, 14)
        .padding(.vertical, 10)
    }

    private var footer: some View {
        VStack(spacing: 0) {
            MenuRow(title: "Rescan Folders", symbol: "arrow.clockwise") { model.rescan() }
            MenuRow(title: "Restore Original Icons…", symbol: "arrow.uturn.backward") { model.restoreOriginalIcons() }
            SettingsLink {
                MenuRowLabel(title: "Settings…", symbol: "gearshape")
            }
            .buttonStyle(MenuRowStyle())
            .simultaneousGesture(TapGesture().onEnded { NSApp.activate(ignoringOtherApps: true) })
            MenuRow(title: "Quit HyperIcon", symbol: "power") { NSApp.terminate(nil) }
        }
        .padding(6)
    }
}

private struct ThemeCard: View {
    let theme: Theme
    let isActive: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(spacing: 5) {
                AsyncPreview(url: theme.previewURL)
                    .aspectRatio(1.44, contentMode: .fit)
                    .clipShape(RoundedRectangle(cornerRadius: 8))
                    .overlay(
                        RoundedRectangle(cornerRadius: 8)
                            .strokeBorder(isActive ? Color.accentColor : Color.primary.opacity(0.12), lineWidth: isActive ? 3 : 1)
                    )
                Text(theme.name)
                    .font(.caption)
                    .fontWeight(isActive ? .semibold : .regular)
                    .lineLimit(1)
            }
        }
        .buttonStyle(.plain)
        .help(theme.summary)
        .accessibilityLabel("\(theme.name) theme\(isActive ? ", active" : "")")
    }
}

private struct AsyncPreview: View {
    let url: URL

    var body: some View {
        if let image = NSImage(contentsOf: url) {
            Image(nsImage: image).resizable()
        } else {
            Color.secondary.opacity(0.2)
        }
    }
}

private struct MenuRowLabel: View {
    let title: String
    let symbol: String

    var body: some View {
        HStack(spacing: 8) {
            Image(systemName: symbol).frame(width: 18)
            Text(title)
            Spacer()
        }
        .contentShape(Rectangle())
    }
}

private struct MenuRowStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        HoverHighlight { configuration.label }
    }
}

private struct HoverHighlight<Content: View>: View {
    @ViewBuilder let content: Content
    @State private var hovering = false

    var body: some View {
        content
            .padding(.horizontal, 8)
            .padding(.vertical, 5)
            .background(RoundedRectangle(cornerRadius: 5).fill(hovering ? Color.primary.opacity(0.1) : Color.clear))
            .onHover { hovering = $0 }
    }
}

private struct MenuRow: View {
    let title: String
    let symbol: String
    let action: () -> Void

    var body: some View {
        Button(action: action) { MenuRowLabel(title: title, symbol: symbol) }
            .buttonStyle(MenuRowStyle())
    }
}
