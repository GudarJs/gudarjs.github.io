# Convenciones

## Nombres de carpetas y orden

- El **slug del taller** va en minúsculas, sin espacios, con guiones: `mi-primer-blog-django`.
- Cada paso es una carpeta con **prefijo numérico de dos dígitos**: `01-`, `02-`, ... El prefijo
  fija el orden y es el `_id` de la página en Lektor.
- Mantén el campo `orden` del paso igual al número del prefijo. Ejemplo: la carpeta
  `04-vistas/` tiene `orden: 4`. Así el sidebar y los botones anterior/siguiente coinciden.
- Numeración recomendada: `01` prerrequisitos, `02` introducción, `03`..`N` un concepto por paso,
  `N+1` cierre. La portada del taller es el `contents.lr` de la carpeta del taller (sin prefijo).

## Distribución de los errores provocados

- No todos los pasos llevan error. Colócalos donde el fallo enseña: primeras configuraciones,
  primer uso de un concepto nuevo, integraciones entre piezas, despliegue.
- **Errores guiados** (modo `guiado`) para conceptos clave: el texto avisa que se provoca a
  propósito. Bajan la ansiedad y enseñan a leer el traceback.
- **Trampas naturales** (modo `trampa`) para errores típicos de principiante: el texto NO delata
  de antemano; el estudiante llega al error como llegaría solo, y el bloque siguiente revela que
  era esperado.
- Todo `error_provocado` va **inmediatamente seguido** de un `solucion_error`. Nunca dejes el
  error sin salida en la misma página.

## Tono según nivel (se decide por taller)

- **Principiantes totales:** explica cada término al introducirlo, usa muchas analogías, frases
  cortas, segunda persona, emojis discretos ocasionales. No asumas nada.
- **Principiantes con bases:** asume variables, funciones, condicionales; explica todo lo del
  stack nuevo. Menos analogías, pero sí en los conceptos realmente abstractos.
- **Intermedio:** ritmo más ágil, menos explicación de fundamentos, foco en lo nuevo del stack o
  de la arquitectura. Analogías solo para lo genuinamente difícil. Modera los emojis.

## Reglas de estilo del contenido

- Español en todo momento.
- No usar guion largo (—). Usar coma, dos puntos, punto y coma o punto.
- Segunda persona ("vas a", "fíjate", "guarda el archivo").
- Resultados visibles temprano: que algo funcione en los primeros pasos.
- Un concepto nuevo por página.
