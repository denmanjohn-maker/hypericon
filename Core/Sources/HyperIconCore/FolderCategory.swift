import Foundation

/// What a folder "is", decided from its contents. Raw values match icon file names in a theme.
public enum FolderCategory: String, Codable, CaseIterable, Sendable {
    case folder
    case git, xcode, node, python, rust, go, java, dotnet
    case docker, kubernetes, terraform, ci
    case documents, spreadsheets, presentations, pdf, images, music, video
    case code, archives, fonts, books, design, data, web
}
