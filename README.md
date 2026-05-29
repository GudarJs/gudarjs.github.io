# Sitio en Lektor — Guzmán D. Darío

Proyecto [Lektor](https://www.getlektor.com/) que genera el sitio estático personal.
El contenido se edita directamente en los archivos `contents.lr` (o desde la UI admin
de Lektor) y el HTML se genera al hacer build.

El sitio es **bilingüe**: español en `/` (alt primaria) e inglés en `/en/`.
Las cadenas de UI viven en `databags/i18n_es.json` y `databags/i18n_en.json`.

---

## Estructura

```
lektor/
│
├─ guzman-dario.lektorproject        # config del proyecto + alts ES / EN
│
├─ databags/
│   ├─ i18n_es.json                  # traducciones de UI — español
│   └─ i18n_en.json                  # traducciones de UI — inglés
│
├─ models/                           # esquemas de página (.ini)
│   ├─ home.ini                      # página de inicio
│   ├─ cv.ini                        # currículum vitae
│   ├─ page.ini                      # página genérica
│   ├─ post-list.ini  · post.ini     # blog
│   ├─ taller-index.ini              # listado de talleres
│   ├─ taller.ini                    # portada de un taller
│   └─ taller-paso.ini               # paso individual de un taller
│
├─ flowblocks/
│   │
│   │  ── CV ──────────────────────────────────────────────────────────
│   ├─ cv_contact_item.ini           # ítem de contacto (email, github…)
│   ├─ cv_entry_item.ini             # entrada de educación o voluntariado
│   ├─ cv_experience_item.ini        # experiencia laboral
│   ├─ cv_skill_item.ini             # habilidad con barra de nivel
│   ├─ cv_talk_item.ini              # charla o taller en el CV
│   │
│   │  ── Home ─────────────────────────────────────────────────────────
│   ├─ home_company_chip.ini         # logo-chip del strip "He trabajado en"
│   ├─ home_skill_card.ini           # tarjeta de habilidad en la sección skills
│   ├─ home_testimonial.ini          # testimonio / quote
│   ├─ home_workshop_card.ini        # taller destacado en el home
│   │
│   │  ── Pasos de talleres ────────────────────────────────────────────
│   ├─ texto.ini                     # párrafos en markdown
│   ├─ codigo.ini                    # bloque de código con etiqueta + lenguaje
│   ├─ comando_os.ini                # comando con variantes Win / macOS / Linux
│   ├─ imagen.ini                    # captura con pie de foto
│   ├─ analogia.ini                  # metáfora pedagógica
│   ├─ advertencia.ini               # callout de advertencia
│   ├─ checkpoint.ini                # "¿lo que ves coincide?"
│   ├─ error_provocado.ini           # error guiado o trampa
│   └─ solucion_error.ini            # solución del error anterior
│
├─ templates/                        # Jinja2
│   ├─ layout.html                   # base: carga i18n, nav, footer, FA icons
│   ├─ _topnav.html                  # nav + selector de idioma
│   ├─ _footer.html
│   ├─ _pasos_nav.html               # sidebar de pasos en un taller
│   ├─ home.html
│   ├─ cv.html                       # vista web + layout de impresión (print-only)
│   ├─ page.html
│   ├─ post-list.html  · post.html
│   ├─ taller-index.html  · taller.html  · taller-paso.html
│   └─ blocks/                       # un .html por flowblock
│       ├─ cv_contact_item.html  cv_entry_item.html  cv_experience_item.html
│       ├─ cv_skill_item.html  cv_talk_item.html
│       ├─ home_company_chip.html  home_skill_card.html
│       ├─ home_testimonial.html  home_workshop_card.html
│       ├─ texto.html  codigo.html  comando_os.html  imagen.html
│       ├─ analogia.html  advertencia.html  checkpoint.html
│       ├─ error_provocado.html  solucion_error.html
│
├─ content/                          # árbol de contenido
│   ├─ contents.lr                   # home ES  (/)
│   ├─ contents+en.lr                # home EN  (/en/)
│   ├─ cv/
│   │   ├─ contents.lr               # CV ES    (/cv/)
│   │   └─ contents+en.lr            # CV EN    (/en/cv/)  — sólo campos que difieren
│   ├─ blog/
│   │   ├─ contents.lr               # listado de posts
│   │   └─ <slug>/contents.lr        # post individual
│   └─ talleres/
│       ├─ contents.lr               # listado de talleres
│       └─ <slug>/
│           ├─ contents.lr           # portada del taller
│           └─ <NN-slug>/contents.lr # paso del taller
│
└─ assets/                           # servidos en la raíz del sitio generado
    ├─ static/
    │   ├─ colors_and_type.css       # tokens de color y tipografía (variables CSS)
    │   ├─ site.css                  # estilos globales
    │   ├─ site.js
    │   ├─ workshop.css              # estilos exclusivos de talleres
    │   ├─ workshop.js
    │   ├─ profile.png
    │   └─ quote.png
    └─ font-awesome/                 # Font Awesome 4 (icon font)
        ├─ css/font-awesome.min.css
        └─ fonts/
```

---

## Cómo correrlo

```bash
# Desde la raíz del proyecto (donde está el venv)
source venv/bin/activate
cd lektor

# Servidor de desarrollo con admin en /admin/
lektor server --admin            # → http://127.0.0.1:5000

# Build de producción
lektor build --output-path dist/
```

---

## Bilingüe (ES / EN)

| Alt | URL base | Archivo de contenido |
|-----|----------|----------------------|
| `es` (primaria) | `/` | `contents.lr` |
| `en` | `/en/` | `contents+en.lr` |

**Regla:** el alt EN sólo necesita los campos que cambian respecto al ES.
Los campos omitidos en `contents+en.lr` heredan el valor del `contents.lr` principal.

Las cadenas de interfaz (navegación, etiquetas, botones) se cargan en `layout.html`:

```jinja
{% set lang = 'en' if this.alt == 'en' else 'es' %}
{% set t = bag('i18n_' + lang) %}
```

**Importante:** los templates de flowblocks se renderizan en un contexto Jinja2
independiente — la variable `t` **no está disponible** dentro de `blocks/*.html`.
Usa texto literal o campos propios del bloque para cualquier copia que necesite traducción.

---

## Imágenes de portada en posts y talleres

Posts y talleres aceptan el campo `cover_image` (ruta o URL absoluta):

```
cover_image: /static/mi-imagen.jpg
```

Si se omite, el thumbnail muestra el gradiente de color configurado.
Los talleres también exponen `cover_image` en el flowblock `home_workshop_card`.

**Colores disponibles para posts** (`theme`): `green`, `blue`, `red`, `coral`.

---

## .gitignore recomendado

```gitignore
# Build output
dist/

# Lektor cache
.lektor/

# Credenciales y tokens (script update_from_linkedin.py)
.env
.linkedin_token.json

# Python
__pycache__/
*.pyc
venv/
```

---

## Actualizar el CV desde LinkedIn

El script `../update_from_linkedin.py` (en la raíz del proyecto) lee la API de
LinkedIn y sobreescribe los campos `experience`, `education`, `volunteering` y
`skills` en `content/cv/contents.lr`, preservando los colores de logo y el resto
de los campos intactos.

**Setup único:**

```bash
# 1. Crear app en https://www.linkedin.com/developers/apps
#    Auth tab → Redirect URL: http://localhost:8000/callback
#    Products tab → solicitar "Sign In with LinkedIn using OpenID Connect"

# 2. Copiar credenciales
cp ../.env.example ../.env
# editar .env con LINKEDIN_CLIENT_ID y LINKEDIN_CLIENT_SECRET

# 3. Ejecutar (abre el navegador la primera vez)
cd ..
python update_from_linkedin.py

# Opciones
python update_from_linkedin.py --auth      # forzar re-autorización
python update_from_linkedin.py --dry-run   # preview sin escribir
```

El token OAuth se cachea en `.linkedin_token.json` (válido 60 días).
Ni `.env` ni `.linkedin_token.json` deben commitearse — añádelos al `.gitignore`.

---

## Agregar un taller paso a paso

**1. Portada del taller** (`content/talleres/<slug>/contents.lr`):

```
_model: taller
---
title: Nombre del taller
---
orden: 2
---
duracion: 1 hora 30 minutos
---
cover_image: /static/cover-mi-taller.jpg
---
prerrequisitos_resumen: Python básico
---
descripcion:

Una línea o dos sobre de qué va el taller.
---
producto_final:

Qué van a tener al final.
---
objetivos:

- Aprender X
- Entender Y
---
stack:

- Python 3.10+
- Algo más
```

**2. Cada paso** (`content/talleres/<slug>/01-<nombre>/contents.lr`):

```
_model: taller-paso
---
title: Instalación
---
orden: 1
---
body:

#### texto ####
texto:

Primer párrafo en markdown.

#### codigo ####
lenguaje: python
----
etiqueta: settings.py
----
codigo: INSTALLED_APPS = [
    "daphne",
    ...
]

#### checkpoint ####
texto:

Si ves el mensaje X, todo va bien.
```

**Convención:** el campo `orden` del paso debe coincidir con el prefijo numérico
de la carpeta (`04-vistas/` → `orden: 4`) para que el sidebar y los botones
anterior/siguiente sean correctos.

---

## Bloques disponibles en pasos de talleres

| Bloque | Cuándo usarlo | Apariencia |
|--------|---------------|------------|
| `texto` | Párrafos normales (markdown) | texto plano |
| `codigo` | Código con etiqueta de archivo + lenguaje | code-block oscuro |
| `comando_os` | Comando que varía entre Win / macOS / Linux | OS tabs |
| `imagen` | Captura de pantalla con pie | screenshot frame |
| `analogia` | Metáfora pedagógica para un concepto abstracto | callout morado |
| `advertencia` | Algo a tener cuidado | callout amarillo |
| `checkpoint` | "¿Lo que ves coincide con esto?" | callout coral |
| `error_provocado` | Error intencional (`guiado` o `trampa`) | callout rojo |
| `solucion_error` | Va **inmediatamente** después de `error_provocado` | callout verde |

---

## Convenciones de contenido

- Español en los campos de contenido; inglés en `contents+en.lr`.
- Segunda persona ("vas a", "fíjate", "guarda el archivo").
- Un concepto nuevo por paso de taller.
- Cada `error_provocado` va seguido **inmediatamente** por un `solucion_error`.
- No usar guion largo (—); usar coma, dos puntos o punto.

---

## Recursos

- [Documentación de Lektor](https://www.getlektor.com/docs/)
- [Models & content](https://www.getlektor.com/docs/models/)
- [Flow blocks](https://www.getlektor.com/docs/api/db/types/flow/)
- [Templates](https://www.getlektor.com/docs/templates/)
- [Alternatives (multilingüe)](https://www.getlektor.com/docs/content/alts/)
