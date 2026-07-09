# TP Final — Nagel-Schreckenberg aplicado a vehículos dirigidos por vibración (VDV)

**72.25 Simulación de Sistemas** (ITBA, Prof. Daniel Parisi) — 2026 Q1 · Grupo **G01S2**

Simulación de tráfico 1D con un autómata celular de **Nagel-Schreckenberg** (Regla 2 modificada
por contacto) aplicado al experimento de robots Hexbug, vehículos dirigidos por vibración
(VDV, sigla técnica usada en el artículo) de Patterson & Parisi. El objetivo es **reproducir por
simulación los observables del experimento y compararlos** (ver el artículo en
[`extras/FD_VDV.pdf`](extras/FD_VDV.pdf)).

> 📐 El diseño completo (modelo, reglas, calibración, matriz de experimentos y plan) está en
> **[`diseno-tp-final-vdv-nasch_v1.md`](diseno-tp-final-vdv-nasch_v1.md)**.
> Leelo antes de tocar código.

---

## Requisitos

| Herramienta | Versión usada |
|---|---|
| Java (JDK) | 21 |
| Maven | 3.9+ |
| Python | 3.12 |

## Estructura

```
.
├── diseno-tp-final-vdv-nasch_v1.md   # documento de diseño (la referencia)
├── README.md
├── CLAUDE.md                # convenciones del repo (modelo, pet-peeves de la cátedra)
├── engine/                  # motor de simulación (Java / Maven) — escribe estado físico
│   ├── pom.xml
│   └── src/main/java/ar/edu/itba/sds/...
├── analysis/                # análisis y animación (Python) — calcula los observables
│   ├── requirements.txt
│   └── *.py
├── data/                    # salidas del motor (ignorado por git)
├── figures/                 # figuras generadas
└── extras/FD_VDV.pdf        # artículo de referencia
```

**Separación clave (la exige la cátedra):** el motor (Java) **solo escribe estado físico**
(`id, posición [mm], velocidad [mm/s]`). **Todos los observables se calculan después** con Python
sobre esos archivos. Nunca dentro del motor.

---

## Cómo construir y correr

### 1. Motor (Java)

```bash
cd engine
mvn clean package            # compila, corre tests y arma el jar ejecutable
java -jar target/nasch-vdv-1.0-SNAPSHOT.jar --help
```

> **Estado actual:** **motor completo y verificado.** Inicialización física, R1–R4, ambas variantes de
> R2 (A contacto puro oficial, B clásica para validar), órdenes de inserción y protocolos FIXED_N e
> INCREMENTAL_180S, con validación `p=0` de la **variante B** contra el diagrama fundamental analítico
> (en el caso homogéneo `p=0`, la variante A da flujo libre hasta el contacto). `mvn test` → **suite
> JUnit completa en verde**; 0 solapamientos y reproducibilidad bit-a-bit verificadas. El motor escribe **solo estado
> físico**; los observables se calculan después (Python).

### 2. Análisis (Python)

```bash
cd analysis
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 -m pytest tests -q                 # tests de comportamiento de los observables
```

#### ⭐ Barrido OFICIAL de la entrega — CONTACTO_PURO (lo que corre `scripts/generar_entrega.sh`)

El barrido **oficial** usa **solo la variante A (CONTACTO_PURO)**: ambos protocolos (N fijo +
incremental), los 3 órdenes de inserción, `N ∈ {5,10,15,20,25,30}`, `p ∈ {0, 0.1, 0.2, 0.3, 0.4}` y
30 realizaciones. Son **1350 corridas** (~8–12 min, ~0,85 GB en disco gracias a `--output-every 10`).
Los observables se calculan **después**, nunca durante la simulación.

La variante B (CLASICA_SALVO_CERO) **no** entra en este barrido: se corre únicamente en su **régimen de
validación analítica** (`validacion.py`: `ℓ=1`, homogéneo, `p=0`, contra el diagrama fundamental
triangular), **no** sobre la grilla calibrada heterogénea.

```bash
cd analysis

# 1) GENERAR el barrido oficial del TP (solo variante A, lo mismo que generar_entrega.sh)
python3 run_matrix.py --out-dir ../data \
    --rule CONTACTO_PURO \
    --protocol FIXED_N INCREMENTAL_180S \
    --order ASCENDING DESCENDING RANDOM \
    --n 5 10 15 20 25 30 \
    --p 0 0.1 0.2 0.3 0.4 \
    --realizations 30 \
    --output-every 10

# 2) ANALIZAR → figuras preliminares + evolución temporal (para elegir el estacionario)
python3 analyze.py --data-dir ../data --figures-dir ../figures

# 3) Mirar figures/evolucion_temporal_*.png, elegir el corte y RECALCULAR las figuras finales
python3 analyze.py --data-dir ../data --figures-dir ../figures --since-step <paso_elegido>

# 4) Validación triangular de la variante B (en su régimen ℓ=1, homogéneo, p=0)
python3 validacion.py --figures-dir ../figures

# 5) Animación (GIF) de una corrida representativa
python3 -c "import animate; animate.animate('../data/<archivo>.txt')"
```

