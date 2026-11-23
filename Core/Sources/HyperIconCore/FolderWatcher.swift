import CoreServices
import Foundation

/// Watches a directory tree with FSEvents and reports the folders whose contents changed.
public final class FolderWatcher {
    private let path: String
    private let latency: TimeInterval
    private let handler: ([String]) -> Void
    private var stream: FSEventStreamRef?
    private let queue = DispatchQueue(label: "com.hypericon.watcher", qos: .utility)

    public init(path: String, latency: TimeInterval = 3, handler: @escaping ([String]) -> Void) {
        self.path = path
        self.latency = latency
        self.handler = handler
    }

    deinit { stop() }

    public func start() {
        guard stream == nil else { return }
        var context = FSEventStreamContext(version: 0, info: Unmanaged.passUnretained(self).toOpaque(),
                                           retain: nil, release: nil, copyDescription: nil)
        let callback: FSEventStreamCallback = { _, info, _, eventPaths, _, _ in
            guard let info else { return }
            let watcher = Unmanaged<FolderWatcher>.fromOpaque(info).takeUnretainedValue()
            let paths = unsafeBitCast(eventPaths, to: NSArray.self) as? [String] ?? []
            if !paths.isEmpty { watcher.handler(paths) }
        }
        // IgnoreSelf keeps the icons we write from triggering another pass.
        let flags = UInt32(kFSEventStreamCreateFlagUseCFTypes | kFSEventStreamCreateFlagIgnoreSelf)
        guard let created = FSEventStreamCreate(kCFAllocatorDefault, callback, &context, [path] as CFArray,
                                                FSEventStreamEventId(kFSEventStreamEventIdSinceNow), latency, flags) else { return }
        stream = created
        FSEventStreamSetDispatchQueue(created, queue)
        FSEventStreamStart(created)
    }

    public func stop() {
        guard let stream else { return }
        FSEventStreamStop(stream)
        FSEventStreamInvalidate(stream)
        FSEventStreamRelease(stream)
        self.stream = nil
    }
}
