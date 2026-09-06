# codesigning/ — semnare Windows (Self-Signed, testare internă)

Acest document acoperă DOAR partea Windows a acestui repo (adăugată
2026-09-06, CLAUDE.md Regula 34). Nu există un `README.md` Mac în acest
folder (`gdc-production-manager` nu are încă infrastructură de
semnare/notarizare Mac în `codesigning/` — dacă apare vreodată, acest
document rămâne strict Windows, fără suprapunere).

## Certificat COMUN pentru tot ecosistemul GDC

**Decizie explicită a lui Cristi**: certificatul self-signed NU e unic
per aplicație — e ACELAȘI certificat, folosit de toate aplicațiile GDC
care produc un `.exe`/installer Windows (CGConvertor, GDC Production
Manager, și orice altă aplicație viitoare). Secretele CI se numesc
IDENTIC în toate repo-urile — `WIN_SELFSIGN_PFX_BASE64` și
`WIN_SELFSIGN_PFX_PASSWORD` — dar sunt încărcate SEPARAT, o dată per
repo (GitHub Actions nu permite partajarea secretelor între repo-uri
fără un cont Organization/Enterprise).

## De ce Self-Signed, și ce NU rezolvă

Un certificat self-signed **nu elimină avertismentul SmartScreen/"Unknown
publisher"** pentru publicul larg — doar un certificat real de la o CA
publică (cu reputație acumulată) sau un certificat EV fac asta. Self-signed
e util STRICT pentru:
- testare internă (buildurile pe care le rulează Cristi însuși),
- distribuire către un cerc restrâns de colaboratori care importă manual
  certificatul public (`.cer`) în Trusted Root o singură dată.

La lansarea comercială publică, planul e Azure Trusted Signing sau un
certificat EV (HSM cloud) — vezi CLAUDE.md Regula 34 pentru context complet.

## Setup unic (o dată, făcut DIRECT de Cristi pe Windows real)

Certificatul (privat, cu cheie) nu trece niciodată prin conversația cu
Claude — la fel ca orice altă parolă/cheie din ecosistem.

**Dacă certificatul comun a fost deja generat pentru alt repo** (ex.
CGConvertor, `codesigning/README-windows.md` de acolo) — sari peste pasul
1, refolosește ACELAȘI `.pfx` deja generat, doar repetă pasul 2 cu
`--repo gordasgdc/gdc-production-manager`.

1. Pe Windows real (Parallels e suficient), deschide PowerShell **ca
   Administrator** și rulează (DOAR dacă certificatul comun nu există
   încă deloc):
   ```powershell
   .\codesigning\generate-self-signed-cert.ps1
   ```
   Scriptul cere o parolă nouă (pentru `.pfx`) și produce două fișiere:
   - `gdc-selfsign.pfx` — **PRIVAT**, nu se distribuie, nu se
     comite în git.
   - `gdc-selfsign.cer` — **PUBLIC**, se distribuie colaboratorilor.

2. Încarcă `.pfx`-ul ca secrete GitHub Actions, PENTRU ACEST REPO —
   comenzile exacte (adaptate) sunt afișate la finalul scriptului
   (necesită `gh` CLI autentificat pe acea mașină):
   ```powershell
   gh secret set WIN_SELFSIGN_PFX_BASE64 --repo gordasgdc/gdc-production-manager --body $b64
   gh secret set WIN_SELFSIGN_PFX_PASSWORD --repo gordasgdc/gdc-production-manager
   ```

3. Șterge `.pfx`-ul local imediat după (`Remove-Item gdc-selfsign.pfx -Force`)
   — rămâne doar în secretele CI, criptate.

4. Distribuie `gdc-selfsign.cer` colaboratorilor (dacă nu l-au primit
   deja de la un alt repo GDC — certificatul e comun, importul e o
   singură dată per mașină de colaborator, nu per aplicație). Pe fiecare
   mașină a lor, o singură dată: dublu-click → **Install Certificate** →
   **Local Machine** → "Place all certificates in the following store" →
   **Trusted Root Certification Authorities**.

Odată făcuți pașii 1-4, **fiecare build viitor din CI** (`git push
origin vX.Y.Z`) semnează automat `.exe`-ul și installer-ul cu ACELAȘI
certificat — colaboratorii nu mai trebuie să reimporte nimic la
versiunile următoare, nici pe acest repo, nici pe alt repo GDC care
folosește același certificat.

## Ce face CI-ul automat (`.github/workflows/build-windows.yml`)

- Dacă secretele NU sunt setate: build-ul continuă **nesemnat**, exact ca
  până acum — nicio eroare, nicio schimbare de comportament.
- Dacă secretele SUNT setate: după ce `GDCProductionManager.exe`
  (PyInstaller) și installer-ul final (Inno Setup,
  `GDCProductionManagerSetup.exe`) există, ambele sunt semnate cu
  `signtool.exe` (localizat dinamic din Windows Kits, cu timestamp), apoi
  verificate cu `Get-AuthenticodeSignature` — confirmă DOAR că semnătura
  a fost atașată corect, fără să ceară lanț de încredere complet (asta ar
  eșua mereu pe un runner CI proaspăt, care nu are certificatul în
  Trusted Root — normal pentru self-signed, nu un bug). Un eșec real de
  semnare (fișier fără nicio semnătură) tot oprește build-ul (CI roșu).

## Regenerarea certificatului (dacă expiră sau e compromis)

Rulează din nou `generate-self-signed-cert.ps1`, reîncarcă secretele
(pasul 2 de mai sus îi suprascrie pe cei vechi) **în TOATE repo-urile GDC
care folosesc certificatul comun** (nu doar acesta) — dar **toți
colaboratorii trebuie să reimporte noul `.cer`**, altfel văd din nou
avertismentul pentru versiunile semnate cu noul certificat. Evită
regenerarea inutilă — de asta scriptul folosește o valabilitate de 5 ani.
