# Changelog

All notable changes to GDC Production Manager are documented here.

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
