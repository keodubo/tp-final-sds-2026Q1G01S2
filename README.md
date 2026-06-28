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

> **Estado actual:** esqueleto auditado. La geometría de la ruta periódica, la E/S y el CLI básico
> están implementados y testeados; el paso de simulación (R1–R4), la inicialización física y las
> reglas de colisión siguen como pendientes a completar con TDD (ver hitos en el documento de
> diseño). `mvn test` pasa en verde con lo ya implementado.

### 2. Análisis (Python)

```bash
cd analysis
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 run_matrix.py --help     # orquesta N × p × variante × orden × protocolo × realizaciones
```

---

## Estado del proyecto

Ver la tabla de **hitos** al final del documento de diseño. Resumen:

- [x] Hito 0 — Spec de diseño
- [~] Hito 1 — Esqueleto Maven/Python auditado
- [ ] Hito 2 — Motor NaSch (R1–R4) con tests de invariantes (TDD)
- [ ] Hito 3 — Validación `p=0` contra el diagrama fundamental analítico
- [ ] Hitos 4–8 — variante de contacto, calibración, observables, figuras, informe y presentación
