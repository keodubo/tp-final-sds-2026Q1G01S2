# Diseño TP Final SdS — Nagel-Schreckenberg aplicado a *Vibration-Driven Vehicles*

**Materia:** 72.25 Simulación de Sistemas (ITBA, Prof. Daniel Parisi) — 2026 Q1
**Grupo:** G01CS2 · **Modalidad:** grupal · **Stack:** Java/Maven (motor) + Python (análisis y animación)
**Fecha:** 2026-06-28 · **Versión:** v1 (spec de diseño, previo a scaffolding)

> **Estado:** documento de diseño para revisión interna del grupo. Doble propósito: (1) base de la
> sección *Modelo / Simulaciones* del informe, y (2) material para confirmar con el profesor las
> decisiones marcadas como **[CONFIRMAR]**.

---

## 1. Contexto y objetivo

El profesor aceptó el modelo de **Nagel-Schreckenberg (NaSch)** pero propuso un escenario concreto
contra el cual validar: el experimento de **G. Patterson & D. Parisi, *"Fundamental diagram of
vibration-driven vehicles"*** (preprint, 2023; `extras/FD_VDV.pdf`). Allí se estudian robots Hexbug
Nano (*vibration-driven vehicles*, VDV) confinados a una **pista circular 1D**.

**Objetivo del TP:** reproducir por simulación ese sistema con una variante de NaSch (con la Regla 2
modificada por el profesor) y **comparar los observables de la simulación contra los del experimento**,
validando primero el motor con el caso determinista `p = 0`.

Esto encaja con el método de la materia (Autómatas Celulares, Unidad 3 / Teórica 2 — visto en teoría
pero no implementado en ningún TP) y aporta lo que más valora la cátedra: **validación contra un caso
conocido**.

---

## 2. El sistema real (resumen del paper)

| Característica | Valor |
|---|---|
| Tipo de agente | Hexbug Nano (VDV), interactúan **solo por contacto** (sin sensado remoto) |
| Largo del vehículo | **44 mm** (cuerpo 44 × 15 × 18 mm) |
| Pista | Canal circular 1D, ancho 18 mm, **longitud efectiva ≈ 1313 mm** |
| Máximo de vehículos | **30** (a contacto: 30 × 44 mm ≈ 1320 mm ≈ pista) |
| Velocidad libre individual | **uniforme en 90–120 mm/s** (de 37 VDV descartaron el más rápido y el más lento → 30) |
| Captura | 24 fps; velocidades por diferencia finita de 4° orden |
| Protocolo | Arrancan con N=5, cada 180 s agregan 5, hasta N=30 (densidades crecientes) |
| Órdenes de inserción | *ascending* (lentos primero), *descending* (rápidos primero), *random* |

**Observables del paper que debemos reproducir/comparar:**

1. **Velocidad media global vs N** (Fig. 2): `v̄ = ⟨L_i / 180 s⟩`. Decrece con N; las tres
   configuraciones convergen a N=30. Hallazgo clave: a saturación la velocidad media es **menor que la
   del VDV más lento** (colapso por clusters).
2. **PDF de densidades** (Fig. 3): densidad individual `ρ_i = 1/d_i`, con `d_i` = distancia al vecino
   más cercano sobre la pista. Pico en **ρ ≈ 0.023 1/mm = 1/44 mm** (distancia de contacto).
3. **PDF de velocidades** (Fig. 4): velocidad microscópica por VDV y por frame. Se **angosta y se
   corre a velocidades menores** al aumentar N.
4. **Diagrama fundamental** velocidad-densidad (Fig. 5): velocidad ~constante hasta `ρ ≈ 0.02 1/mm`
   (~11 % por encima del tamaño del vehículo) y luego cae. Reducción máxima 25–40 %.

**Mecanismo físico** (y por qué el profe modificó la R2): los VDV **no anticipan** — van a su velocidad
libre hasta que **chocan** físicamente con el de adelante, y recién ahí se frenan. No hay frenado
preventivo tipo conductor humano.

