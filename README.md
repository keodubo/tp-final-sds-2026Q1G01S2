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
> INCREMENTAL_180S, con validación `p=0` contra el diagrama fundamental analítico. `mvn test` → 39 tests
> en verde; 0 solapamientos y reproducibilidad bit-a-bit verificadas. El motor escribe **solo estado
> físico**; los observables se calculan después (Python).

### 2. Análisis (Python)

```bash
cd analysis
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 -m pytest tests -q                 # tests blackbox de los observables

# pipeline completo (los observables se calculan DESPUÉS de las corridas):
python3 run_matrix.py --out-dir ../data    # 1) genera las corridas (núcleo N×p, N fijo)
python3 analyze.py --data-dir ../data \
        --figures-dir ../figures           # 2) calcula observables y genera las figuras
python3 -c "import animate; animate.animate('../data/<archivo>.txt')"  # 3) animación (GIF)
```

> `run_matrix.py` por defecto corre solo el **núcleo** (N × p × variante × realizaciones, N fijo).
> Los **órdenes** de inserción y el **protocolo incremental** son opt-in
> (`--protocol INCREMENTAL_180S --order ASCENDING DESCENDING RANDOM`).

---

## Estado del proyecto

Ver la tabla de **hitos** al final del documento de diseño. Resumen:

- [x] Hito 0 — Spec de diseño
- [x] Hito 1 — Esqueleto Maven/Python (auditado)
- [x] Hito 2 — Motor NaSch (R1–R4, variante B) con tests de invariantes (TDD)
- [x] Hito 3 — Validación `p=0` contra el diagrama fundamental analítico
- [x] Hito 4 — Variante A (contacto puro) + resolución de agrupamientos
- [x] Hito 5 — Matriz + observables Python (**falta correr** el barrido)
- [x] Hito 6 — Figuras + animación (código listo; se generan al correr)
- [ ] Hitos 7–8 — sensibilidades, informe y presentación (tras correr las simulaciones)
