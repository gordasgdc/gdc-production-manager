# Changelog

All notable changes to GDC Production Manager are documented here.

## v2.0.1 (2026-09-04) — Integrare completă cu ecosistemul GDC Plugin Manager

### Added
- Profil + ID de mașină, deja vizibile în meniul lateral (v2.0.0), acum
  complet integrate cu ecosistemul: verificare de revocare a licenței
  (online, opțională — o licență deja activată nu se blochează niciodată
  doar pentru că ești offline) și preț dinamic (fără să mai fie nevoie de
  o actualizare a aplicației doar pentru o schimbare de preț/ofertă).
- Aplicația e acum vizibilă cu preț propriu în catalogul GDC Plugin
  Manager.

## v2.0.0 (2026-09-04) — Arhitectură nativă & pipeline configurabil

Versiune majoră: fereastră nativă (nu mai deschide browser-ul de sistem)
și pipeline de producție complet configurabil, în loc de listele fixe de
până acum.

### Added
- **Fereastră nativă** — aplicația nu mai deschide un tab de browser;
  rulează într-o fereastră proprie, fără bară de adresă.
- **Tipuri de proiect și etape configurabile** — adaugă, redenumește,
  dezactivează sau reordonează-le liber din Setări. Linie de progres
  interactivă (click direct pe orice etapă) pe fiecare proiect, cu istoric
  complet, needitabil, al fiecărei avansări.
- **Clienți**: tip explicit (persoană fizică / contact neoficial, pe lângă
  firmele deja existente), CNP opțional, marcaj vizibil de atenționare
  (client/proiect) cu notiță.
- **Financiar**: rest de plată calculat automat pe fiecare proiect, monedă
  USD adăugată, status „Avans" nou.
- **Checklist-uri**: aplicate automat la crearea unui proiect, după tipul
  lui; itemele pot fi legate de un echipament din inventar (autocompletare).
- **Echipament**: status „Subînchiriat" nou; predarea/returnarea
  înregistrează starea reală (OK / lipsă / avariat) — un echipament avariat
  trece automat în mentenanță, unul lipsă e semnalat vizibil, în loc să
  rămână blocat silențios „în teren".
- **Buton „Deschide folderul"** lângă fiecare cale de fișiere (RAW/Montaj/
  Export), pe lângă selectorul de directoare deja existent.
- **Profil și ID de mașină vizibile direct în meniul lateral**, nu doar în
  Setări.

## v1.2.4 (2026-08-26)

### Added
- Pop-up modal (nu doar bannerul discret existent) la detectarea automată
  a unei versiuni noi la lansare — cerință explicită, Directivă Permanentă
  Supremă ("verificator + notificare vizibilă"). Dismissal per-versiune,
  cuplat cu bannerul (închiderea unuia ascunde și pe celălalt).

## v1.2.3 (2026-08-26)

### Fixed (audit secvențial — release-ul v1.2.2 nu conținea fix-ul din cod)
- Release-ul live `v1.2.2` fusese tăiat înainte de commit-ul care elimina
  `Instalare_GDCProductionManager.command` — verificat direct (`unzip -l`
  pe arhiva descărcată), nu presupus. `v1.2.3` conține fix-ul real.
- Cele 3 ghiduri PDF separate (RO/EN/ES) combinate într-un singur
  `Instructiuni_Utilizare.pdf` (27 pagini) — arhiva Mac respectă acum
  strict "3 fișiere la rădăcină" (pkg + uninstaller + 1 PDF).
- Versiune sincronizată la `1.2.3` (`backend/config.py` + `docs/update.json`).

## [Unreleased]

### Fixed (2026-08-25, audit "Directivă Permanentă Supremă")
- Eliminat `Instalare_GDCProductionManager.command` (hack Gatekeeper/quarantine inutil — pachetul e deja semnat+notarizat+stapled).
- Curățare de versiune veche mutată corect într-un `installer/scripts/preinstall` (fără hack-uri de quarantine).
- Uninstaller mutat la rădăcina arhivei Mac (era în subfolder), redenumit `Dezinstalare_GDCProductionManager.command`.
- Site (RO/EN/ES) actualizat: dublu-click direct pe `.pkg`.
- Restul checklist-ului (versiune în UI, update checker, sincronizare `update.json`) era deja conform — verificat, nu presupus.

### Added
- Checklist progress bar (percentage + X/Y count) on every checklist
- Per-checklist PDF export via a dedicated print-friendly page
- 4 default checklist templates seeded automatically for every new account (Pre/Post-filmare Nuntă, Pre/Post-filmare Reclamă), each taggable with a best-fit project type; fully editable/deletable like any other template
- Calendar export (.ics) combining reminders, upcoming courses, and project delivery dates — importable into Apple Calendar, Outlook, Google Calendar
- In-app pop-up notifications: checked on load and every 15 minutes for upcoming/overdue deadlines, outstanding payments, and reminders due within 3 days; shown as in-app toasts plus native browser notifications when permission is granted
- **Checklists & reminders module**: per-project checklists (pre-shoot / post-shoot / custom) with checkable items, "mark all", and reusable templates managed from Settings; standalone reminders (deadlines, invoices, meetings) with a dedicated page and a dashboard summary
- Fixed a SQLAlchemy JSON-column persistence bug where in-place mutation of nested checklist items could silently fail to save (checklist toggling, "mark all", and item add/remove now deep-copy before mutating)
- **Courses module**: 1-on-1 training sessions with topic, date/time, duration, price, payment status, course status, and location; linked to clients
- **Digital products module**: DCTLs, PowerGrades, LUTs, presets and templates, with price, version, compatibility, file path and download link
- **Selectable currency (EUR/RON)** per project, course and product, with a default set per user account; dashboard totals are tracked separately per currency rather than mixed together
- **"Next Step" button** to advance a project to the next pipeline stage in one click
- **Per-stage notes** on projects — each pipeline stage keeps its own note
- Dashboard: courses this week, total courses, total products, course revenue (current month, per currency), product revenue (total, per currency), upcoming courses
- Calendar page: monthly view of shoots and deliveries
- Settings page: theme, data export/import, and self-hosted sync configuration
- Light/dark theme toggle, persisted per account
- Notifications for upcoming/overdue deadlines and outstanding payments
- Project attachments (contracts, briefs, references) stored locally per project
- Export/Import full data snapshot as JSON
- Optional self-hosted sync between two instances of the app (push/pull, shared-secret token)
- Per-project PDF report (print-to-PDF from a dedicated print-friendly page)
- Presentation site (`docs/index.html`) redesigned: hero, about, features, how-it-works, roadmap, download, footer — RO/EN/ES, responsive, scroll-reveal animations

## [1.0.0] — Unreleased

First public version.

### Added
- Local Flask + SQLite backend, packaged as a standalone desktop app (Mac `.pkg`, Windows `.exe`)
- Local multi-user accounts (one installed copy, separate data per account)
- Projects: type, status pipeline (planning → filming → editing → coloring → review → final → delivered), shoot location, shoot/delivery dates, RAW/edit/export file paths, budget & payment tracking, notes
- Clients: contact info, linked project count
- Dashboard: totals, per-stage breakdown, outstanding balance, upcoming deliveries
- RO / EN / ES interface
- GitHub Actions workflows for automated Mac and Windows builds on tag push
- GitHub Pages presentation site (`docs/index.html`)
