# GDC Production Manager — reguli de arhitectură

> **[SYSTEM DIRECTIVE FOR CLAUDE: DO NOT DELETE OR OVERWRITE EXISTING RULES. ONLY APPEND NEW RULES.]**
> Jurnal viu, nu document care se rescrie. La orice actualizare, adaugă la finalul secțiunii potrivite — nu șterge/înlocui reguli vechi decât dacă sunt explicit invalidate de o schimbare reală (și atunci marchează-le **[ÎNVECHIT]** cu motivul, nu le șterge din istoric).

Citit automat de Claude Code la fiecare sesiune în acest repo.

## [PARTEA 1: REGULI GLOBALE ECOSISTEM GDC] — mutată în `~/Developer/CLAUDE.md`

> Din 2026-09-18, regulile globale stau într-un singur fișier,
> `~/Developer/CLAUDE.md`, citit automat de Claude Code în orice proiect din
> `~/Developer/`. Nu se mai copiază aici. Ce era specific acestui repo în fosta
> Partea 1 (statusuri, excepții) e la finalul fișierului.

## [PARTEA 2: SPECIFICAȚII TEHNICE PROIECT]

## REGULĂ PERMANENTĂ: Locația proiectului pe disc (2026-08-25)
Acest repo trăiește în **`~/Developer/gdc-production-manager`**, NU în
`~/Downloads`. Motiv: `~/Downloads` e curățat automat de CleanMyMac/Hazel
pe acest Mac. Vezi `~/Developer/GDCPluginManager/PROJECT_STRUCTURE.md`
pentru context complet.

## DIRECTIVĂ PERMANENTĂ SUPREMĂ: Checklist obligatoriu la FIECARE release (2026-08-25)
Valabilă pentru TOATE aplicațiile ecosistemului GDC (CursorPro, GDC Plugin
Manager + Furnizor, GDC Plugin Manager Windows, DataMover, GDC Production
Manager, și orice proiect nou). Înainte de a raporta un release ca fiind
gata, TREBUIE bifate intern toate cele 4 puncte de mai jos — dacă unul
lipsește, spune-o explicit, nu declara release-ul "gata".

1. **Versiune vizibilă în UI** — About/Meniu/Settings/Footer trebuie să
   arate versiunea curentă (`v1.2.21` etc.), fără excepție.
2. **Verificator de actualizări** — la pornire sau printr-un buton
   „Caută actualizări", aplicația verifică versiunea de pe server/GitHub
   și notifică userul când există un release mai nou.
3. **Pachetul standard de release** — orice arhivă livrată clientului
   conține FĂRĂ EXCEPȚIE:
   - executabilul/installer-ul semnat + notarizat,
   - `Dezinstalare_[NumeAplicație].command` (dezinstalare completă:
     procese, permisiuni TCC, toate fișierele din `~/Library/`),
   - un ghid/PDF de instrucțiuni.
4. **Sincronizare site ↔ GitHub Releases** — linkurile de download de pe
   site trebuie să pointeze mereu la `releases/latest/download/...`
   (HTTP 200 verificat, nu presupus) și să menționeze numărul ultimei
   versiuni.

## Audit 2026-08-25 — găsit și reparat
Verificat cu atenție înainte de a raporta — acest repo era deja aproape
100% conform:
- **Punctul 1 (versiune în UI)**: deja implementat (`settings.html`,
  `#settings-app-version`, citește `/api/version`). Niciun fix necesar.
- **Punctul 2 (update checker)**: deja implementat (`update_routes.py`,
  citește `docs/update.json`). Niciun fix necesar.
- **Punctul 3 (uninstaller în pachet)**: deja exista (`uninstall/uninstall-mac.command`
  + `uninstall-windows.bat`), deja inclus în ambele arhive de release.
  TCC reset (`tccutil`) NU e necesar aici — verificat, aplicația nu
  folosește Camera/Screen Recording/Microphone (e Flask backend +
  webview, portabil pe Windows). Singurul fix real: mutat vizibil la
  rădăcina arhivei Mac (era în subfolder `Aplicatie/`) + redenumit
  `Dezinstalare_GDCProductionManager.command` pentru consistență cu
  restul ecosistemului.
