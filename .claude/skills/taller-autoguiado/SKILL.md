---
name: taller-autoguiado
description: >
  Genera talleres autoguiados al estilo Django Girls para estudiantes, en español, como
  contenido para un sitio Lektor. Cada taller es una página padre con una página hija por
  cada paso o concepto (un concepto = una página), navegables con sidebar y botones
  anterior/siguiente. Usa flow blocks tipados (texto, código, imagen, analogía, checkpoint,
  error-provocado, solución-error, advertencia, comando-os) y enseña deliberadamente a
  través del error (mixto: errores guiados para conceptos clave, trampas naturales para
  errores comunes de principiante). Usa esta skill SIEMPRE que el usuario pida crear un
  "taller", "taller autoguiado", "tutorial estilo Django Girls", "workshop para estudiantes",
  "guía paso a paso para Lektor", o material formativo dividido en pasos/capítulos navegables.
  Actívala también si menciona generar contenido de enseñanza con stack tecnológico, conceptos
  a profundizar y pasos secuenciales, aunque no diga la palabra "taller" explícitamente.
---

# Generador de Talleres Autoguiados (estilo Django Girls, para Lektor)

## Qué produce esta skill

Talleres autoguiados en **español**, pensados para que un estudiante avance solo, paso a
paso, como en el tutorial de Django Girls. Cada taller se materializa como **contenido de un
sitio Lektor**: una página padre (la portada del taller) y una página hija por cada paso.
El principio rector es **un concepto por página** y **resultados visibles temprano**.

La salida son archivos `contents.lr` listos para colocar en el árbol `content/` del proyecto
Lektor del usuario, más (si aún no existen) los modelos, flow blocks, plantillas y CSS que
hacen falta una sola vez.

---

## Infraestructura: ya instalada en este proyecto

Este proyecto (gudarjs.github.io) ya tiene toda la infraestructura instalada:

- ✅ **Modelos** — `models/taller.ini`, `models/taller-paso.ini`, `models/taller-index.ini`
- ✅ **Flowblocks** — los 9 bloques pedagógicos en `flowblocks/`
- ✅ **Plantillas** — `templates/taller.html`, `templates/taller-paso.html`, `templates/taller-index.html` y `templates/blocks/` (reescritas con Tailwind v4)
- ✅ **CSS** — estilos de taller integrados en `assets/static/workshop.css` y `assets/static/site.css` (Vite + Tailwind)
- ✅ **Índice** — `content/talleres/contents.lr` existe

Ve directo al flujo de creación de un taller. No generes ni copies archivos de infraestructura.

---

## Flujo de creación de un taller

El flujo tiene dos fases. **No generes ningún `contents.lr` hasta terminar la Fase 1 y tener
el índice de pasos aprobado por el usuario.** El usuario fue explícito: el contexto y el
alcance completos del proyecto deben estar claros antes de generar.

### Fase 1 — Descubrimiento (una pregunta a la vez)

Haz las preguntas **de una en una**, esperando la respuesta antes de la siguiente. No
amontones preguntas. Cuando sea cómodo para el usuario, usa botones de opción. El objetivo es
entender el proyecto completo antes de escribir nada.

Cubre, como mínimo, en este orden aproximado:

1. **La actividad / producto final.** ¿Qué van a construir los estudiantes al terminar?
   Pide una descripción concreta del resultado (ej. "un blog con publicaciones y comentarios",
   "una API REST de tareas", "una landing page responsive"). Esto ancla todo el taller.
2. **El stack tecnológico exacto, con versiones.** Lenguajes, frameworks, librerías,
   herramientas, servicios de despliegue. Pregunta por versiones concretas: las versiones
   cambian comandos y mensajes de error, y el taller debe ser reproducible.
3. **Nivel de los estudiantes para ESTE taller.** (Varía por taller; siempre pregúntalo.)
   Opciones: principiantes totales (cero programación, explicar todo desde la base, estilo
   Django Girls puro) / principiantes con bases (ya conocen variables, funciones, pero son
   nuevos en este stack) / intermedio (programan bien, el stack o los conceptos son nuevos).
   El nivel define el tono y cuánto se explica cada concepto base.