**Notas:**
- `--output-every 10` reduce disco/RAM/tiempo ~10× con pérdida estadística despreciable (los cuadros
  consecutivos están correlacionados). Para FIXED_N el `--order` se ignora (sólo importa en el incremental),
  así que no genera corridas redundantes.
- **Más rápido / menos disco:** bajar `--realizations` (p. ej. 20) si el error entre realizaciones ya estabiliza.
- **Solo el subconjunto del artículo** (variante oficial A, protocolo incremental):
  `python3 run_matrix.py --out-dir ../data --rule CONTACTO_PURO --protocol INCREMENTAL_180S --order ASCENDING DESCENDING RANDOM --output-every 10`
- **Exploración opcional (NO es la entrega):** agregar `CLASICA_SALVO_CERO` a `--rule` corre también la
  variante B sobre la grilla calibrada heterogénea (**~2700 corridas**, ~16–24 min, ~1,7 GB, el doble del
  oficial). Ojo: B sobre la grilla calibrada **no** es su validación analítica (esa es `validacion.py`
  con `ℓ=1`, homogéneo, `p=0`) ni forma parte del barrido oficial; queda solo como material exploratorio.

---

## 🎬 Animaciones (siguen las guías de formato)

Estándar de la cátedra (guía externa *GuiaPresentaciones* de la materia, no versionada en este repo; puntos 2.4.1, 2.4.8 y 1.7–1.9),
ya implementado en `animate.py`:

- Una **animación característica por parámetro estudiado**, idealmente con **dos valores extremos** para
  mostrar comportamientos distintos: p. ej. **baja densidad (N=5, flujo libre)** vs **alta densidad
  (N=30, congestión)**; y los **tres órdenes** de inserción en el protocolo incremental.
- Ejes con leyenda **en palabras + unidad física** (SI: mm, mm/s; p. ej. `posición (mm)`), **fuente ≥ 20**, **barra de color**
  rotulada (`velocidad (mm/s)`), tiempo en segundos, y los **parámetros fijos al costado** de la figura.
- **Tiempo real** por defecto (24 fps si la corrida se generó con `--output-every 1`, igual que la
  cámara del experimento de 24 fps).
- ⚠️ En el **PDF entregable NO van animaciones ni se entregan archivos de animación**: va una **imagen
  fija** de un fotograma representativo y, **debajo, una nota neutral de publicación** hasta tener
  links reales a las animaciones. `animate.py`
  exporta ese fotograma (`*_fotograma.png`) junto al GIF.
  - **Estado actual:** la presentación usa fotograma fijo + nota (macro `\videohero`). Los 5 videos
    (`animaciones_presentacion_2026Q1G01S2.zip`) están **pendientes de subir a YouTube**. Cuando estén
    los enlaces, reemplazar `\videohero{base}{ancho}` por `\videolink{base}{ancho}{URL}` en el `.tex`
    (macro ya definido) — **no** dejar enlaces `run:` a archivos `.mp4` locales (llegan rotos al docente).

> **Camino canónico para los fotogramas hero del entregable:** usá **`scripts/generar_entrega.sh`**.
> Corre estas mismas corridas hero y exporta los fotogramas con el **nombre exacto que referencian los
> `.tex`** — es decir, **sin** el sufijo `_oeN` (`_oe1`/`_oe10`) que `run_matrix.py` agrega al tag del
> archivo. Si en cambio corrés `animate.animate(f)` **sin `outfile`** sobre los `.txt` hero, los PNG
> salen como `..._oe10_r1_fotograma.png` y **no** coinciden con los `\includegraphics` del informe. La
> receta manual de abajo replica ese recorte del sufijo pasando un `outfile` explícito.

**Generar las animaciones a mano** (corridas "hero" dedicadas, con `output_every=1` para que salgan suaves):