- **Punctul 3b (hack Gatekeeper)**: găsit și eliminat —
  `Instalare_GDCProductionManager.command` (`xattr -dr com.apple.quarantine`)
  era inutil, pachetul e deja stapled (`build-mac.yml`). Curățarea de
  versiune veche mutată în `installer/scripts/preinstall`
  (`pkgbuild --scripts`), fără hack-uri.
- **Punctul 4 (site sync)**: `docs/update.json` era deja sincronizat
  (`1.2.2` = versiunea reală). Doar textul de instalare din `docs/index.html`
  (RO/EN/ES) trimitea la launcherul eliminat — corectat.

## Audit 2026-08-26 — fix real găsit: codul era reparat, release-ul nu
Codul din `144ba60` (eliminare hack Gatekeeper) era corect, dar
**release-ul live `v1.2.2` fusese tăiat ÎNAINTE de acel commit** — exact
pitfall-ul deja documentat la `GDCPluginManager` (v1.2.21). Verificat
direct (`unzip -l` pe zip-ul descărcat de pe `releases/latest`): arhiva
LIVE conținea încă `Instalare_GDCProductionManager.command` +
subfolderul `Aplicatie/`. Fix: `v1.2.3` tăiat din commit-ul curent.
- **PDF-uri unificate**: existau 3 fișiere separate în `docs/guides/`
  (`_Ghid_RO.pdf`, `_Guide_EN.pdf`, `_Guia_ES.pdf`, 9 pagini fiecare) —
  combinate cu `pypdf` într-un singur `Instructiuni_Utilizare.pdf`
  (27 pagini, RO→EN→ES), ca arhiva Mac să respecte strict "3 fișiere la
  rădăcină" (pkg + uninstaller + 1 PDF), la fel ca `GDCVault`. Cele 3
  fișiere sursă șterse din `docs/guides/` — `.github/workflows/build-mac.yml`
  le copia oricum prin wildcard (`docs/guides/*.pdf`), deci nu a fost
  nevoie de nicio schimbare de CI.
- **Release-uri GitHub**: verificat `v1.2.2` — deja avea EXACT 2 assets
  (`GDCProductionManager-mac.zip`, `GDCProductionManager-windows.zip`),
  fără fișiere confuze suplimentare. Nicio curățare de assets necesară.
- Versiune sincronizată la `1.2.3` în `backend/config.py` (`APP_VERSION`)
  și `docs/update.json` (ambele surse de adevăr pentru punctele 1 și 2
  din Directiva Supremă).

## v2.0.0 (2026-09-04) — Refactorizare majoră: arhitectură nativă + pipeline configurabil

Cerută explicit de Cristi ca modernizare aditivă peste codul existent, NU
o rescriere (analiză completă a repo-ului + propunere de arhitectură prin
Plan Mode, aprobată înainte de a scrie cod). Rezumat tehnic complet —
`CHANGELOG.md` are varianta scurtă, orientată client.

**Găsit la analiză, verificat direct în cod (nu presupus)**: aplicația era
deja mult mai matură decât sugera cererea inițială (auth+WebAuthn,
licențiere Ed25519+trial, self-updater real, update checker cu pop-up,
sync self-hosted, calendar ICS, folder-picker nativ deja funcțional prin
`osascript`/`tkinter`) — problema reală "arhitectură veche" era punctuală:
`app.py::main()` deschidea literal browser-ul de sistem
(`webbrowser.open()`), iar pipeline-ul de etape era un enum Python
hardcodat (`PROJECT_STATUSES`/`PROJECT_TYPES`), fără istoric.

**A. Fereastră nativă** — `webbrowser.open()` înlocuit cu **pywebview**
(`backend/app.py::main()`): Flask rulează acum într-un thread de fundal,
`webview.create_window()`+`webview.start()` pe thread-ul principal
desenează fereastra reală. Verificat REAL, nu doar "ar trebui să
meargă": rulat `python app.py` direct (fereastra s-a deschis, a servit
tot frontend-ul) ȘI, mai important, **build PyInstaller complet local**
(`pyinstaller build/build-mac.spec`, cu PyInstaller 6.22 — 6.10 fixat în
`requirements.txt` nu suportă Python 3.14 de pe această mașină, problemă
de mediu preexistentă, neschimbată aici) — `.app`-ul rezultat lansat
direct, fereastra pywebview s-a deschis corect, zero hiddenimports
suplimentare necesare (`pyinstaller-hooks-contrib` acoperă deja
`pywebview`). Dependințe noi în `requirements.txt`: `pywebview`,
`pyobjc-framework-Cocoa/WebKit/Quartz` (Mac), `pythonnet` (Windows,
backend implicit EdgeChromium) — **partea Windows NU a putut fi testată
real de-aici** (fără mașină Windows), rămâne de confirmat o dată de
Cristi.

