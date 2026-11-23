import CoreGraphics
import Foundation
import ImageIO
import UniformTypeIdentifiers

/// Draws a theme's artwork on top of a plain folder and writes the result as a PNG.
enum IconComposer {
    private static func load(_ url: URL) -> CGImage? {
        guard let source = CGImageSourceCreateWithURL(url as CFURL, nil) else { return nil }
        return CGImageSourceCreateImageAtIndex(source, 0, nil)
    }

    /// Returns `destination` if it was written (or already exists), nil on failure.
    static func compose(base: URL?, artwork: URL, to destination: URL) -> URL? {
        if FileManager.default.fileExists(atPath: destination.path) { return destination }
        guard let art = load(artwork) else { return nil }
        let folder = base.flatMap(load)
        let width = folder?.width ?? art.width
        let height = folder?.height ?? art.height
        guard let space = CGColorSpace(name: CGColorSpace.sRGB),
              let context = CGContext(data: nil, width: width, height: height, bitsPerComponent: 8, bytesPerRow: 0,
                                      space: space, bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue) else { return nil }
        let rect = CGRect(x: 0, y: 0, width: width, height: height)
        context.interpolationQuality = .high
        if let folder { context.draw(folder, in: rect) }
        context.draw(art, in: rect)
        guard let image = context.makeImage() else { return nil }

        try? FileManager.default.createDirectory(at: destination.deletingLastPathComponent(), withIntermediateDirectories: true)
        guard let output = CGImageDestinationCreateWithURL(destination as CFURL, UTType.png.identifier as CFString, 1, nil) else {
            return nil
        }
        CGImageDestinationAddImage(output, image, nil)
        return CGImageDestinationFinalize(output) ? destination : nil
    }
}
