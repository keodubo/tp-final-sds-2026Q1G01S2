# TP Final — Nagel-Schreckenberg aplicado a *Vibration-Driven Vehicles*

**72.25 Simulación de Sistemas** (ITBA, Prof. Daniel Parisi) — 2026 Q1 · Grupo **G01S2**

Simulación de tráfico 1D con un autómata celular de **Nagel-Schreckenberg** (Regla 2 modificada
por contacto) aplicado al experimento de robots *vibration-driven vehicles* (Hexbug) de
Patterson & Parisi. El objetivo es **reproducir por simulación los observables del experimento y
compararlos** (ver el artículo en [`extras/FD_VDV.pdf`](extras/FD_VDV.pdf)).

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
> (en el caso homogéneo `p=0`, la variante A da flujo libre hasta el contacto). `mvn test` → 39 tests
> en verde; 0 solapamientos y reproducibilidad bit-a-bit verificadas. El motor escribe **solo estado
> físico**; los observables se calculan después (Python).

### 2. Análisis (Python)

```bash
cd analysis
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 -m pytest tests -q                 # tests de comportamiento de los observables
```

#### ⭐ Barrido completo del TP — comando recomendado (fijado)

Corre **todas las variaciones** que diseñamos: ambas variantes de R2 (A contacto puro + B clásica),
ambos protocolos (N fijo + incremental), los 3 órdenes de inserción, `N ∈ {5,10,15,20,25,30}`,
`p ∈ {0, 0.1, 0.2, 0.3, 0.4}` y 30 realizaciones. Son **~2700 corridas** (~8–12 min, ~1,3 GB en disco
gracias a `--output-every 10`). Los observables se calculan **después**, nunca durante la simulación.

```bash
cd analysis

# 1) GENERAR todas las corridas del TP
python3 run_matrix.py --out-dir ../data \
    --rule CONTACTO_PURO CLASICA_SALVO_CERO \
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

# 4) Animación (GIF) de una corrida representativa
python3 -c "import animate; animate.animate('../data/<archivo>.txt')"
```

**Notas:**
- `--output-every 10` reduce disco/RAM/tiempo ~10× con pérdida estadística despreciable (los cuadros
  consecutivos están correlacionados). Para FIXED_N el `--order` se ignora (sólo importa en el incremental),
  así que no genera corridas redundantes.
- **Más rápido / menos disco:** bajar `--realizations` (p. ej. 20) si el error entre realizaciones ya estabiliza.
- **Solo el dataset experimental** (variante oficial A, protocolo del artículo):
  `python3 run_matrix.py --out-dir ../data --rule CONTACTO_PURO --protocol INCREMENTAL_180S --order ASCENDING DESCENDING RANDOM --output-every 10`

---

## 🎬 Animaciones (siguen las guías de formato)

Estándar de la cátedra (`docs/Guias de Formato/GuiaPresentaciones.pdf`, puntos 2.4.1, 2.4.8 y 1.7–1.9),
ya implementado en `animate.py`:

- Una **animación característica por parámetro estudiado**, idealmente con **dos valores extremos** para
  mostrar comportamientos distintos: p. ej. **baja densidad (N=5, flujo libre)** vs **alta densidad
  (N=30, congestión)**; y los **tres órdenes** de inserción en el protocolo incremental.
- Ejes con leyenda **en palabras + unidad MKS** (`posición (mm)`), **fuente ≥ 20**, **barra de color**
  rotulada (`velocidad (mm/s)`), tiempo en segundos, y los **parámetros fijos al costado** de la figura.
- **Tiempo real** por defecto (24 fps si la corrida se generó con `--output-every 1`, igual que la
  cámara del experimento de 24 fps).
- ⚠️ En el **PDF entregable NO van animaciones ni se entregan archivos de animación**: va una **imagen
  fija** de un fotograma representativo y, **debajo, un link a YouTube** (o similar). `animate.py`
  exporta ese fotograma (`*_fotograma.png`) junto al GIF.

**Generar las animaciones** (corridas "hero" dedicadas, con `output_every=1` para que salgan suaves):

```bash
cd analysis

# 1) corridas hero para animar (pocas, output_every=1): dos extremos de densidad + los 3 órdenes
python3 run_matrix.py --out-dir ../data_anim --rule CONTACTO_PURO --protocol FIXED_N \
    --n 5 30 --p 0.1 --realizations 1 --output-every 1 --steps 2000
python3 run_matrix.py --out-dir ../data_anim --rule CONTACTO_PURO --protocol INCREMENTAL_180S \
    --order ASCENDING DESCENDING RANDOM --p 0.1 --realizations 1 --output-every 10

# 2) GIF + fotograma fijo (PNG) de cada corrida (clip de ~25 s en tiempo real)
python3 - <<'PY'
import sys, glob; sys.path.insert(0, ".")
import animate
for f in sorted(glob.glob("../data_anim/*.txt")):
    gif, png = animate.animate(f)         # GIF (tiempo real) + *_fotograma.png
    print("animación:", gif, "| fotograma:", png)
PY
```

**Para el entregable:** subí cada GIF/MP4 a YouTube (no listado) y en el informe/presentación poné el
`*_fotograma.png` correspondiente **con el link debajo**. Las **fórmulas y ecuaciones** del informe y la
presentación van **numeradas y en LaTeX** (GuiaInformes): escalares en itálica, vectores en negrita,
unidades sin itálica; en las **figuras**, los ejes van en palabras con unidades (no en símbolos).

> Nota: un GIF en tiempo real de la corrida incremental completa (1080 s) sería enorme; por eso el hero
> incremental usa `--output-every 10` (queda acelerado ~10×, suficiente para ilustrar el efecto del
> orden). Para los extremos de densidad alcanza con el clip de ~25 s.

---

## Estado del proyecto

Ver la tabla de **hitos** al final del documento de diseño. Resumen:

- [x] Hito 0 — Spec de diseño
- [x] Hito 1 — Esqueleto Maven/Python (auditado)
- [x] Hito 2 — Motor NaSch (R1–R4, variante B) con tests de invariantes (TDD)
- [x] Hito 3 — Validación `p=0` (variante B) contra el diagrama fundamental analítico
- [x] Hito 4 — Variante A (contacto puro) + resolución de agrupamientos
- [x] Hito 5 — Matriz + observables Python (**falta correr** el barrido)
- [x] Hito 6 — Código de figuras + animación (la comparación final requiere correr el barrido y elegir estacionario)
- [ ] Hitos 7–8 — sensibilidades, informe y presentación (tras correr las simulaciones)
