/**
 * Inkdesk visitor log.
 * Deployed as a Google Apps Script web app (Execute as: Me, Who has access: Anyone).
 * Each first visit adds a row to the "Inkdesk visitors" sheet and emails the owner.
 * Later visits update "Last visit" and "Visits".
 */
const SHEET_NAME = 'Visitors';
const HEADERS = ['Email', 'Name', 'First visit', 'Last visit', 'Visits', 'Device', 'Came from'];

function getSheet_() {
  const props = PropertiesService.getScriptProperties();
  const id = props.getProperty('SHEET_ID');
  let ss = null;
  if (id) { try { ss = SpreadsheetApp.openById(id); } catch (e) { ss = null; } }
  if (!ss) {
    ss = SpreadsheetApp.create('Inkdesk visitors');
    props.setProperty('SHEET_ID', ss.getId());
    const sh = ss.getSheets()[0];
    sh.setName(SHEET_NAME);
    sh.appendRow(HEADERS);
    sh.setFrozenRows(1);
    sh.getRange(1, 1, 1, HEADERS.length).setFontWeight('bold');
    sh.setColumnWidth(1, 240); sh.setColumnWidth(2, 160); sh.setColumnWidth(6, 260);
  }
  return ss.getSheetByName(SHEET_NAME) || ss.getSheets()[0];
}

/** Run once from the editor: creates the sheet and asks for permission. */
function setup() {
  const sh = getSheet_();
  Logger.log('Visitor sheet: ' + sh.getParent().getUrl());
}

// Stops a visitor's text from being treated as a spreadsheet formula.
function clean_(v, max) {
  let s = String(v == null ? '' : v).replace(/[\r\n\t]+/g, ' ').trim().slice(0, max);
  if (/^[=+\-@]/.test(s)) s = "'" + s;
  return s;
}

function doPost(e) {
  const lock = LockService.getScriptLock();
  lock.tryLock(10000);
  try {
    const d = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    const email = clean_(d.email, 200).toLowerCase();
    const name = clean_(d.name, 100);
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) return out_({ ok: false, error: 'email' });
    const sh = getSheet_();
    const now = new Date();
    const last = sh.getLastRow();
    const emails = last > 1 ? sh.getRange(2, 1, last - 1, 1).getValues().map(r => String(r[0]).toLowerCase()) : [];
    const idx = emails.indexOf(email);
    if (idx < 0) {
      sh.appendRow([email, name, now, now, 1, clean_(d.ua, 300), clean_(d.ref, 300)]);
      const owner = Session.getEffectiveUser().getEmail();
      if (owner) {
        MailApp.sendEmail({
          to: owner,
          subject: 'New Inkdesk visitor: ' + (name || email),
          body: (name || 'Someone') + ' (' + email + ') just opened Inkdesk for the first time.\n\n' +
                'Device: ' + clean_(d.ua, 300) + '\nCame from: ' + (clean_(d.ref, 300) || 'direct link') + '\n\n' +
                'All visitors: ' + sh.getParent().getUrl(),
        });
      }
      return out_({ ok: true, isNew: true });
    }
    const row = idx + 2;
    sh.getRange(row, 4).setValue(now);
    sh.getRange(row, 5).setValue((Number(sh.getRange(row, 5).getValue()) || 0) + 1);
    if (name && !sh.getRange(row, 2).getValue()) sh.getRange(row, 2).setValue(name);
    return out_({ ok: true, isNew: false });
  } catch (err) {
    return out_({ ok: false, error: String(err) });
  } finally {
    lock.releaseLock();
  }
}

function doGet() { return out_({ ok: true, service: 'inkdesk-visitors' }); }

function out_(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}