**B. Pipeline dinamic** — tabele noi `ProjectTypeDef`/`ProjectStageDef`
(`backend/models.py`), per-user, editabile/reordonabile din Setări
("Tipuri & Etape proiect"), seed automat din vechile constante
(`seed.py::seed_default_pipeline_defs`, apelat la înregistrare ȘI la
migrare pentru userii existenți, `app.py::_migrate_schema`) — clienții
existenți nu-și pierd datele. Audit trail real: `ProjectStageEvent`, un
rând NOU (niciodată suprascris) la fiecare avansare (`next-step` sau
click direct pe stepper — `jump-to-stage`), inclusiv la creare. Stepper
interactiv în Quick Preview (`projects.html`), cu istoric per-proiect.
Verificat complet prin curl, pe o bază de date izolată (nu cea reală a
lui Cristi): creare proiect, jump direct, istoric cu 2+ rânduri, adăugare/
reordonare/dezactivare tip și etapă custom, **și blocarea corectă (409)
a ștergerii unei etape/tip încă în uz**.

**C. Context total** — `Client.kind` (individual/informal; Company
existent = juridic, cu CUI), `fiscal_id` opțional, `is_flagged`/
`flag_note` pe Client ȘI Project (badge vizibil, distinct de `notes`).
`PAYMENT_STATUSES` +„advance", `CURRENCIES` +USD (inclusiv
`auth.py::set_currency`, care valida hardcodat doar EUR/RON — bug de
drift închis pe drum). `balance_due`/`is_overdue` calculate direct pe
`Project.to_dict()` (`is_overdue` e computed, NU un al 5-lea status
stocat — depinde de data curentă, nu de o alegere manuală). Endpoint nou
`/api/open-folder` (oglindă exactă a lui `pick-folder`, `open`/
`explorer`), buton „Deschide folderul" lângă fiecare cale RAW/Montaj/
Export.

**D. Checklist-uri** — auto-aplicare la creare proiect
(`create_project`: caută `ChecklistTemplate` cu `project_type` potrivit,
copiază itemele) — verificat: proiect nou tip nuntă → 2 checklist-uri
aplicate automat. Item de checklist capătă `equipment_id` opțional,
autocompletare din inventar în UI (`+ din inventar`), enriched cu
`equipment_name` în `to_dict()`.

**E. Echipament** — status nou „subrented"; `return_checkout_item`
capătă `condition` (ok/missing/damaged): avariat → `maintenance`,
lipsă → `lost` (vizibil, cu alertă în UI), nu mai revine tăcut la
`available`. **Fix real, verificat direct**: `complete_checkout` (închide
forțat o fișă) lăsa echipamentul blocat la nesfârșit pe `checked_out`,
fără nicio alertă — acum orice item neprocesat devine `missing`→`lost`,
răspunsul include `newly_missing_count` pentru alertă explicită în UI.
Testat cu date reale prin curl: 2 echipamente pe o fișă, unul întors OK,
celălalt rămas la `complete` → confirmat trecut pe `lost`, alertă
generată.

## v2.0.2 (2026-09-04) — Ghid corectat + zero referințe GitHub pe site

**Cerință directă de la Cristi**: (1) instrucțiuni pentru cum ștergi baza
de date veche înainte de o instalare complet nouă; (2) "regula master"
încălcată — nu trebuie să existe niciun link/text către GitHub, nici pe
pagina web, nici la descărcare de către clienți (Regula 20, extinsă acum
explicit și la site, nu doar la self-updater).