---

## 3. El modelo

### 3.1 Geometría

- **Ruta unidimensional con condiciones periódicas** (single-lane), discretizada en **L celdas**. La
  pista circular del experimento se modela como una **línea periódica**: lo que sale por un extremo
  reentra por el otro. La **curvatura no entra** en el modelo — la dinámica de NaSch depende solo de
  la coordenada 1D a lo largo de la pista, así que es equivalente a la pista circular real.
- Vehículos como partículas **extendidas**: cada uno ocupa `ℓ` celdas (no es el NaSch puntual de libro;
  es necesario para tener resolución de velocidad — ver §4).
- Convención de posición: `x_i` = celda de **cola** del vehículo `i`; su cuerpo ocupa
  `[x_i, x_i + ℓ − 1]` (módulo L). Los vehículos se indexan por orden a lo largo de la ruta (periódico).
- **Gap** (huecos libres delante de `i`): `g_i = (x_{i+1} − (x_i + ℓ)) mod L`. A contacto, `g_i = 0`.

### 3.2 Las cuatro reglas (actualización síncrona por paso de tiempo)

Para cada vehículo `i`, con velocidad entera `v_i ∈ {0,…,v_max,i}` (celdas/paso):

- **R1 — Aceleración.** `v_i ← min(v_i + 1, v_max,i)`.
  Si no llegó a su velocidad máxima, acelera una unidad.

- **R2 — Resolución de colisión (modificada por el profe).** Reemplaza la R2 clásica anticipatoria
  `v_i ← min(v_i, g_i)`. Dos variantes a comparar (**[CONFIRMAR]** cuál es la oficial):
  - **(A) Contacto puro** *(primaria — matchea el paper)*: el vehículo **no frena** mientras no alcance
    al de adelante.
    - si `v_i ≤ g_i` → avanza libre a `v_i`;
    - si `v_i > g_i` → **colisión**: toma la velocidad del líder `v_i ← v_{i+1}` y queda **pegado**
      (a contacto) detrás de él.
  - **(B) Clásica salvo a distancia 0**: `v_i ← min(v_i, g_i)` (anticipa), pero si `g_i = 0` entonces
    `v_i ← v_{i+1}` (en vez de quedar en 0).
  - En ambas, los vehículos en contacto forman **clusters** que se mueven a la velocidad del que va
    al frente del cluster (en una ruta totalmente llena, todos a la mínima).

- **R3 — Frenado aleatorio.** Con probabilidad `p`, si `v_i > 0` → `v_i ← v_i − 1`.
  Si `p = 0` (NaSch determinista) esta regla nunca se aplica. Usa un PRNG **sembrado por realización**.

- **R4 — Movimiento.** `x_i ← (x_i + v_i) mod L`.

### 3.3 Heterogeneidad

Cada agente tiene su **velocidad máxima propia** `v_max,i`, derivada de una velocidad libre
`v_free,i ~ U[90,120] mm/s` (igual que los 30 VDV del paper). Esto es **imprescindible** para reproducir
las Figs. 2 y 4 y para el estudio de órdenes *ascending/descending/random* (extensión, §6).

### 3.4 Esquema de actualización (decisiones explícitas — Parisi exige colisiones reproducibles)

- Actualización **síncrona/paralela**: las velocidades nuevas se calculan a partir de la configuración
  al **inicio** del paso; luego se mueven todos. `v_{i+1}` en R2 se toma de esa configuración inicial
  (decisión documentada; **[CONFIRMAR]** con el profe si prefiere la velocidad del líder *post*-R1/R3).
- **Sin solapamiento garantizado:** en la variante A el desplazamiento se resuelve por clusters
  (cadenas de vehículos a contacto) recorriendo la ruta desde un vehículo libre; en la variante B el
  `min(v_i, g_i)` ya impide el solapamiento. El algoritmo exacto de resolución de clusters se fija en la
  fase de implementación con tests de invariantes (sin solapamiento, N conservado).
