# Icons

`icon.svg` is the master icon (red-to-teal "G" mark on dark background,
matching the app's tally/scope color palette).

Before your first tagged build, generate the platform-specific files the
PyInstaller specs expect — `icon.icns` (Mac) and `icon.ico` (Windows). The
GitHub Actions workflows read them from this folder at build time, so they
need to exist in the repo (they're small, safe to commit).

## Quickest path — one online converter
Upload `icon.svg` (or a 1024×1024 PNG export of it) to any SVG→ICO/ICNS
converter (e.g. cloudconvert.com, icoconvert.com) and save the results here
as `icon.icns` and `icon.ico`.

## From macOS (no extra tools needed)
```bash
# 1) Export icon.svg to icon.png at 1024x1024 (Preview, Figma, or:
#    qlmanage -t -s 1024 -o . icon.svg   then rename the .png)

mkdir icon.iconset
sips -z 16 16     icon.png --out icon.iconset/icon_16x16.png
sips -z 32 32     icon.png --out icon.iconset/icon_16x16@2x.png
sips -z 32 32     icon.png --out icon.iconset/icon_32x32.png
sips -z 64 64     icon.png --out icon.iconset/icon_32x32@2x.png
sips -z 128 128   icon.png --out icon.iconset/icon_128x128.png
sips -z 256 256   icon.png --out icon.iconset/icon_128x128@2x.png
sips -z 256 256   icon.png --out icon.iconset/icon_256x256.png
sips -z 512 512   icon.png --out icon.iconset/icon_256x256@2x.png
sips -z 512 512   icon.png --out icon.iconset/icon_512x512.png
sips -z 1024 1024 icon.png --out icon.iconset/icon_512x512@2x.png
iconutil -c icns icon.iconset -o icon.icns
rm -rf icon.iconset
```

## From any platform with Python + Pillow
```bash
pip install pillow cairosvg
python - <<'PY'
import cairosvg
cairosvg.svg2png(url="icon.svg", write_to="icon.png", output_width=1024, output_height=1024)

from PIL import Image
img = Image.open("icon.png")
img.save("icon.ico", sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])
PY
```

Until `icon.icns` / `icon.ico` exist, you can still build locally — just
remove the `icon=` line from the relevant `.spec` file and PyInstaller will
use its default icon.