**Fix real găsit pe drum, în afara cererii inițiale**: ghidul PDF
(RO/EN/ES) și pagina de prezentare menționau amândouă "7 zile de probă
gratuită" — perioada reală, din cod (`backend/license_manager.py::
TRIAL_DAYS`), e **25 de zile**. Corectat peste tot (6 apariții în ghid,
8 pe site), verificat direct în PDF-ul generat și pe pagina live.

**Audit complet al mențiunilor GitHub client-facing** (`grep -rn "github"`
pe `docs/`, `frontend/`, comparat cu ce apare doar în cod/comentarii
dezvoltator, care rămân neatinse):
- Eliminat butonul "Cod sursă (GitHub)" din hero (`docs/index.html`).
- Eliminat link-ul "GitHub" din footer.
- Eliminat toate mențiunile text "disponibil pe GitHub"/"din ultima
  versiune de pe GitHub"/"Descarcă aplicația de pe GitHub Releases" —
  reformulate generic, fără să numească sursa.
- `frontend/` (aplicația în sine): **deja conform** — self-updater-ul
  (Regula 20) nu a avut niciodată text/link vizibil către GitHub, doar
  comentarii de cod (developer-facing, niciodată afișate userului).
- **NEATINS, semnalat explicit**: cele 4 butoane de descărcare
  (`releases/latest/download/...`) rămân linkuri DIRECTE către fișierul
  `.pkg`/`.exe` — nu randează o pagină GitHub (nu există "Cod sursă",
  browsing de commit-uri, etc.), doar declanșează descărcarea fișierului.
  Regula 9 din Partea 1 CERE explicit exact acest tipar
  (`releases/latest/download/...`, HTTP 200 verificat). Nu le-am
  schimbat fără confirmare explicită — ar necesita un proxy de
  redirecționare (arhitectură nouă, nu doar un edit de text) dacă chiar
  se dorește ascunderea domeniului github.com și la aceste 4 linkuri.
- `README.md` (fișierul propriu al repo-ului GitHub) — NEATINS,
  intenționat: e citit doar de cineva deja pe GitHub, nu de un client
  care descarcă aplicația de pe `gordas.dev`.

**Verificat**: PDF regenerat (`generate_guides.py` → `html_to_pdf.swift`
→ `pypdf`, 27 pagini), conținut confirmat direct din fișier (25 zile
prezent, 7 zile dispărut, FAQ nou prezent, în toate 3 limbile). Sincronizat
în oglinda `gdc-plugin-manager-catalog-vendor` și verificat live pe
`gordas.dev` (conținut real descărcat și verificat, nu presupus).

## v2.0.1 (2026-09-04) — F închis complet: revocare, preț dinamic, catalog

Continuarea directă a secțiunii F de mai jos (v2.0.0) — după citirea
implementării de referință reale din `gdc-plugin-manager-catalog-vendor`
(`RevocationCheck.swift`, `SupabaseConfig.swift`, migrarea SQL,
`AnalyticsClient.swift`, `PricingChecker.swift` din DataMover), nu ghicit.

- `backend/revocation_check.py` (nou) — port 1:1 al `RevocationCheck.swift`:
  RPC Supabase `is_license_revoked(machine_id, product_id)`, fail-open,
  verificare la lansare + la 6 ore (thread de fundal). Cheia Supabase
  folosită e cea "anon public", identică cu restul ecosistemului — RLS
  blochează orice altceva decât acest RPC exact, deci e sigur de comis.
  Cablat în `license_manager.is_licensed()`: o licență validă Ed25519 dar
  marcată revocată devine `False` (cade pe trial/demo), niciodată
  invers — revocarea nu suprascrie niciodată o stare "not revoked" pe
  baza unui răspuns vechi/lipsă.
- `backend/analytics_client.py` (nou) — port 1:1 al `AnalyticsClient.swift`:
  `POST /rest/v1/devices` (fire-and-forget, thread separat, erori
  înghițite). Notă specifică acestui repo: aplicația nu are conceptul de
  "email" (cont local username/parolă) — trimis gol, nu omis, ca
  înregistrarea să rămână structural identică cu restul ecosistemului.
  Apelat la `register()` și `login()` (`auth.py`).
- `backend/pricing_checker.py` (nou) + `GET /api/license/pricing`
  (`license_routes.py`, public) — port 1:1 al `PricingChecker.swift`
  (DataMover): citește `gordas.dev/pricing.json`, calculează fereastra
  de ofertă activă, fail-open pe `25 €` (suma deja documentată în acest
  repo — NU 23 € generic, prețul specific era deja stabilit). Verificat
  live: fără intrare pentru acest produs în `pricing.json`, ruta
  întoarce corect fallback-ul, nu o eroare.
- `frontend/settings.html` — mesajul WhatsApp + rândul de preț din
  Setări citesc acum prin `/api/license/pricing`, nu mai au suma
  hardcodată `25€ lifetime` în JS.
- **`gdc-plugin-manager-catalog-vendor/docs/catalog.json`**: adăugat
  `"pricingProductID": "gdc-production-manager"` pe intrarea deja
  existentă (aplicația era deja în catalog, doar fără preț propriu) —
  edit chirurgical (o linie), nu regenerare completă a fișierului (prima
  încercare, cu `json.dump(sort_keys=True)`, a rescris tot fișierul,
  847 linii — anulată explicit, refăcută corect).
- **`gdc-plugin-manager-catalog-vendor/docs/pricing.json`**: intrare nouă
  `"gdc-production-manager"`, `basePrice: 25 EUR`, fără promoție
  programată (nicio decizie de preț/ofertă luată unilateral — Cristi
  poate adăuga o promoție oricând din Furnizor, panoul "Prețuri & Oferte").
- **NEATINS, intenționat**: `catalog.json`/`pricing.json` sunt fișiere
  statice, editate direct (nu prin Furnizor/GitOps) — modificate local în
  acest repo, DAR necomise/nepublicate încă pe `gdc-plugin-manager-catalog-vendor`
  (repo separat, cu propriul flux de commit+push) — vezi jurnalul acelui
  repo pentru comanda exactă de publicare.

**Verificat live**: `/api/license/pricing` (fail-open confirmat, 25 EUR),
`/api/license/status` neafectat de integrarea de revocare, înregistrare
cont nouă (declanșează `analytics_client.register_device` fără să
blocheze/crape), zero erori server. **Nu s-a putut verifica**: un
răspuns REAL "true" de la RPC-ul de revocare (necesită o intrare reală în
`license_revocations`, pusă manual de Cristi din Supabase) — comportamentul
fail-open pe absența răspunsului e singurul verificat direct.

## v2.0.0 (2026-09-04, F parțial la publicare — vezi v2.0.1 mai sus pentru închidere completă)

**F. Integrare GDC Plugin Manager — PARȚIAL, restul EXPLICIT deferred**
(Regula 30, nu ascuns): protocolul de licențiere (Ed25519+`machine_id.py`)
e deja identic cu restul ecosistemului, nimic de schimbat acolo.
Implementat acum: Profil (Nume/Username, acest repo nu are conceptul de
"Email" — aplicație 100% locală, fără cont online) + Machine ID mutate
vizibil în sidebar (`renderShell`/`renderLicenseBadge`), nu doar în
Settings. **NEIMPLEMENTAT, decis explicit cu Cristi să rămână așa
deocamdată**: revocare/blacklist prin Supabase (Regula 12) și Pricing
Manager dinamic (Regula 27) — ambele cer citirea prealabilă a
implementării de referință din `gdc-plugin-manager-catalog-vendor`
(schemă Supabase reală, format `pricing.json`) ca să nu fie ghicite;
adăugarea acestei aplicații în `catalog.json` — schimbare pe alt repo,
nefăcută încă. TODO real pentru o sesiune viitoare, nu opțional uitat.

**G. Versiune & packaging** — `2.0.0` sincronizat în
`backend/config.py`, `docs/update.json`, `build/build-mac.spec`
(`CFBundleShortVersionString`/`CFBundleVersion` — găsite desincronizate
de la `1.2.1`, drift preexistent, reparat pe drum) și `installer.iss`
(`MyAppVersion` — găsit la `1.2.5`, la fel desincronizat, reparat).
Packaging Mac (`.pkg` semnat+notarizat+stapled, instalare directă în
`/Applications`) și Windows (Inno Setup, Program Files) rămân neatinse —
deja conforme conform auditurilor de mai sus; DB/config deja separate
corect în Application Support/AppData (`config.py::get_data_dir()`), deci
supraviețuiesc oricărui update. **Nu s-a rulat un build de release real
(cu semnare/notarizare/CI)** — doar buildul local de verificare descris
la punctul A. Pasul de instalare efectivă (dublu-click pe pkg, prompt de
parolă admin) rămâne de confirmat manual, o dată, de Cristi — la fel ca
la restul ecosistemului.

## Completare 2026-08-26 (v1.2.4) — pop-up modal, nu doar banner
Verificat explicit: punctul 2 din Directiva Supremă (update checker) exista
deja, dar notificarea era DOAR bannerul discret (`checkUpdateBanner`,
`#update-banner-slot`) — nu un pop-up care întrerupe, cum s-a cerut. Fix:
`checkUpdateBanner()` (`frontend/script.js`) construiește acum și un
overlay modal (`#update-modal-overlay`, `.update-modal`), afișat o dată
per versiune, cuplat cu aceeași stare de dismissal
(`gdcpm_dismissed_update_version`) ca bannerul — închiderea oricăruia le
ascunde pe amândouă. Chei de traducere noi în `translations.js`
(`update_modal_title`/`update_modal_body`/`update_modal_later`, RO/EN/ES).
Stil în `style.css` (`.update-modal-overlay`/`.update-modal`).