- El motor es **100 % determinista dada la semilla** (posiciones iniciales + `v_free,i` + secuencia del
  PRNG).

---

## 4. Calibración continuo → lattice

La idea es elegir el paso espacial y temporal para que **una corrida sea directamente comparable con el
experimento** (ejes en mm/s y 1/mm) y las velocidades libres 90–120 mm/s caigan en enteros con buena
resolución.

| Cantidad | Símbolo | Valor | Origen |
|---|---|---|---|
| Paso espacial | `Δx` | **0.25 mm** | elegido (resolución de velocidad) |
| Paso temporal | `dt` | **1/24 s ≈ 0.0417 s** | cadencia de cámara (24 fps) → 1 paso = 1 frame |
| Cuanto de velocidad | `Δv = Δx/dt` | **6 mm/s** | derivado |
| Largo de vehículo | `ℓ` | 44 mm = **176 celdas** | paper |
| Largo de pista | `L` | 1320 mm = **5280 celdas** | `30·ℓ` (cierre exacto a N=30) |
| Velocidad libre | `v_free,i` | `U[90,120]` mm/s | paper (30 VDV uniformes) |
| Velocidad máx. (lattice) | `v_max,i = round(v_free,i/Δv)` | **{15,…,20}** celdas/paso | derivado (6 clases) |
| Densidad global | `ρ = N/L_phys` | hasta **0.0227 1/mm** | derivado (N=30 → contacto) |
| Prob. de frenado | `p` | barrido (§6) | parámetro |

**Notas de calibración:**
- `Δx = 0.25 mm` es la perilla de resolución: más chico → más clases de velocidad pero lattice más
  grande/lento. 0.25 mm da 6 clases de `v_max` (15–20) y una ruta de 5280 celdas (manejable, N≤30).
- Se fija `L = 30·ℓ = 5280` celdas (1320 mm) en vez de 1313 mm para que **N=30 cierre exactamente a
  contacto** (diferencia 0.5 % con el paper; consistente con que el paper también dice "≈ 1313 mm" y
  admite leve solapamiento/desalineación).
- **Limitación honesta (va en Discusión del informe):** en NaSch la velocidad está acotada por la
  velocidad *media* libre (`v_max,i`), por lo que el modelo **no** reproduce la cola instantánea de
  hasta ~300 mm/s de la Fig. 4 (que viene del ruido instantáneo del robot vibrante). Esperamos
  reproducir bien la **forma y las tendencias** (PDF de densidad geométrica, corrimiento/angostamiento
  de la PDF de velocidad con N, caída del diagrama fundamental), no el match absoluto de la cola.

---

## 5. Parámetros vs. condiciones iniciales (distinción explícita — corrección recurrente de Parisi)

- **Parámetros del modelo:** `L`, `ℓ`, `Δx`, `dt`, `p`, `N`, el rango de velocidad libre `[90,120]`,
  la variante de R2.
- **Condiciones iniciales (cambian por realización):** posiciones iniciales de los vehículos, el valor
  concreto sorteado de `v_free,i` por agente, y la semilla del PRNG.

---

## 6. Matriz de experimentos

**Núcleo (lo que pidió el profe — variar N y p):**

| Estudio | Barrido | Fijo |
|---|---|---|
| Velocidad media vs **N** | `N ∈ {5,10,15,20,25,30}` (+ N finos para FD) | `p = 0.1` (y repetir para otros p) |
| Velocidad media vs **p** | `p ∈ {0, 0.1, 0.2, 0.3, 0.4}` | varios N |
| Validación determinista | `p = 0` | homogéneo (§8) |

- **Variante de R2:** correr A y B y comparar (decisión Q2).
- **Realizaciones:** M por cada `(N, p)` (M a determinar por convergencia; arrancamos con ~30–50).
- **Estacionario:** se descarta el transitorio **por inspección** del observable vs. tiempo, no con un
  porcentaje fijo (corrección de Parisi en TP2/TP3).

