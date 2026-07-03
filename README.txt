# Caja de herramientas

Colección de herramientas web para tareas administrativas. Todo funciona directamente en el navegador: no hay servidor, no se instala nada y los datos se procesan localmente.

## Herramientas actuales

| Código | Herramienta | Descripción |
|--------|-------------|-------------|
| HT-001 | Calculadora de horas | Diferencias horarias a partir de reportes de asistencia (PDF o carga manual) |
| HT-002 | Comparativo de presupuestos | Cuadro comparativo entre presupuestos de proveedores |
| HT-003 | Comparador de nombres | Cruce de dos listas de nombres (exactas, reordenadas, parciales, sin match) |

## Estructura

```
├── index.html            ← página de inicio (índice de herramientas)
├── herramientas/         ← una herramienta por archivo HTML
│   ├── calculadora_horas.html
│   ├── comparador_presupuestos.html
│   └── comparador_nombres.html
└── README.md
```

## Cómo publicar en GitHub Pages

1. Creá un repositorio nuevo en GitHub y subí estos archivos a la raíz.
2. En el repositorio, entrá a **Settings → Pages**.
3. En *Source*, elegí **Deploy from a branch**, rama `main`, carpeta `/ (root)`.
4. Guardá. En uno o dos minutos el sitio queda publicado en
   `https://TU-USUARIO.github.io/NOMBRE-DEL-REPO/`.

## Cómo agregar una herramienta nueva

1. Guardá el archivo `.html` dentro de `herramientas/`.
2. Abrí `index.html` y agregá una entrada al listado `HERRAMIENTAS` (está comentado en el código). Usá el siguiente código correlativo (HT-004, HT-005, …).
3. Subí los cambios (`git add`, `git commit`, `git push`). GitHub Pages se actualiza solo.

## ¿Y los scripts de Python?

GitHub Pages solo sirve archivos estáticos: **no puede ejecutar Python en un servidor**. Aun así, hay tres caminos según el script:

1. **Reescribirlo en JavaScript** (recomendado para scripts simples): si el script procesa texto, hace cálculos o transforma archivos, casi siempre se puede convertir a una herramienta HTML como las que ya hay. Es la opción más liviana y rápida para el usuario.
2. **Ejecutar Python en el navegador con [Pyodide](https://pyodide.org)**: carga un intérprete de Python vía WebAssembly dentro de la página. Funciona incluso con librerías como `pandas` o `numpy`. La contra es que la primera carga pesa varios MB y tarda unos segundos.
3. **Un backend externo**: solo si el script necesita sí o sí correr en un servidor (acceso a bases de datos, credenciales, procesos largos). En ese caso se aloja aparte (Render, Railway, Cloud Functions) y la página lo consume por API. Es la opción más compleja de mantener.

En la práctica, la mayoría de los scripts administrativos entran en la opción 1 o 2.