## Audit final 2026-08-26 — Inno Setup installer (lipsea complet)
Găsit la auditul de conformitate global: aplicația Windows se distribuia
ca `.exe` portabil brut într-un zip (rulat direct din orice folder,
dezinstalat manual cu `uninstall-windows.bat`) — încălca Regula 5
(instalare automată în Program Files, scurtături, dezinstalare nativă).
Fix: `installer.iss` (nou, Inno Setup) — `DefaultDirName={autopf}\GDC\GDC
Production Manager`, scurtături Start Menu + Desktop, `[UninstallDelete]`
curăță și `%APPDATA%\GDCProductionManager`. `.github/workflows/build-windows.yml`
actualizat să compileze installer-ul (ISCC, preinstalat pe
`windows-latest`) și să publice `GDCProductionManagerSetup.exe` — nu mai
zip-ul brut vechi.

## v2.0.3 (2026-09-06) — Ghidul PDF accesibil direct din pagina de Ajutor

Audit ecosistem (cerut de Cristi): `docs/guides/Instructiuni_Utilizare.pdf`
(deja unificat, 27 pagini, RO/EN/ES — vezi v2.0.2) exista, dar nimic din
`help.html` nu-l deschidea efectiv — userul trebuia să-l caute manual în
arhiva de instalare.

