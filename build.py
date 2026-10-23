#!/usr/bin/env python3
"""Build the hosted Inkdesk site from the app source.

Usage: python3 build.py path/to/app.html [path/to/node_modules]

- Rewrites CDN script/font URLs to self-hosted copies in vendor/ (no third-party requests from visitors).
- Adds the document shell, theme metas, visitor-log URL and a Content-Security-Policy.
- Writes vercel.json with security headers, including CSP hashes for the inline scripts.
"""
import base64, hashlib, json, pathlib, re, shutil, sys

ROOT = pathlib.Path(__file__).parent
SRC = pathlib.Path(sys.argv[1])
NM = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else None
TRACK_URL = "https://script.google.com/macros/s/AKfycbx8fWvtcVMmNUUbSDuC4tkJj6-bCeEsOdjByRtMTRT_pj53zoM7oP44UlIgcg8pu18-ew/exec"

app = SRC.read_text()

# 1. self-hosted libraries and fonts
REPL = {
    "https://cdn.jsdelivr.net/npm/pdfjs-dist@4.10.38/build/pdf.min.mjs": "./vendor/pdf.min.mjs",
    "https://cdn.jsdelivr.net/npm/pdfjs-dist@4.10.38/build/pdf.worker.min.mjs": "./vendor/pdf.worker.min.mjs",
    "https://cdn.jsdelivr.net/npm/pdf-lib@1.17.1/dist/pdf-lib.min.js": "vendor/pdf-lib.min.js",
    "https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js": "vendor/jszip.min.js",
    "https://cdn.jsdelivr.net/npm/@neslinesli93/qpdf-wasm@0.3.0/dist/qpdf.js": "vendor/qpdf/qpdf.js",
    "https://cdn.jsdelivr.net/npm/@neslinesli93/qpdf-wasm@0.3.0/dist/qpdf.wasm": "vendor/qpdf/qpdf.wasm",
}
REPL["const LO_BASE = 'https://cdn.jsdelivr.net/npm/@bentopdf/libreoffice-wasm@2.3.1/assets/';"] = "const LO_BASE = 'vendor/lo/';"
REPL["const LO_MIRRORS = [];"] = "const LO_MIRRORS = ['https://amrsamiredris.github.io/inkdesk/vendor/lo/'];"
for a, b in REPL.items():
    assert a in app, a
    app = app.replace(a, b)
# pdf.js worker path must resolve against the page, not the module
app = app.replace("pdfjsLib.GlobalWorkerOptions.workerSrc = './vendor/pdf.worker.min.mjs';",
                  "pdfjsLib.GlobalWorkerOptions.workerSrc = new URL('vendor/pdf.worker.min.mjs', document.baseURI).href;")
app = re.sub(r'<link rel="preconnect"[^>]*>\n?', '', app)
app = re.sub(r'<link rel="stylesheet" href="https://fonts.googleapis.com/[^"]+">', '<link rel="stylesheet" href="vendor/fonts/fonts.css">', app)
assert 'fonts.googleapis' not in app and 'cdn.jsdelivr' not in app and 'cdnjs' not in app

if NM:
    v = ROOT / 'vendor'; (v / 'fonts').mkdir(parents=True, exist_ok=True)
    shutil.copy(NM / 'pdfjs-dist/build/pdf.min.mjs', v)
    shutil.copy(NM / 'pdfjs-dist/build/pdf.worker.min.mjs', v)
    shutil.copy(NM / 'pdf-lib/dist/pdf-lib.min.js', v)
    shutil.copy(NM / 'jszip/dist/jszip.min.js', v)
    LO_PKG = pathlib.Path(sys.argv[3]) if len(sys.argv) > 3 else None
    if LO_PKG:
        (v / 'lo').mkdir(exist_ok=True)
        for fn in ['soffice.js', 'soffice.worker.js', 'browser.worker.global.js', 'soffice.wasm.gz', 'soffice.data.gz']:
            shutil.copy(LO_PKG / fn, v / 'lo' / fn)
    (v / 'qpdf').mkdir(exist_ok=True)
    shutil.copy(NM / '@neslinesli93/qpdf-wasm/dist/qpdf.js', v / 'qpdf')
    shutil.copy(NM / '@neslinesli93/qpdf-wasm/dist/qpdf.wasm', v / 'qpdf')
    faces = [('Sacramento', 'sacramento', [400]), ('Great Vibes', 'great-vibes', [400]), ('Dancing Script', 'dancing-script', [600]),
             ('Caveat', 'caveat', [600]), ('IBM Plex Sans Arabic', 'ibm-plex-sans-arabic', [400, 600])]
    css = ['/* Self-hosted fonts (SIL Open Font License 1.1). */']
    for fam, pkg, weights in faces:
        subsets = ['latin', 'arabic'] if pkg == 'ibm-plex-sans-arabic' else ['latin']
        for w in weights:
            for sub in subsets:
                fn = f'{pkg}-{sub}-{w}-normal.woff2'
                shutil.copy(NM / '@fontsource' / pkg / 'files' / fn, v / 'fonts' / fn)
                rng = 'U+0600-06FF,U+0750-077F,U+0870-088E,U+0890-0891,U+0898-08E1,U+08E3-08FF,U+200C-200E,U+2010-2011,U+204F,U+2E41,U+FB50-FDFF,U+FE70-FE74,U+FE76-FEFC' if sub == 'arabic' else 'U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD'
                css.append(f"@font-face{{font-family:'{fam}';font-style:normal;font-weight:{w};font-display:swap;src:url('{fn}') format('woff2');unicode-range:{rng}}}")
    (v / 'fonts' / 'fonts.css').write_text('\n'.join(css) + '\n')
    # third-party license texts
    lic = ROOT / 'vendor' / 'LICENSES'; lic.mkdir(exist_ok=True)
    shutil.copy(NM / 'pdfjs-dist/LICENSE', lic / 'pdfjs-dist-Apache-2.0.txt')
    shutil.copy(NM / 'pdf-lib/LICENSE.md', lic / 'pdf-lib-MIT.txt')
    shutil.copy(NM / 'jszip/LICENSE.markdown', lic / 'jszip-MIT-or-GPLv3.txt')
    shutil.copy(NM / '@fontsource/sacramento/LICENSE', lic / 'fonts-OFL-1.1.txt')
    (lic / 'libreoffice-MPL-2.0.txt').write_text(
        "LibreOffice (https://www.libreoffice.org), copyright The Document Foundation and contributors,\n"
        "is licensed under the Mozilla Public License 2.0: https://www.mozilla.org/MPL/2.0/\n"
        "Source code: https://git.libreoffice.org/core\n\n"
        "The WebAssembly build used here is @bentopdf/libreoffice-wasm 2.3.1 (MPL-2.0), unmodified:\n"
        "https://www.npmjs.com/package/@bentopdf/libreoffice-wasm\n")
    (lic / 'qpdf-Apache-2.0.txt').write_text(
        "qpdf 12.2.0 (https://github.com/qpdf/qpdf), copyright Jay Berkenbilt and contributors,\n"
        "is licensed under the Apache License, Version 2.0: https://www.apache.org/licenses/LICENSE-2.0\n\n"
        "The WebAssembly build is from qpdf-wasm (https://github.com/neslinesli93/qpdf-wasm), licensed under the ISC License.\n"
        "It is used unmodified.\n")

