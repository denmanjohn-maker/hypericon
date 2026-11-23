# Making a theme

A theme is a folder containing a manifest and one PNG per folder type.

```
my-theme/
  theme.json
  preview.png      (optional, shown in the menu; 3:2 works best)
  folder.png       (required)
  git.png
  documents.png
  ...
```

Put the folder in `~/Library/Application Support/HyperIcon/Themes/` (Settings → **Open My Themes Folder**), then choose **Rescan Folders** from the menu. A theme with the same `id` as a bundled one replaces it.

## theme.json

```json
{
  "id": "my-theme",
  "name": "My Theme",
  "group": "Custom",
  "description": "One line shown as a tooltip.",
  "accent": "#ff62a6"
}
```

`id` and `name` are required. `id` should match the folder name.

## Icons

- PNG with transparency, square, 512×512 or 1024×1024.
- Leave a little empty space around the artwork, as Finder's own folder does.
- Only `folder.png` is required. Any type you leave out falls back to it.

| File | Used for |
| --- | --- |
| `folder` | Anything not matched below |
| `git` | Git repositories |
| `xcode`, `node`, `python`, `rust`, `go`, `java`, `dotnet` | Projects in that language or toolchain |
| `docker`, `kubernetes`, `terraform`, `ci` | Container, Helm/Kustomize, Terraform and pipeline folders |
| `documents`, `spreadsheets`, `presentations`, `pdf` | Office files |
| `images`, `music`, `video` | Media |
| `code`, `archives`, `fonts`, `books`, `design`, `data`, `web` | Other majority types |

The full list is also in [`Themes/categories.json`](../Themes/categories.json).

## Adding a bundled theme

Bundled themes are generated, not drawn by hand. In [`tools/icongen/gen.py`](../tools/icongen/gen.py):

1. Write a function that returns the SVG for one category by calling `compose(...)` with your folder colours, decorations and glyph colour. The existing themes are short examples.
2. Add an entry to `THEMES`.
3. Rebuild and check:

```bash
python3 tools/icongen/gen.py my-theme
```

```bash
python3 tools/check_themes.py
```

```bash
python3 tools/site/build.py
```

Glyphs are shared by every theme and live in [`tools/icongen/glyphs.py`](../tools/icongen/glyphs.py). Keep new artwork original: no vendor logos and no copies of another operating system's icons.