4. **Conceptos que deben profundizarse.** Pide la lista de conceptos que el usuario quiere
   que el taller trate en detalle (ej. "rutas y vistas", "ORM y migraciones", "componentes y
   estado"). Cada concepto importante tenderá a ser su propia página.
5. **Duración estimada** del taller (para la portada y para dimensionar el número de pasos).
6. **Prerrequisitos.** Qué deben tener instalado/sabido antes de empezar. Recuerda: el taller
   incluirá una **página de prerrequisitos ligera** (qué tener instalado + enlaces oficiales),
   NO instrucciones de instalación paso a paso.
7. **Objetivos de aprendizaje.** Qué sabrá hacer el estudiante al terminar (van en la portada).
8. **Slug y título del taller.** Confirma el título visible y el identificador de carpeta
   (slug en minúsculas, sin espacios, con guiones; ej. `mi-primer-blog-django`).

Sugiere proactivamente, y pregunta si quiere incluirlos, los elementos típicos de Django Girls
que el usuario quizá no mencionó: una analogía del mundo real por cada concepto abstracto
nuevo; checkpoints de "en este punto deberías ver esto funcionando"; comandos marcados por
sistema operativo (Windows/Mac/Linux) cuando el stack use terminal; una página de cierre con
"siguientes pasos" para seguir aprendiendo. No los impongas: propón y deja decidir.

### Cierre de Fase 1 — Propuesta de índice

Cuando tengas el panorama completo, **propón el índice de pasos** (la "tabla de capítulos"):
una lista ordenada de páginas con su título y una frase de qué cubre cada una. Estructura
recomendada, adaptable:

```
00 · Portada del taller            (objetivos, duración, producto final, prerrequisitos/stack)
01 · Prerrequisitos                (qué instalar + enlaces, ligera)
02 · Introducción / el panorama    (qué vamos a construir y por qué, analogía inicial)
03..N · Un paso por concepto        (cada concepto en su página, con resultados visibles)
N+1 · Cierre                       (lo que lograste, siguientes pasos)
```

Recuerda los principios al diseñar el índice: introducir **un concepto nuevo a la vez**;
ordenar para que haya **un resultado visible cuanto antes**; insertar puntos donde provocar
errores tiene valor pedagógico. Pide al usuario que apruebe o ajuste el índice. **No avances
sin aprobación.**

### Fase 2 — Generación

Una vez aprobado el índice, **pregunta el ritmo de generación** (el usuario decide en cada
taller):

- Paso a paso con confirmación (genera un paso, lo muestra, pregunta antes del siguiente).
- Por bloques de pasos (ej. de 3 en 3) con confirmación entre bloques.
- Todo de una vez tras aprobar el índice, y luego ajustar.

Genera según el ritmo elegido. Cada paso es un `contents.lr` con el modelo `taller-paso`,
dentro de su carpeta numerada (`01-prerrequisitos/`, `02-introduccion/`, ...). El prefijo
numérico fija el orden en el sidebar.

---

## Dónde escribir los archivos

Escribe los archivos directamente en el directorio de trabajo del proyecto usando la
herramienta Write. El path base para los talleres es:

```
content/talleres/<slug-del-taller>/
```

Estructura completa:

```
content/
  talleres/
    <slug-del-taller>/
      contents.lr                 modelo: taller   (portada)
      01-prerrequisitos/
        contents.lr               modelo: taller-paso
      02-introduccion/
        contents.lr               modelo: taller-paso
      03-<concepto>/
        contents.lr               modelo: taller-paso
      ...
```

Si `content/talleres/contents.lr` no existe, créalo. En este proyecto ya existe, así que
solo crea la subcarpeta del taller nuevo.

**No uses `/mnt/user-data/outputs/` ni ninguna ruta temporal.** Escribe directamente en
el árbol `content/` del proyecto.

---

## Cómo escribir cada paso

Sigue el espíritu de Django Girls: cálido, cercano, en segunda persona ("vas a", "fíjate
en"), sin jerga sin explicar, asumiendo solo lo que el nivel declarado permite. Emojis
ocasionales y discretos están bien si el nivel es principiante; modéralos en nivel intermedio.
Nunca uses guion largo (—) en el contenido; usa coma, dos puntos o punto.

Cada paso se compone de **flow blocks**. El formato de un `contents.lr` con flow se detalla en
`references/formato-contents-lr.md`; **léelo antes de escribir el primer taller.**

> Error crítico a evitar (verificado construyendo con Lektor): dentro de un bloque flow con
> varios campos, separa cada campo con `----` (CUATRO guiones) en su propia línea. Si no lo
> haces, Lektor mete todo el texto siguiente dentro del primer campo y el bloque se rompe (por
> ejemplo, un `error_provocado` mostraría siempre la etiqueta de modo equivocada). Los bloques de
> un solo campo (texto, advertencia, checkpoint sin título) no necesitan `----`.

Resumen de los bloques disponibles y cuándo usarlos:

- **texto** — explicación en markdown. El hilo conductor del paso.
- **codigo** — bloque de código con lenguaje y, opcionalmente, etiqueta de archivo o terminal.
- **imagen** — captura o diagrama (ruta a un attachment del propio paso).
- **analogia** — recuadro con un símil del mundo real para un concepto abstracto. Úsalo la
  primera vez que aparece un concepto difícil (al estilo del cartero y el urlresolver).
- **checkpoint** — recuadro destacado de "en este punto deberías ver/tener esto". Da resultado
  visible y refuerza el avance. Úsalo tras cada hito ejecutable.
- **error-provocado** — el bloque distintivo. Induce deliberadamente a un error.
- **solucion-error** — acompaña SIEMPRE a un error-provocado: explica por qué ocurrió, cómo
  leer el mensaje y cómo resolverlo.
- **advertencia** — aviso de "ojo con esto" para errores frecuentes o pasos delicados.
- **comando-os** — un comando con sus variantes Windows / Mac / Linux.

### La mecánica del error (mixto)

El usuario quiere que el taller **haga equivocarse a propósito** y luego enseñe a resolver.
Aplica el enfoque **mixto**:

- **Errores guiados** para los **conceptos clave**: di abiertamente "vamos a escribir esto mal
  a propósito para ver qué pasa". El estudiante sabe que lo provoca, baja la carga emocional y
  se concentra en **leer el traceback**. Ideal para enseñar a interpretar mensajes de error.
  Usa `error-provocado` (con la instrucción explícita) seguido de `solucion-error`.
- **Trampas naturales** para los **errores comunes de principiante**: lleva al estudiante por
  el camino que recorrería solo y que falla (olvidar guardar, no activar el entorno, una coma
  de más, importar mal). Deja que vea el error real y **luego revela** que era esperado y que
  acaba de aprender a reconocerlo. Usa `error-provocado` (sin delatar de antemano) seguido de
  `solucion-error`.

Cada `error-provocado` debe ir **siempre** acompañado de su `solucion-error`. Nunca dejes a un
estudiante en un error sin la salida. Distribuye los errores: no todos los pasos necesitan uno;
colócalos donde el aprendizaje del fallo es valioso (configuración, primeros usos de un
concepto, integraciones).

---

## Campos de cada modelo (resumen)

Detalle completo y ejemplos en `references/integracion-lektor.md`. Resumen:

- **taller** (portada): `title`, `descripcion`, `producto_final`, `objetivos` (markdown lista),
  `duracion`, `stack` (markdown lista), `prerrequisitos_resumen`, `cover_image` (opcional,
  ruta o URL), `orden`.
- **taller-paso** (paso): `title`, `orden` (entero para ordenar), `body` (flow con los bloques).
- **taller-index**: `title`, `intro`.

El `orden` y/o el prefijo numérico de la carpeta gobiernan la secuencia del sidebar y los
botones anterior/siguiente. Mantén ambos consistentes.

---

## Recordatorios de calidad

- Un concepto nuevo por página; no mezcles dos conceptos grandes en un mismo paso.
- Resultado visible cuanto antes: que el estudiante vea algo funcionando en los primeros pasos.
- Toda analogía y todo checkpoint deben ser relevantes, no decorativos.
- Todo `error-provocado` lleva su `solucion-error`.
- Verifica que los comandos y mensajes de error correspondan a las **versiones** declaradas del
  stack. Si no estás seguro de un mensaje de error exacto de una versión reciente, búscalo.
- Español en todo el contenido. Sin guion largo (—).
- Cierra cada taller con una página de "lo que lograste + siguientes pasos".
