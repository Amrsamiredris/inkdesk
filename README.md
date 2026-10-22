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

## Visitor log
On the public site, first-time visitors enter their name and email (stored in their browser, sent once to a Google Apps Script web app in `tracking/Code.gs`). New visitors are added to the owner's "Inkdesk visitors" Google Sheet and trigger an email; return visits update "Last visit" and "Visits". 

## Build
`python3 build.py app.html path/to/node_modules` produces `index.html`, `vendor/` (self-hosted pdf.js, pdf-lib, JSZip, fonts and their licences) and `vercel.json` (security headers with a hash-based Content-Security-Policy).

## Privacy & security
- No third-party requests from visitors except the opt-in visitor log (Google Apps Script). Libraries and fonts are self-hosted.
- No cookies, analytics or ads. Local storage only for user-requested features (listed in `privacy.html`).
- Headers: CSP (hashed inline scripts, `frame-ancestors 'none'`), HSTS, nosniff, `X-Frame-Options: DENY`, strict referrer, Permissions-Policy, COOP/CORP.
- `privacy.html`, `terms.html`, `licenses.html`, `.well-known/security.txt`.
