# Releasing HyperIcon

Pushing a version tag runs [`.github/workflows/release.yml`](../.github/workflows/release.yml), which:

1. Builds a universal Release build.
2. Signs it with your **Developer ID Application** certificate (hardened runtime).
3. Notarizes and staples the app, builds `HyperIcon.dmg`, then signs, notarizes and staples the disk image.
4. Generates a signed Sparkle `appcast.xml`.
5. Publishes a GitHub release with `HyperIcon.dmg`, its checksum, `appcast.xml` and `restore-icons.sh`.

Installed copies check `https://github.com/denmanjohn-maker/hypericon/releases/latest/download/appcast.xml` for updates.

## One-time setup

You do these once, on a Mac, with your Apple Developer account.

### 1. Developer ID certificate

1. In Xcode: **Settings → Accounts → your team → Manage Certificates → + → Developer ID Application**.
2. Open **Keychain Access**, find *Developer ID Application: Your Name (TEAMID)*, right-click → **Export**, save as `developer-id.p12` and set a password.
3. Encode it for GitHub:

```bash
base64 -i developer-id.p12 | pbcopy
```

| Secret | Value |
| --- | --- |
| `DEVELOPER_ID_P12_BASE64` | The clipboard contents from the command above |
| `DEVELOPER_ID_P12_PASSWORD` | The export password |
| `APPLE_TEAM_ID` | Your 10-character Team ID ([developer.apple.com/account](https://developer.apple.com/account) → Membership details) |

### 2. App Store Connect API key (for notarization)

1. Go to [App Store Connect → Users and Access → Integrations → App Store Connect API](https://appstoreconnect.apple.com/access/integrations/api).
2. Create a key with the **Developer** role and download the `.p8` file (it can only be downloaded once).

| Secret | Value |
| --- | --- |
| `ASC_KEY_ID` | The Key ID shown next to the key |
| `ASC_ISSUER_ID` | The Issuer ID shown above the key list |
| `ASC_KEY_P8` | The full text of the `.p8` file, including the BEGIN and END lines |

### 3. Sparkle update key

Download the latest [Sparkle release](https://github.com/sparkle-project/Sparkle/releases), unpack it, and run:

```bash
./bin/generate_keys
```

It prints a public key and stores the private key in your login keychain. Export the private key:

```bash
./bin/generate_keys -x sparkle-private-key.txt
```

- Paste the **public** key into [`Config/HyperIcon.xcconfig`](../Config/HyperIcon.xcconfig) as `SPARKLE_PUBLIC_KEY = ...` and commit it. It is not a secret.
- Add the contents of `sparkle-private-key.txt` as the secret `SPARKLE_ED_PRIVATE_KEY`, then delete the file.

Keep a backup of the private key. If it is lost, existing installs cannot verify future updates.

### 4. Add the secrets

In the repository: **Settings → Secrets and variables → Actions → New repository secret**, one for each of the seven names above. The release job stops with a clear message if any is missing.

### 5. Turn on the website

**Settings → Pages → Build and deployment → Source: GitHub Actions.** The site in `site/` deploys on every push to `main` that changes it. GitHub Pages and public release downloads need the repository to be public (or a paid plan for Pages on a private repository).

### Optional: your own bundle identifier

The app ships as `com.hypericon.app`. To use your own, change `PRODUCT_BUNDLE_IDENTIFIER` in `Config/HyperIcon.xcconfig` before the first release. Changing it later makes macOS treat the app as a different one.

## Cutting a release

```bash
git tag v0.1.0
```

```bash
git push origin v0.1.0
```

The tag sets the version number (`v0.1.0` → `0.1.0`); the build number is the workflow run number.

## Check before announcing

Do this on a Mac with the downloaded DMG. None of it can be verified by CI.

- [ ] The DMG opens without a Gatekeeper warning and the app launches after dragging to Applications.
- [ ] Picking a theme changes folder icons in Finder; switching themes replaces them.
- [ ] macOS asks for Desktop, Documents and Downloads access, and denying one does not break the others.
- [ ] A Git repository gets one icon and `git status` stays clean.
- [ ] **Restore Original Icons** returns every folder to how it was, including one you had customised by hand (with *Replace icons I set myself* on).
- [ ] After the second release: an older install offers the update.

## Replacing the website illustrations with real screenshots

The images in `site/assets/screenshot-*.png` are rendered from the page's live demo by `node tools/site/shots.js`. To use real captures, take these at 2x and save over the same file names (about 2160 px wide):

1. A Finder window in icon view with 15 to 20 varied folders, HyperIcon's menu open beside it, for each of: Synthwave '84, Sci-Fi HUD, Winter Holiday, Nineties Desktop.
2. Update the `alt` text in `site/index.html` and remove the "illustrations" note in `README.md`.