**Fix**: `backend/routes.py` — rută nouă `POST /api/open-guide` (mirror
exact al `open_folder()` deja existent — `open`/Mac, `os.startfile`/
Windows), deschide `resource_path("docs", "guides",
"Instructiuni_Utilizare.pdf")`. `build/build-mac.spec` +
`build-windows.spec` — `docs/guides/` adăugat în `datas` (NU era
bundle-uit deloc până acum, deci ruta ar fi eșuat cu 404 în orice build
real, deși PDF-ul exista pe disc în dev). `help.html` — card nou sub
„Mai multe resurse”, buton care apelează ruta prin `API.post` (același
tipar ca „Deschide folderul”). Chei noi `help_pdf_title`/`help_pdf_text`/
`help_pdf_link` (RO/EN/ES, `translations.js`).

**Verificat REAL**: `resource_path()` testat direct (venv izolat, deps
din `requirements.txt`) — rezolvă corect calea, fișierul există pe disc.
Ruta înregistrată corect pe un Flask app de test (`api_bp` montat,
`/api/open-guide` prezent în `url_map`). Import-ul întârziat
(`from app import resource_path`, în interiorul funcției, nu la nivel de
modul) evită circularitatea `app.py`↔`routes.py` (`app.py` importă deja
`api_bp` din `routes.py` la nivel de modul).

Versiune 2.0.2 → 2.0.3 (PATCH), sincronizată în `backend/config.py` și
`docs/update.json`.

**Regula 32 — REZOLVAT 2026-09-06.** 40 atribuiri reale găsite; `git
filter-repo` refuzat de clasificatorul automat al mediului Claude Code,
nu o amânare deliberată. Repo PUBLIC — Regula 32 se aplică integral.
Script de curățare pregătit (`~/Developer/clean-claude-attribution.sh`)
și rulat manual de Cristi. **Verificat după rulare: 0 apariții**, remote
`origin` corect re-adăugat, push confirmat pe `main` și tag-uri.

