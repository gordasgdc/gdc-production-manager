# GDC Production Manager

[🇷🇴 Română](README.md) · [🇬🇧 English](README.en.md) · [🇪🇸 Español](README.es.md)

**A standalone desktop app for managing video production projects.**
Each user installs it on their own laptop; data stays local, no cloud involved.

---

## 📦 Download & install

The latest version is available in [Releases](https://github.com/gordasgdc/gdc-production-manager/releases).

| Platform | File | Install |
|---|---|---|
| **Mac** | `GDCProductionManager.pkg` | double-click → follow the installer |
| **Windows** | `GDCProductionManager.exe` | double-click to run |

On first launch the app opens its interface in a local browser tab (`http://127.0.0.1:xxxx`) — nothing ever leaves your machine.

## 🚀 Features

- **Projects** with type (film, commercial, wedding, documentary, broadcast, music video, corporate), shoot location, shoot/delivery dates
- **Clear production stages**: planning → filming → editing → coloring → review → final → delivered, with a **"Next Step"** button that advances the project automatically, shown as a scope-style progress bar on every project
- **Per-stage notes**: every stage (planning, filming, editing…) keeps its own separate note field
- **Selectable currency** (EUR / RON) per project, course or product — dashboard totals are computed separately per currency, never mixed together
- **Clients** with contact details and linked project/course count
- **1-on-1 courses**: topic, date & time, duration, price, payment status, course status (scheduled/confirmed/completed/cancelled), location (online/in-person)
- **Digital products**: DCTLs, PowerGrades, LUTs, presets, templates — with price, version, compatibility, local path and download link
- **File paths** for RAW footage, edit, and final export
- **Attachments**: contracts, briefs or references right on a project
- **Per-project checklists** (pre-shoot, post-shoot, custom), with checkable items, progress tracking and reusable templates
- **Reminders** for deadlines, invoices and meetings, with a dashboard summary
- **Simple invoicing**: total budget, amount paid, payment status
- **Dashboard** with stats, notifications (upcoming deadlines, unpaid invoices), upcoming deliveries and courses
- **Monthly calendar** of shoots and deliveries
- **PDF reports** per project (print straight from the app)
- **Export/Import JSON** — backup and migration between laptops
- **Light/dark theme**, switchable instantly
- **Optional self-hosted sync** — between two installs of the app, no third-party server
- **Local multi-user**: each account keeps its own data on the same laptop
- **RO / EN / ES interface**
- **100% local and free**, open-source (MIT)

## 🛠️ Tech stack

- Backend: **Flask** + **SQLite** (via SQLAlchemy)
- Frontend: vanilla HTML + CSS + JavaScript (no build step)
- Packaging: **PyInstaller** → `.app`/`.pkg` (Mac) and `.exe` (Windows)
- CI/CD: **GitHub Actions** (automatic build on every `v*` tag)

## 💻 Running from source (development)

```bash
git clone https://github.com/gordasgdc/gdc-production-manager.git
cd gdc-production-manager
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python backend/app.py
```

The app starts a local server and opens the UI in your browser automatically.

## 📁 Project structure

```
gdc-production-manager/
├── .github/workflows/       # build-mac.yml, build-windows.yml
├── backend/                 # Flask: app.py, models.py, routes.py, auth.py, config.py
├── frontend/                # HTML/CSS/JS: dashboard, projects, clients, auth
├── docs/                    # presentation page (GitHub Pages)
├── build/                   # PyInstaller .spec files
├── icon/                    # app icons
├── requirements.txt
├── CHANGELOG.md
└── LICENSE
```

## 🏷️ Releasing a new version

See [CHANGELOG.md](CHANGELOG.md) for history, and the steps below to ship a new build:

```bash
git add .
git commit -m "Describe your changes"
git push origin main

git tag -a v1.0.1 -m "Version description"
git push origin v1.0.1
```

> Git note: create the tag **after** `git push`, never before —
> otherwise Actions may start building a commit that isn't on the remote yet.

GitHub Actions automatically builds Mac and Windows packages and publishes them to [Releases](https://github.com/gordasgdc/gdc-production-manager/releases).

## 👤 Author

**Cristi Gordas (GDC)** — colorist and video editor

- [GitHub](https://github.com/gordasgdc)
- [Facebook](https://web.facebook.com/cristiGDC)
- [YouTube](https://www.youtube.com/@cristigordas)
- [resolvemaster.training](https://resolvemaster.training)

## 📄 License

MIT — see [LICENSE](LICENSE).
