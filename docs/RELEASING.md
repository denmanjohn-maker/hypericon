# Releasing HyperIcon

Pushing a version tag runs [`.github/workflows/release.yml`](../.github/workflows/release.yml), which:

1. Builds a universal Release build.
2. Signs it with your **Developer ID Application** certificate (hardened runtime).
3. Notarizes and staples the app, builds `HyperIcon.dmg`, then signs, notarizes and staples the disk image.
4. Publishes a GitHub release with `HyperIcon.dmg`, its checksum and `restore-icons.sh`.

HyperIcon does not update itself. People get new versions by downloading the latest DMG from the Releases page.

## One-time setup

You do these once, on a Mac, with your Apple Developer account.

### 1. Developer ID certificate

1. In Xcode: **Settings → Accounts → your team → Manage Certificates → + → Developer ID Application**.
2. Open **Keychain Access**, choose the **My Certificates** category, and find *Developer ID Application: Your Name (TEAMID)*. It must have a private key under it when expanded. Right-click the certificate → **Export**, save as `developer-id.p12` and set a password. Exporting from the plain *Certificates* category, or exporting an *Apple Development* certificate, produces a file the release cannot sign with.
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

### 3. Add the secrets

In the repository: **Settings → Secrets and variables → Actions → New repository secret**, one for each of the six names above. If you added `SPARKLE_ED_PRIVATE_KEY` earlier, it is no longer used and can be deleted. The release job stops with a clear message if any is missing.

### 4. Turn on the website

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

## Replacing the website illustrations with real screenshots

The images in `site/assets/screenshot-*.png` are rendered from the page's live demo by `node tools/site/shots.js`. To use real captures, take these at 2x and save over the same file names (about 2160 px wide):

1. A Finder window in icon view with 15 to 20 varied folders, HyperIcon's menu open beside it, for each of: Synthwave '84, Sci-Fi HUD, Winter Holiday, Nineties Desktop.
2. Update the `alt` text in `site/index.html` and remove the "illustrations" note in `README.md`.