**Extensiones (si da el tiempo / si el profe quiere acercarse más al paper):**
- Órdenes de inserción **ascending / descending / random** (Fig. 2) usando la heterogeneidad de `v_free`.
- Protocolo **incremental** (agregar 5 cada 180 s) en vez de N fijo, para replicar el experimento tal cual.
- Doble carril con cambio de carril.

---

## 7. Observables (todos **post-simulación**, desde los archivos de salida)

> Regla de oro de la cátedra: **ningún observable se calcula dentro del motor**; el motor solo escribe
> estado físico (id, posición, velocidad) y el análisis Python computa todo después.

1. **Velocidad media global vs N** (≈ Fig. 2): por vehículo `v̄_i = (celdas avanzadas / pasos)·Δv`
   [mm/s], promediada sobre `i` y sobre realizaciones. Error: **desvío correcto entre realizaciones**
   (no promedio-de-promedios subrepresentado — corrección de Parisi en TP2).
2. **PDF de densidades** (≈ Fig. 3): `ρ_i = 1 / (Δx·(ℓ + g_i^{vecino más cercano}))` [1/mm], sobre todos
   los vehículos y todos los pasos del estacionario. Esperado: pico en `1/44 mm`.
3. **PDF de velocidades** (≈ Fig. 4): `v_i(t)·Δv` [mm/s] sobre todos los vehículos y pasos del
   estacionario; un panel por N (curvas de colores en **una sola figura**, Parisi).
4. **Diagrama fundamental** (≈ Fig. 5): velocidad instantánea vs. densidad local `ρ_i`, con media móvil.
5. **Evolución temporal** de la velocidad media (para detectar el estacionario por inspección).

**Curva respuesta-estímulo** (estructura que pide Parisi en Resultados): respuesta = velocidad media;
estímulos = `N` y `p`.

---

## 8. Validación

- **`p = 0` determinista, homogéneo y puntual** (`ℓ = 1` celda, `v_max` único): el diagrama fundamental
  tiene solución analítica clásica `Q(ρ) = min(ρ·v_max, 1−ρ)` (triangular, máximo en `ρ_c = 1/(v_max+1)`).
  Se compara la simulación contra esa curva exacta → valida el motor.
- **Invariantes (tests):** N se conserva, nunca hay solapamiento de cuerpos, el orden periódico se
  preserva, y con `p=0` la corrida es bit-a-bit reproducible.
- Recién con el motor validado se pasa a la configuración **calibrada/heterogénea** (§4) para comparar
  con el paper.

---

## 9. Arquitectura del software

### 9.1 Motor (Java / Maven) — `engine/`

Escribe **solo variables físicas**; sin color ni radio (corrección de Parisi en TP2). Módulos:

```
Vehicle            id, posición (cola), velocidad, vMax        (estado puro)
Ring               L, ℓ; gaps periódicos; vecino más cercano
CollisionRule      «interface { resolve(...) }»
  ├ ContactoPuro   (variante A, primaria)
  └ ClasicaSalvo0  (variante B)
NaSchEngine        paso síncrono: R1 → R2(rule) → R3(rng) → R4
RandomBrake        PRNG sembrado por realización
Config             parámetros (L, ℓ, Δx, dt, N, p, rango v_free, rule, seed, pasos, transitorio)
OutputWriter       escribe estado físico por paso (id, x_mm, v_mmps)
Main / CLI         corre UNA simulación dada una config
```

- Representación eficiente: vehículos en lista ordenada por posición (N ≤ 30) → gaps en O(N) por paso
  (no hace falta un array de 5280 celdas).
- **Salida:** un archivo por `(N, p, variante, realización)`. Formato compacto: bloques por paso de
  tiempo con `id  x[mm]  v[mm/s]`. Se escriben solo los pasos del régimen a analizar (configurable) para
  no explotar en tamaño. `data/` va en `.gitignore`.

### 9.2 Orquestación y análisis (Python) — `analysis/`

