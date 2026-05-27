# Integración en tu proyecto Lektor

Esta guía explica dónde copiar cada archivo de la skill, una sola vez, para que tu sitio
Lektor pueda renderizar los talleres. Después de esto, generar talleres es solo crear
archivos `contents.lr`.

## 1. Copiar modelos

Copia a la carpeta `models/` de tu proyecto:

- `taller-index.ini`
- `taller.ini`
- `taller-paso.ini`

Estos definen los tres tipos de página: el índice de talleres, la portada de un taller y un
paso. El modelo `taller-paso` declara un campo `body` de tipo `flow` que admite los nueve
bloques pedagógicos.

## 2. Copiar flow blocks

Copia los nueve `.ini` a la carpeta `flowblocks/` (créala si no existe):

`texto.ini`, `codigo.ini`, `imagen.ini`, `analogia.ini`, `checkpoint.ini`,
`error_provocado.ini`, `solucion_error.ini`, `advertencia.ini`, `comando_os.ini`.

## 3. Copiar plantillas

Copia a `templates/`:

- `taller-index.html`, `taller.html`, `taller-paso.html`

Y a `templates/blocks/` (créala si no existe) las nueve plantillas de bloque, con el mismo
nombre que su `.ini` pero extensión `.html`. Lektor asocia automáticamente cada flow block a
su plantilla en `templates/blocks/` por el nombre del archivo.

**Importante sobre el layout:** las plantillas extienden `layout.html`. Tu proyecto debe tener
un `templates/layout.html` con, al menos, los bloques `{% block title %}` y `{% block body %}`.
Si tu plantilla base usa otros nombres de bloque, ajusta la primera y última línea de las tres
plantillas de página para que coincidan con tu layout.

## 4. Copiar el CSS

Copia `taller.css` a la carpeta de assets estáticos de tu sitio (habitualmente `assets/static/`
en Lektor) e inclúyelo desde tu `layout.html`:

```html
<link rel="stylesheet" href="{{ '/static/taller.css'|url }}">
```

La paleta y el espaciado están en variables CSS al inicio del archivo (bloque `:root`). Ajusta
ahí los colores para que combinen con tu sitio sin tocar el resto.

## 5. Crear el contenedor de talleres

Crea `content/talleres/contents.lr` con el modelo del índice. Ejemplo mínimo:

```
_model: taller-index
---
title: Talleres
---
intro:

Talleres autoguiados para aprender paso a paso.
```

A partir de aquí, cada taller es una subcarpeta de `content/talleres/`, y cada paso una
subcarpeta del taller. La skill genera todo eso por ti.

## Comprobar que funciona

Arranca el servidor de desarrollo de Lektor (`lektor server`) y entra en `/talleres/`. Deberías
ver el índice; al entrar a un taller, su portada; y al entrar a un paso, el sidebar con todos
los pasos y los botones anterior/siguiente.

Si un paso no aparece en el sidebar o el orden es raro, revisa el campo `orden` del paso y el
prefijo numérico de su carpeta: ambos deben ser coherentes (ver `convenciones.md`).