```bash
cd analysis

# 1) corridas hero para animar (pocas, output_every=1): dos extremos de densidad + los 3 órdenes
python3 run_matrix.py --out-dir ../data_anim --rule CONTACTO_PURO --protocol FIXED_N \
    --n 5 30 --p 0.1 --realizations 1 --output-every 1 --steps 2000
python3 run_matrix.py --out-dir ../data_anim --rule CONTACTO_PURO --protocol INCREMENTAL_180S \
    --order ASCENDING DESCENDING RANDOM --p 0.1 --realizations 1 --output-every 10

# 2) GIF + fotograma fijo (PNG) de cada corrida (clip de ~25 s en tiempo real).
#    Se pasa un outfile SIN "_oe" para que el nombre del fotograma empate con los .tex.
python3 - <<'PY'
import glob, os, re, sys; sys.path.insert(0, ".")
import animate
for f in sorted(glob.glob("../data_anim/*.txt")):
    base = os.path.basename(f)[:-4]              # sin .txt
    clean = re.sub(r"_oe\d+", "", base)          # quita _oe1 / _oe10 para empatar los nombres de los .tex
    out_gif = os.path.join("../data_anim", clean + ".gif")
    still = 6480 if base.startswith("INC") else None   # incrementales: fotograma en la fase N=10 (se distingue el orden)
    gif, png = animate.animate(f, outfile=out_gif, still_step=still)   # GIF (tiempo real) + <clean>_fotograma.png
    print("animación:", gif, "| fotograma:", png)
PY
```

**Para el entregable:** al publicar las animaciones, agregar los links reales debajo del
`*_fotograma.png` correspondiente. Las **fórmulas y ecuaciones** del informe y la
presentación van **numeradas y en LaTeX** (GuiaInformes): escalares en itálica, vectores en negrita,
unidades sin itálica; en las **figuras**, los ejes van en palabras con unidades (no en símbolos).

> Nota: un GIF en tiempo real de la corrida incremental completa (1080 s) sería enorme; por eso el hero
> incremental usa `--output-every 10` (queda acelerado ~10×, suficiente para ilustrar el efecto del
> orden). Para los extremos de densidad alcanza con el clip de ~25 s.

---

## 📦 Reproducir la entrega desde un clon limpio

Los directorios `data/`, `figures/` y `data_anim/` **no se versionan** (son grandes y regenerables;
ver [`.gitignore`](.gitignore)). Los **PDFs finales** (`informe/*.pdf`, `presentacion/*.pdf`) **sí se
versionan**: son el entregable y se pueden abrir sin compilar nada. Para regenerar todo —datos,
figuras, fotogramas hero y ambos PDFs— desde cero, con un solo comando:

```bash
scripts/generar_entrega.sh          # variante oficial CONTACTO_PURO (~8–12 min, ~0,85 GB en disco)
```

El script construye el motor, corre el barrido (1350 corridas: 900 N-fijo + 450 incremental, 30
realizaciones), calcula las figuras (`analyze.py --since-step 2000 --p-representativo 0.1`), la
validación triangular (`validacion.py`), los fotogramas hero (`animate.py`, nombres alineados a los
`.tex`) y compila informe y presentación (`pdflatex` ×2). Requiere JDK 21, Maven, Python 3.12 con
`analysis/requirements.txt` y `pdflatex` con `beamer`. El corte del estacionario (`--since-step 2000`)
quedó elegido por inspección de la evolución temporal y registrado por punto en
`figures/manifiesto.csv`. La integridad de los binarios versionados (ambos PDFs + el artículo
`extras/FD_VDV.pdf`) se puede verificar con `sha256sum -c SHA256SUMS`.

> **Entorno Python:** el script corre con las dependencias de `analysis/` (`numpy`, `matplotlib`,
> `scipy` de `requirements.txt`). Si creaste el venv en `analysis/.venv` (paso 2 de *Análisis*), el
> script lo **activa solo**; si preferís tu `python3` del sistema, activá el venv antes de correrlo
> (`source analysis/.venv/bin/activate`) o instalá `analysis/requirements.txt` en ese `python3`.

---

## Estado del proyecto

Ver la tabla de **hitos** al final del documento de diseño. Resumen:

- [x] Hito 0 — Spec de diseño
- [x] Hito 1 — Esqueleto Maven/Python (auditado)
- [x] Hito 2 — Motor NaSch (R1–R4, variante B) con tests de invariantes (TDD)
- [x] Hito 3 — Validación `p=0` (variante B) contra el diagrama fundamental analítico
- [x] Hito 4 — Variante A (contacto puro) + resolución de agrupamientos
- [x] Hito 5 — Matriz + observables Python (barrido corrido: 1350 corridas CONTACTO_PURO)
- [x] Hito 6 — Figuras + animación generadas; estacionario elegido por inspección (`--since-step 2000`)
- [x] Hitos 7–8 — informe y presentación finales (PDFs versionados; regenerables con `scripts/generar_entrega.sh`)
