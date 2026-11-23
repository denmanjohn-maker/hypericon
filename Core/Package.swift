// swift-tools-version:5.9
import PackageDescription

let package = Package(
    name: "HyperIconCore",
    platforms: [.macOS(.v14)],
    products: [
        .library(name: "HyperIconCore", targets: ["HyperIconCore"]),
        .executable(name: "hypericon", targets: ["hypericon"]),
    ],
    targets: [
        .target(name: "HyperIconCore"),
        .executableTarget(name: "hypericon", dependencies: ["HyperIconCore"]),
        .testTarget(name: "HyperIconCoreTests", dependencies: ["HyperIconCore"]),
    ]
)