## Etapa 2026-09-11 — v2.0.4 publicat cu semnare Windows activa

Secretele CI (`WIN_SELFSIGN_PFX_BASE64`/`WIN_SELFSIGN_PFX_PASSWORD`,
certificat COMUN ecosistemului) erau deja incarcate de Cristi. Acest release
e primul in care semnarea Regulii 34 chiar a rulat pe un build real.

Verificat direct, nu presupus: pasul de semnare marcat OK in lista de pasi a
job-ului, plus directorul de securitate din header-ul PE al installer-ului
descarcat = 7496 bytes de semnatura Authenticode (acelasi certificat +
timestamp pe toate aplicatiile). Link stabil `releases/latest/download/...`
verificat HTTP 200.


## Etapa 2026-09-12 (v2.1.0) — DECIZIE DE PRODUS: gratuit până la anunțul versiunii oficiale

**Cerință explicită a lui Cristi, de reținut permanent.** Aplicația rămâne
**gratuită, fără nicio limitare și fără perioadă de probă**, cât timp e în
dezvoltare. Motivul dat: aplicația „încă nu este concretizată", iar un preț
afișat pe ceva neterminat nu are atracție și blochează exact feedback-ul care
trebuie strâns acum de la cei care o descarcă.

**Condiția de ieșire, singura:** prețul și trialul intră în funcțiune DOAR
când Cristi declară explicit că versiunea e oficială. Nu la o versiune anume,
nu la o dată, nu automat.

**Cum e implementat (un singur comutator, nu o rescriere):**
- `backend/license_manager.py` → `PREVIEW_FREE_MODE = True`. Cât e True,
  `is_unlocked()` întoarce mereu `True`, iar `status()` expune
  `preview_free: true`. Toată infrastructura de licențiere (Ed25519, trial de
  25 zile, revocare, `pricing.json`) rămâne INTACTĂ și netestată-de-la-zero —
  la anunțul versiunii oficiale se schimbă `True` → `False` și revine totul.
- UI: `frontend/settings.html` ascunde starea de probă, linia de preț și tot
  blocul de activare (Machine ID + WhatsApp + formular de serial), în locul lor
  arată explicația + butonul „Trimite o sugestie" (mesaj WhatsApp cu versiunea
  curentă completată automat). `frontend/script.js` → badge-ul din sidebar nu
  mai numără zile, arată „În dezvoltare — gratuit".
- Chei noi RO/EN/ES în `translations.js`: `preview_free_badge`,
  `preview_free_title`, `preview_free_text`, `preview_free_feedback`,
  `suggest_btn`.
- `docs/index.html` (RO/EN/ES): secțiunea de preț devine „În dezvoltare —
  gratuit", butonul principal trimite o sugestie, nu o donație; textul de
  licență și meta-descrierea actualizate.
- `gdc-plugin-manager-catalog-vendor/docs/catalog.json`: intrarea acestei
  aplicații trece de la `"kind": "trial"` la `"kind": "free"` și i s-a scos
  `pricingProductID`, ca să nu apară nicio sumă în catalogul GDC Plugin
  Manager. **Intrarea din `pricing.json` a fost lăsată INTACTĂ** intenționat —
  la revenirea pe plătit se readaugă `pricingProductID` și prețul e deja
  acolo, nu trebuie recreat.

