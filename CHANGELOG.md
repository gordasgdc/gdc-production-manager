# Changelog

All notable changes to GDC Production Manager are documented here.

## [Unreleased]

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
