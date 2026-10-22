# Inkdesk

Private, in-browser PDF editor. Nothing is uploaded: rendering uses [pdf.js](https://github.com/mozilla/pdf.js), writing uses [pdf-lib](https://github.com/Hopding/pdf-lib).

Live: https://inkdesk-iota.vercel.app

## Tools
- **Edit**: edit existing text, add text, images, whiteout, fill forms
- **Review**: real PDF comments, highlight / underline / strikeout, freehand draw, shapes (box, ellipse, line, arrow), stamps (Approved, Paid…, ✔ ✘ ●, today's date)
- **Sign**: draw, type or upload a signature, saved on your device
- **Redact**: covered content is removed; redacted pages are rebuilt as images
- **Pages**: merge, organize (reorder, rotate, delete, insert blank), extract, split to separate files
- **Download options**: flatten forms, page numbers, watermark, strip document info
- **Find** (Ctrl+F) and Acrobat-style keyboard shortcuts (press `?` in the editor)

## Known limits
- Edited text and whiteout cover the original; use Redact to remove content.
- Edited lines use the standard PDF fonts (Helvetica, Times, Courier).
- Arabic and other non-Latin text you add is saved as an image.
- Password-protected or restricted PDFs are not supported.
- Not built: compress, conversion to/from Office, OCR, PDF/A, password protection, certificate signatures.
