# GDC Production Manager

[🇷🇴 Română](README.md) · [🇬🇧 English](README.en.md) · [🇪🇸 Español](README.es.md)

**Una app de escritorio independiente para gestionar proyectos de producción de vídeo.**
Cada usuario la instala en su propio portátil; los datos se quedan en local, sin nube.

---

## 📦 Descargar e instalar

La última versión está disponible en [Releases](https://github.com/gordasgdc/gdc-production-manager/releases).

| Plataforma | Archivo | Instalación |
|---|---|---|
| **Mac** | `GDCProductionManager.pkg` | doble clic → sigue el instalador |
| **Windows** | `GDCProductionManager.exe` | doble clic para ejecutar |

Al iniciar por primera vez, la app abre su interfaz en una pestaña de navegador local (`http://127.0.0.1:xxxx`) — nada sale de tu equipo.

## 🚀 Características

- **Proyectos** con tipo (película, anuncio, boda, documental, broadcast, videoclip musical, corporativo), lugar de rodaje, fechas de rodaje/entrega
- **Etapas de trabajo claras**: planificación → rodaje → montaje → etalonaje → revisión → final → entregado, mostradas como una barra de progreso al estilo scope en cada proyecto
- **Clientes** con datos de contacto y número de proyectos asociados
- **Rutas de archivos** para RAW, montaje y exportación final
- **Facturación simple**: presupuesto total, cantidad cobrada, estado de pago
- **Panel** con estadísticas y próximas entregas
- **Multiusuario local**: cada cuenta guarda sus propios datos en el mismo portátil
- **Interfaz en RO / EN / ES**
- **100% local y gratis**, de código abierto (MIT)

## 🛠️ Stack técnico

- Backend: **Flask** + **SQLite** (vía SQLAlchemy)
- Frontend: HTML + CSS + JavaScript puro (sin paso de compilación)
- Distribución: **PyInstaller** → `.app`/`.pkg` (Mac) y `.exe` (Windows)
- CI/CD: **GitHub Actions** (build automático en cada etiqueta `v*`)

## 💻 Ejecutar desde el código fuente (desarrollo)

```bash
git clone https://github.com/gordasgdc/gdc-production-manager.git
cd gdc-production-manager
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python backend/app.py
```

La app inicia un servidor local y abre la interfaz en tu navegador automáticamente.

## 📁 Estructura del proyecto

```
gdc-production-manager/
├── .github/workflows/       # build-mac.yml, build-windows.yml
├── backend/                 # Flask: app.py, models.py, routes.py, auth.py, config.py
├── frontend/                # HTML/CSS/JS: panel, proyectos, clientes, autenticación
├── docs/                    # página de presentación (GitHub Pages)
├── build/                   # archivos .spec de PyInstaller
├── icon/                    # iconos de la app
├── requirements.txt
├── CHANGELOG.md
└── LICENSE
```

## 🏷️ Publicar una nueva versión

Consulta [CHANGELOG.md](CHANGELOG.md) para el historial y sigue estos pasos para publicar un nuevo build:

```bash
git add .
git commit -m "Describe tus cambios"
git push origin main

git tag -a v1.0.1 -m "Descripción de la versión"
git push origin v1.0.1
```

> Nota de Git: crea la etiqueta **después** de `git push`, nunca antes —
> de lo contrario, Actions podría intentar compilar un commit que aún no existe en el remoto.

GitHub Actions compila automáticamente los paquetes de Mac y Windows y los publica en [Releases](https://github.com/gordasgdc/gdc-production-manager/releases).

## 👤 Autor

**Cristi Gordas (GDC)** — colorista y editor de vídeo

- [GitHub](https://github.com/gordasgdc)
- [Facebook](https://web.facebook.com/cristiGDC)
- [YouTube](https://www.youtube.com/@cristigordas)
- [resolvemaster.training](https://resolvemaster.training)

## 📄 Licencia

MIT — ver [LICENSE](LICENSE).
