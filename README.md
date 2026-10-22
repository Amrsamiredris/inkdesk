# Inkdesk

Private, in-browser PDF editor. Edit existing text, sign, comment, highlight, draw, whiteout, add images, fill forms, merge and rotate.

Everything runs in the browser with [pdf.js](https://github.com/mozilla/pdf.js) (rendering) and [pdf-lib](https://github.com/Hopding/pdf-lib) (writing). No file is uploaded to any server.

Single static file: `index.html`. Deploy anywhere that serves static files (Vercel, GitHub Pages).

## Known limits
- Edited text and whiteout cover the original; the old content stays in the file underneath.
- Edited lines use the standard PDF fonts (Helvetica, Times, Courier).
- Arabic and other non-Latin text you add is saved as an image.
- Password-protected or restricted PDFs are not supported.
