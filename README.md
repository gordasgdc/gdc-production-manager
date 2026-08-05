# GDC Production Manager

[🇷🇴 Română](README.md) · [🇬🇧 English](README.en.md) · [🇪🇸 Español](README.es.md)

**Aplicație desktop, standalone, pentru gestionarea proiectelor de producție video.**
Fiecare utilizator o instalează pe propriul laptop; datele rămân locale, fără cloud.

---

## 📦 Descarcă și instalează

Ultima versiune e disponibilă în [Releases](https://github.com/gordasgdc/gdc-production-manager/releases).

| Platformă | Fișier | Instalare |
|---|---|---|
| **Mac** | `GDCProductionManager.pkg` | dublu-click → urmează instalatorul |
| **Windows** | `GDCProductionManager.exe` | dublu-click pentru a rula |

La prima pornire, aplicația deschide automat interfața într-un tab de browser local (`http://127.0.0.1:xxxx`) — nimic nu pleacă pe internet.

## 🚀 Caracteristici

- **Proiecte** cu tip (film, reclamă, nuntă, documentar, broadcast, videoclip muzical, corporate), locație de filmare, date de filmare/predare
- **Etape de lucru** clare: planificare → filmare → montaj → colorizare → review → final → predat, cu buton **"Next Step"** care avansează automat proiectul și o bară vizuală de tip "scope" pentru fiecare proiect
- **Notițe per etapă**: fiecare etapă (planificare, filmare, montaj...) are propriul câmp de notițe, păstrat separat
- **Monedă selectabilă** (EUR / RON) per proiect, curs sau produs — totalurile din dashboard sunt calculate separat pe fiecare monedă, nu amestecate
- **Clienți** cu date de contact și numărul de proiecte/cursuri asociate
- **Cursuri 1-la-1**: subiect, dată și oră, durată, preț, status plată, status curs (programat/confirmat/finalizat/anulat), locație (online/fizic)
- **Produse digitale**: DCTL-uri, PowerGrade, LUT-uri, presetări, șabloane — cu preț, versiune, compatibilitate, cale locală și link de descărcare
- **Căi de fișiere** pentru RAW, montaj și export final
- **Atașamente**: contracte, brief-uri sau referințe direct pe proiect
- **Facturare simplă**: buget total, sumă încasată, status plată
- **Panou general** cu statistici, notificări (termene apropiate, facturi neplătite), predări și cursuri apropiate
- **Calendar lunar** cu filmări și predări
- **Rapoarte PDF** per proiect (printare directă din aplicație)
- **Export/Import JSON** — backup și migrare între laptopuri
- **Temă light/dark**, comutabilă instant
- **Sincronizare opțională self-hosted** — între două instalări ale aplicației, fără server terț
- **Multi-utilizator local**: fiecare cont își are propriile date, pe același laptop
- **Interfață RO / EN / ES**
- **100% local și gratuit**, open-source (MIT)

## 🛠️ Cerințe tehnice / stack

- Backend: **Flask** + **SQLite** (prin SQLAlchemy)
- Frontend: HTML + CSS + JavaScript vanilla (fără build step)
- Distribuție: **PyInstaller** → `.app`/`.pkg` (Mac) și `.exe` (Windows)
- CI/CD: **GitHub Actions** (build automat la fiecare tag `v*`)

## 💻 Rulare din surse (pentru dezvoltare)

```bash
git clone https://github.com/gordasgdc/gdc-production-manager.git
cd gdc-production-manager
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python backend/app.py
```

Aplicația pornește un server local și deschide automat interfața în browser.

## 📁 Structura proiectului

```
gdc-production-manager/
├── .github/workflows/       # build-mac.yml, build-windows.yml
├── backend/                 # Flask: app.py, models.py, routes.py, auth.py, config.py
├── frontend/                # HTML/CSS/JS: dashboard, proiecte, clienți, autentificare
├── docs/                    # pagina de prezentare (GitHub Pages)
├── build/                   # fișiere .spec pentru PyInstaller
├── icon/                    # iconițe aplicație
├── requirements.txt
├── CHANGELOG.md
└── LICENSE
```

## 🏷️ Lansarea unei versiuni noi

Vezi [CHANGELOG.md](CHANGELOG.md) pentru istoric și pașii de mai jos pentru a publica un build nou:

```bash
git add .
git commit -m "Descriere modificări"
git push origin main

git tag -a v1.0.1 -m "Descriere versiune"
git push origin v1.0.1
```

> Notă importantă de Git: tag-ul se creează **după** `git push`, niciodată înainte —
> altfel Actions poate porni build-ul pe un commit care nu există încă pe remote.

GitHub Actions va porni automat build-urile pentru Mac și Windows și va publica pachetele în [Releases](https://github.com/gordasgdc/gdc-production-manager/releases).

## 👤 Autor

**Cristi Gordas (GDC)** — colorist și editor video

- [GitHub](https://github.com/gordasgdc)
- [Facebook](https://web.facebook.com/cristiGDC)
- [YouTube](https://www.youtube.com/@cristigordas)
- [resolvemaster.training](https://resolvemaster.training)

## 📄 Licență

MIT — vezi [LICENSE](LICENSE).