# 2. Content-Security-Policy with hashes of the inline scripts
track_js = f'window.INKDESK_TRACK={json.dumps(TRACK_URL)};'
inline = [track_js] + re.findall(r'<script type="module">([\s\S]*?)</script>', app)
hashes = ' '.join("'sha256-%s'" % base64.b64encode(hashlib.sha256(x.encode()).digest()).decode() for x in inline)
csp = ("default-src 'self'; script-src 'self' 'wasm-unsafe-eval' " + hashes + "; worker-src 'self' blob:; "
       "connect-src 'self' blob: https://script.google.com https://script.googleusercontent.com https://amrsamiredris.github.io; "
       "img-src 'self' data: blob:; font-src 'self' data:; style-src 'self' 'unsafe-inline'; "
       "object-src 'none'; base-uri 'self'; form-action 'none'; manifest-src 'self'")

head = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta http-equiv="Content-Security-Policy" content="{csp}; upgrade-insecure-requests">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta name="color-scheme" content="light dark">
<meta name="theme-color" content="#F5F5F7" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#000000" media="(prefers-color-scheme: dark)">
<meta name="description" content="Edit, sign, comment on and fill PDFs in your browser. Files never leave your device.">
<style>:root{{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}body{{margin:0}}img{{max-width:100%}}</style>
<script>{track_js}</script>
</head>
<body>
'''
(ROOT / 'index.html').write_text(head + app + '\n</body>\n</html>\n')

# 3. Security headers (Vercel). GitHub Pages can't set headers, so it relies on the CSP meta tag above.
headers = [
    {"key": "Content-Security-Policy", "value": csp + "; frame-ancestors 'none'; upgrade-insecure-requests"},
    {"key": "Strict-Transport-Security", "value": "max-age=63072000; includeSubDomains; preload"},
    {"key": "X-Content-Type-Options", "value": "nosniff"},
    {"key": "X-Frame-Options", "value": "DENY"},
    {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"},
    {"key": "Permissions-Policy", "value": "camera=(), microphone=(), geolocation=(), payment=(), usb=(), serial=(), hid=(), browsing-topics=()"},
    {"key": "Cross-Origin-Opener-Policy", "value": "same-origin"},
    {"key": "Cross-Origin-Resource-Policy", "value": "same-site"},
    {"key": "Cross-Origin-Embedder-Policy", "value": "require-corp"},
]
# The LibreOffice engine's worker scripts need eval (Emscripten embind); allow it only for those files.
lo_csp = ("default-src 'self'; script-src 'self' 'unsafe-eval' 'wasm-unsafe-eval' blob:; worker-src 'self' blob:; "
          "connect-src 'self' blob: https://amrsamiredris.github.io; object-src 'none'; base-uri 'self'")
lo_headers = [h for h in headers if h["key"] != "Content-Security-Policy"] + [{"key": "Content-Security-Policy", "value": lo_csp}]
cfg = {
    "cleanUrls": False,
    "headers": [
        {"source": "/((?!vendor/lo/).*)", "headers": headers},
        {"source": "/vendor/lo/(.*)", "headers": lo_headers},
        {"source": "/vendor/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=31536000, immutable"}]},
    ],
}
(ROOT / 'vercel.json').write_text(json.dumps(cfg, indent=2) + '\n')
print('built index.html, vercel.json; inline scripts hashed:', len(inline))