**Bug-uri preexistente găsite pe drum și reparate** (Regula 30):
- Butonul de WhatsApp zicea „Cumpără"/„Buy"/„Comprar" — încălcare directă a
  Regulii 3 (susținerea se exprimă exclusiv ca donație, niciodată „cumpără").
  Reformulat în toate cele 3 limbi.
- `installer.iss` (`MyAppVersion`) și `build/build-mac.spec`
  (`CFBundleShortVersionString`/`CFBundleVersion`) rămăseseră la `2.0.2` deși
  aplicația era la `2.0.4` — încălcare a Regulii 14, sincronizate la `2.1.0`.

**Verificat direct, nu presupus:** `is_unlocked()` întoarce `True` pe o
instalare cu trialul deja aproape epuizat (`trial_days_remaining: 1`) — adică
gating-ul chiar nu mai blochează, nu doar că textul s-a schimbat.

### Completări specifice acestui repo, mutate din fosta Partea 1 (2026-09-18)

Păstrate verbatim. Regula generală la care se referă fiecare e în
`~/Developer/CLAUDE.md`.

**Regula 20:**

**Status acest repo (2026-08-27): IMPLEMENTAT (cod complet, publicare prin
CI existent, netestat manual încă de Cristi).** `backend/self_updater.py`
(nou) — descarcă installer-ul (`.pkg` Mac / `.exe` Windows) cu `urllib`,
îl instalează (Mac: script bash elevat cu `osascript ... with
administrator privileges`, la fel ca `SelfUpdater.swift`; Windows:
`subprocess.Popen` detașat), scrie progresul într-un fișier de status
(`%TEMP%/gdc_production_manager_update_status.json`) — NU o fereastră
nativă, UI-ul e servit în browser local, deci progresul se arată prin
polling. Rute noi: `POST /api/update/install` (pornește update-ul
async), `GET /api/update/install-status` (polling). `frontend/script.js`
+ `settings.html` — `window.open(url, "_blank")` ÎNLOCUIT complet cu
`startSelfUpdate()` (apel API + modal de progres cu polling, NICIODATĂ
tab nou de browser). `docs/update.json.download_url.mac` schimbat de la
`.zip` (nu putea fi instalat direct) la `.pkg` direct — `.github/workflows/
build-mac.yml` actualizat să publice și `GDCProductionManager.pkg` ca
asset separat (înainte doar zip-ul, .pkg-ul exista doar în interiorul
lui). Windows publica deja exe-ul brut, nicio schimbare necesară acolo.
Versiune → `1.3.0`. **WARNING nemodificat**: pasul de instalare efectiv
nu poate fi verificat automat — necesită confirmare manuală, o dată, de
Cristi, pe fiecare platformă, după ce CI-ul publică `v1.3.0`.

**Regula 21:**

**Status acest repo (2026-08-28, verificat): NU SE APLICA ACUM.** Auditat la cererea lui Cristi — `backend/sync.py` face doar cereri API mici prin `urllib.request.urlopen` (cu timeout), nu transfera fisiere de proiect mari. Daca se adauga vreodata upload/download de fisiere de productie (footage, proiecte Resolve arhivate etc.), aplica Regula 21 atunci.

**Regula 34:**

  installer (asset de release sau folder `dist/`) — colaboratorii îl
  importă o SINGURĂ dată în Trusted Root, apoi orice build viitor semnat
  cu ACELAȘI certificat (persistent via secret CI, NU regenerat la
  fiecare build — un cert nou la fiecare release ar rupe încrederea deja
  acordată) e automat de încredere pe mașinile lor.
- **Aplicare**: la fiecare build de release/actualizare Windows, pe orice
  aplicație din `~/Developer/` care produce un `.exe`/installer Windows —
  aplicată incremental, la următoarea atingere reală a fiecărui repo
  (Regula 11), nu retroactiv peste tot dintr-o sesiune dedicată.
- **Implementare de referință**: CGConvertor (`build-windows.spec` +
  `.github/workflows/build-windows.yml`, 2026-09-06) — vezi
  `codesigning/README-windows.md` din acel repo pentru pașii exacți pe
  care Cristi trebuie să-i ruleze o singură dată (generare cert + upload
  secret CI). **Portat în acest repo (`gdc-production-manager`,
  2026-09-06)** — `codesigning/sign-windows.ps1` +
  `codesigning/generate-self-signed-cert.ps1` (adaptate, cert COMUN
  ecosistemului, vezi `codesigning/README-windows.md` din acest repo),
  cei 2 pași de semnare adăugați în `.github/workflows/build-windows.yml`
  (`env.HAS_WIN_SELFSIGN` la nivel de job, identic tipar CGConvertor) —
  validat cu `actionlint`, 0 erori. Secretele CI (`WIN_SELFSIGN_PFX_BASE64`/
  `WIN_SELFSIGN_PFX_PASSWORD`) rămân de încărcat separat de Cristi, direct
  pe acest repo (`gh secret set ... --repo gordasgdc/gdc-production-manager`),
  chiar dacă valoarea e identică cu cea din CGConvertor.
