import Foundation

/// A mounted disk that can be themed.
public struct MountedVolume: Equatable, Sendable {
    public let url: URL
    /// Stable across mounts, so a disk is recognised when it is plugged in again.
    public let uuid: String
    /// `.externalDisk` or `.networkDisk`. The boot disk is handled separately because it needs an admin password.
    public let place: Place

    public init(url: URL, uuid: String, place: Place) {
        self.url = url
        self.uuid = uuid
        self.place = place
    }

    /// The journal key for this disk. Disks are keyed by UUID because their mount path can change.
    var journalKey: String { "volume:\(uuid)" }
}

/// Lists the disks HyperIcon may theme. Abstracted so the engine can be tested without real disks.
public protocol VolumeListing: AnyObject {
    func mounted() -> [MountedVolume]
}

/// The real mounted volumes, minus anything that cannot or should not get an icon.
public final class SystemVolumes: VolumeListing {
    private static let keys: [URLResourceKey] = [
        .volumeUUIDStringKey, .volumeIsLocalKey, .volumeIsReadOnlyKey, .volumeIsRootFileSystemKey,
        .volumeIsBrowsableKey, .volumeIsInternalKey,
    ]

    public init() {}

    public func mounted() -> [MountedVolume] {
        let urls = FileManager.default.mountedVolumeURLs(includingResourceValuesForKeys: Self.keys, options: [.skipHiddenVolumes]) ?? []
        return urls.compactMap { url in
            guard let values = try? url.resourceValues(forKeys: Set(Self.keys)),
                  let uuid = values.volumeUUIDString,
                  values.volumeIsRootFileSystem != true,
                  values.volumeIsReadOnly != true,
                  values.volumeIsBrowsable != false,
                  !url.path.hasPrefix("/System/"),
                  !Self.isBackupDisk(url) else { return nil }
            return MountedVolume(url: url, uuid: uuid, place: values.volumeIsLocal == false ? .networkDisk : .externalDisk)
        }
    }

    /// Time Machine disks are left alone.
    private static func isBackupDisk(_ url: URL) -> Bool {
        let fm = FileManager.default
        return fm.fileExists(atPath: url.appendingPathComponent("Backups.backupdb").path)
            || fm.fileExists(atPath: url.appendingPathComponent(".com.apple.timemachine.donotpresent").path)
    }
}

/// Sets the icon of the startup disk ("Macintosh HD"). This is the only change HyperIcon makes that needs
/// an administrator password, so it is kept behind its own setting and protocol.
public protocol BootDiskIconSetting: AnyObject {
    /// Sets the startup disk's icon from a PNG, or removes it when `imageURL` is nil. If `backup` is given
    /// on removal, that icon file is put back instead. Returns false if the user cancelled or it failed.
    func setIcon(_ imageURL: URL?, restoring backup: URL?) -> Bool
    func hasCustomIcon() -> Bool
    /// Copies the startup disk's current custom icon file, if it has one.
    func backUpIcon(to destination: URL) -> Bool
}

/// The locations outside the home folder that HyperIcon can theme. Each is optional so tests and other
/// callers only touch what they opt into.
public struct SystemPlaces {
    public var applications: URL?
    public var volumes: VolumeListing?
    public var bootDisk: BootDiskIconSetting?

    public init(applications: URL? = nil, volumes: VolumeListing? = nil, bootDisk: BootDiskIconSetting? = nil) {
        self.applications = applications
        self.volumes = volumes
        self.bootDisk = bootDisk
    }

    /// Nothing outside the home folder.
    public static var none: SystemPlaces { SystemPlaces() }

    /// `/Applications`, mounted disks and the startup disk of this Mac.
    public static var live: SystemPlaces {
        SystemPlaces(applications: URL(fileURLWithPath: "/Applications", isDirectory: true),
                     volumes: SystemVolumes(), bootDisk: BootVolumeIcon())
    }
}
