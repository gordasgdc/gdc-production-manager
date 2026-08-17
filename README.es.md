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
- **Etapas de trabajo claras**: planificación → rodaje → montaje → etalonaje → revisión → final → entregado, con un botón **"Next Step"** que avanza el proyecto automáticamente, mostradas como una barra de progreso al estilo scope en cada proyecto
- **Notas por etapa**: cada etapa (planificación, rodaje, montaje…) guarda su propio campo de notas por separado
- **Moneda seleccionable** (EUR / RON) por proyecto, curso o producto — los totales del panel se calculan por separado para cada moneda, nunca mezclados
- **Clientes** con datos de contacto y número de proyectos/cursos asociados
- **Cursos 1 a 1**: tema, fecha y hora, duración, precio, estado de pago, estado del curso (programado/confirmado/finalizado/cancelado), ubicación (en línea/presencial)
- **Productos digitales**: DCTLs, PowerGrades, LUTs, presets, plantillas — con precio, versión, compatibilidad, ruta local y enlace de descarga
- **Rutas de archivos** para RAW, montaje y exportación final
- **Adjuntos**: contratos, briefs o referencias directamente en el proyecto
- **Listas de verificación por proyecto** (antes del rodaje, después del rodaje, personalizadas), con elementos marcables, progreso y plantillas reutilizables
- **Recordatorios** para plazos, facturas y reuniones, con resumen en el panel
- **Facturación simple**: presupuesto total, cantidad cobrada, estado de pago
- **Panel** con estadísticas, notificaciones (plazos próximos, facturas pendientes), próximas entregas y cursos
- **Calendario mensual** de rodajes y entregas
- **Informes PDF** por proyecto (imprime directamente desde la app)
- **Exportar/Importar JSON** — copia de seguridad y migración entre portátiles
- **Tema claro/oscuro**, cambio instantáneo
- **Sincronización self-hosted opcional** — entre dos instalaciones de la app, sin servidor de terceros
- **Multiusuario local**: cada cuenta guarda sus propios datos en el mismo portátil
- **Interfaz en RO / EN / ES**
- **100% local**, código abierto (MIT) — 7 días de prueba gratuita, luego activación de por vida (25€, pago único)
- **Recuperación de contraseña con código de rescate**, inicio rápido con Touch ID / Windows Hello, verificación de actualizaciones en la app

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
