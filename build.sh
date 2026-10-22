#!/bin/bash
# Wraps the app source (artifact form, no <html> shell) into a full page for static hosting.
# Usage: ./build.sh path/to/app.html > index.html
TRACK_URL="https://script.google.com/macros/s/AKfycbx8fWvtcVMmNUUbSDuC4tkJj6-bCeEsOdjByRtMTRT_pj53zoM7oP44UlIgcg8pu18-ew/exec"
printf '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n<meta name="color-scheme" content="light dark">\n<meta name="theme-color" content="#F5F5F7" media="(prefers-color-scheme: light)">\n<meta name="theme-color" content="#000000" media="(prefers-color-scheme: dark)">\n<meta name="description" content="Edit, sign, comment on and fill PDFs in your browser. Files never leave your device.">\n<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%%}</style>\n<script>window.INKDESK_TRACK=%s;</script>\n</head>\n<body>\n' "\"$TRACK_URL\""
cat "$1"
printf '\n</body>\n</html>\n'