```
run_matrix.py    invoca el jar sobre la matriz (N × p × variante × realizaciones) vía subprocess
io.py            carga archivos de salida
observables.py   velocidad media vs N/p, PDF densidad, PDF velocidad, diagrama fundamental,
                 detección de estacionario por inspección, error correcto entre realizaciones
plots.py         figuras del informe (una figura con curvas de colores; texto grande; log donde ayude)
animate.py       animación de la ruta (línea periódica horizontal); color DERIVADO de la velocidad (post-sim)
```

### 9.3 Flujo

```
Config → [ Java NaSchEngine ] → archivos físicos (data/) → [ Python observables ] → figuras/ + animaciones
```

---

## 10. Estructura del repo y convenciones

```
tp-final-sds-2026Q1G01S2/
├── diseno-tp-final-vdv-nasch_v1.md   (este documento)
├── README.md · CLAUDE.md
├── engine/          pom.xml, src/main/java/..., src/test/java/...
├── analysis/        requirements.txt, *.py
├── data/            salidas del motor            (gitignored)
├── figures/         figuras generadas
└── extras/          FD_VDV.pdf (paper)           (ya está)
```

- **Nombres de entregables** (según tus TPs previos): `SdS_TPFinal_2026Q1G01CS2_Informe.pdf`,
  `SdS_TPFinal_2026Q1G01CS2_Presentación.pdf`.
- **[CONFIRMAR] inconsistencia de código de grupo:** la carpeta del repo dice `G01S2`, pero tus
  entregables de TP2–TP5 y la memoria dicen `G01CS2`. Conviene unificar (probablemente `G01CS2`).

---

## 11. Decisiones abiertas a confirmar con el profe

1. **Semántica oficial de la R2** (variante A vs. B; y si `v_{i+1}` es del inicio o del fin del paso).
   Proponemos A (contacto puro) como primaria y mostramos ambas.
2. **Protocolo:** N fijo por corrida (estándar para el diagrama fundamental) vs. incremental cada 180 s
   (réplica exacta del experimento). Proponemos N fijo en el núcleo, incremental como extensión.
3. **Alcance de la comparación:** ¿basta con tendencias/formas (dado el límite de la cola instantánea,
   §4) o esperan match cuantitativo de la Fig. 4?
4. ¿Incluimos los órdenes ascending/descending/random (Fig. 2) en el núcleo o como extensión?

---

## 12. Plan de trabajo por etapas

| Hito | Entregable | Estado |
|---|---|---|
| 0 | **Este spec** revisado por el grupo | ⏳ en revisión |
| 1 | Scaffold: Maven `engine/` + esqueleto Python `analysis/` + README + `.gitignore` | pendiente |
| 2 | Motor NaSch (R1–R4, variante B) con tests de invariantes (TDD) | pendiente |
| 3 | **Validación p=0** contra el diagrama fundamental analítico | pendiente |
| 4 | Variante A (contacto puro) + resolución de clusters + tests | pendiente |
| 5 | Calibración + corrida de la matriz (N, p) + observables Python | pendiente |
| 6 | Figuras + animaciones + comparación con el paper | pendiente |
| 7 | Extensiones (órdenes, incremental, doble carril) si da el tiempo | pendiente |
| 8 | Informe (GuiaInformes) + presentación (20 min) con links a animaciones | pendiente |

---

### Apéndice — correcciones de Parisi ya incorporadas al diseño

- Observables **post-simulación**, nunca dentro del motor. · Salida solo con **variables físicas** (sin
  color/radio). · Implementación = del modelo matemático al cómputo (no tipos de archivo). · Resultados:
  animación → evolución temporal → curva respuesta-estímulo, por parámetro; conclusiones al final. ·
  Estacionario **por inspección** (≠ sincronizado). · **"Realizaciones"**, no "seeds". · Cifras
  significativas acordes al error; **desvío bien calculado**. · Una figura con curvas de colores;
  texto de figuras grande; log donde ayude. · Español sin anglicismos. · Nombrar el método (autómata
  celular / dirigido por paso temporal), no "el TP X". · Distinguir **parámetros de condiciones iniciales**.
```
