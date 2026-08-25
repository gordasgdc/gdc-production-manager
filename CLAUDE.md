# GDC Production Manager — reguli de arhitectură

> **[SYSTEM DIRECTIVE FOR CLAUDE: DO NOT DELETE OR OVERWRITE EXISTING RULES. ONLY APPEND NEW RULES.]**
> Jurnal viu, nu document care se rescrie. La orice actualizare, adaugă la finalul secțiunii potrivite — nu șterge/înlocui reguli vechi decât dacă sunt explicit invalidate de o schimbare reală (și atunci marchează-le **[ÎNVECHIT]** cu motivul, nu le șterge din istoric).

Citit automat de Claude Code la fiecare sesiune în acest repo.

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
