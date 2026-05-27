# Formato de los archivos `contents.lr`

Lektor guarda cada página en un `contents.lr`. Los campos se separan con una línea de tres
guiones `---`. Dentro de un campo `flow`, los bloques se separan con `####  nombre ####` y los
campos internos de cada bloque usan **cuatro** guiones `----` (un nivel más que el separador de
campos de página).

## Portada del taller (`taller/contents.lr`)

```
_model: taller
---
title: Mi primer blog con Django
---
orden: 1
---
duracion: 6 a 8 horas
---
descripcion:

Vas a construir un blog funcional desde cero y publicarlo en internet.
---
producto_final:

Un blog donde puedes crear, editar y mostrar publicaciones, con una página de inicio
que las lista y una página de detalle para cada una.
---
objetivos:

Al terminar este taller vas a poder:

- Crear un proyecto Django y entender su estructura
- Definir modelos y aplicar migraciones
- Escribir vistas, urls y plantillas
- Publicar tu sitio en internet
---
stack:

- Python 3.12
- Django 5.0
- SQLite (incluido con Python)
- Git y una cuenta en PythonAnywhere
---
prerrequisitos_resumen: Python 3.12 y un editor de código instalados
```

## Un paso (`taller/03-modelos/contents.lr`)

El campo `body` es un flow. Cada bloque empieza con `#### nombre_del_bloque ####`. Dentro,
los campos se separan con `----`. Ejemplo con varios tipos de bloque, incluyendo los dos modos
de error:

```
_model: taller-paso
---
title: Crear el modelo de publicaciones
---
orden: 3
---
body:

#### texto ####
texto:

Ahora vamos a decirle a Django cómo se ve una publicación de nuestro blog.
A esto se le llama un **modelo**: es la forma en la que describimos qué datos
guardamos y de qué tipo son.

#### analogia ####
titulo: Un modelo es como una ficha de biblioteca
texto:

Piensa en las fichas de cartón de una biblioteca antigua. Cada ficha tiene los mismos
campos: título, autor, año. El modelo es el formato de la ficha; cada publicación que
crees será una ficha rellenada con ese formato.

#### codigo ####
etiqueta: blog/models.py
lenguaje: python
codigo:

from django.db import models

class Publicacion(models.Model):
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    creada = models.DateTimeField(auto_now_add=True)

#### error_provocado ####
modo: guiado
titulo: Vamos a ver qué pasa si olvidamos migrar
texto:

Guarda el archivo y, sin hacer nada más, arranca el servidor con `python manage.py runserver`
y entra al panel de administración. A propósito todavía **no** hemos aplicado los cambios a la
base de datos. Vas a ver un error parecido a este:

`OperationalError: no such table: blog_publicacion`

#### solucion_error ####
texto:

Ese error significa que Django conoce tu modelo, pero la tabla todavía no existe en la base de
datos. Falta el paso de **migrar**. Ejecuta estos dos comandos y el error desaparece:

`python manage.py makemigrations`
`python manage.py migrate`

La lección: cada vez que cambies un modelo, tienes que crear y aplicar migraciones.

#### checkpoint ####
texto:

Si todo salió bien, ahora puedes entrar al panel de administración y ver tu modelo
**Publicacion** disponible. Acabas de guardar tu primer dato en la base de datos.

#### advertencia ####
texto:

Ojo: si renombras un campo del modelo más adelante, vuelve a ejecutar `makemigrations` y
`migrate`. Es el olvido más común al principio.
```

## Reglas importantes del formato

- Cada campo de página va separado por `---` (tres guiones) en su propia línea.
- Dentro de un campo `flow`, los campos de cada bloque van separados por `----` (cuatro guiones).
- Los campos de texto largo (markdown, text) empiezan en la línea siguiente al nombre del campo
  y pueden ocupar varias líneas.
- El nombre del bloque entre almohadillas debe coincidir con el nombre del flowblock declarado
  en el modelo `taller-paso` (`texto`, `codigo`, `imagen`, `analogia`, `checkpoint`,
  `error_provocado`, `solucion_error`, `advertencia`, `comando_os`).
- En `comando_os`, rellena solo los sistemas operativos relevantes; los vacíos no se muestran.
- En `imagen`, el campo `imagen` es el nombre de un archivo adjunto en la misma carpeta del paso
  (un attachment). Coloca la imagen junto al `contents.lr` del paso.
- El campo `orden` del paso y el prefijo numérico de la carpeta deben ser coherentes para que el
  sidebar muestre el orden correcto.
