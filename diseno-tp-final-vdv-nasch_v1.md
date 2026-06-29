# Diseño TP Final SdS — Nagel-Schreckenberg aplicado a *Vibration-Driven Vehicles*

**Materia:** 72.25 Simulación de Sistemas (ITBA, Prof. Daniel Parisi) — 2026 Q1
**Grupo:** G01S2 · **Modalidad:** grupal · **Stack:** Java/Maven (motor) + Python (análisis y animación)
**Fecha:** 2026-06-28 · **Versión:** v1 (spec de diseño + esqueleto inicial auditado)

> **Estado:** documento de diseño para revisión interna del grupo y contrato del esqueleto inicial.
> Doble propósito: (1) base de la sección *Modelo / Simulaciones* del informe, y (2) material para
> confirmar con el profesor las decisiones marcadas como **[CONFIRMAR]**.

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

## 2. El sistema real (resumen del artículo)

| Característica | Valor |
|---|---|
| Tipo de agente | Hexbug Nano (VDV), interactúan **solo por contacto** (sin sensado remoto) |
| Largo del vehículo | **44 mm** (cuerpo 44 × 15 × 18 mm) |
| Pista | Canal circular 1D, ancho 18 mm, **longitud efectiva ≈ 1313 mm** |
| Máximo de vehículos | **30** (a contacto: 30 × 44 mm ≈ 1320 mm ≈ pista) |
| Velocidad libre individual | **uniforme en 90–120 mm/s** (de 37 VDV descartaron el más rápido y el más lento → 30) |
| Captura | 24 fps; velocidades por diferencia finita de 4° orden |
| Protocolo | Arrancan con N=5, cada 180 s agregan 5, hasta N=30 (densidades crecientes) |
| Órdenes de inserción | creciente (*ascending*), decreciente (*descending*) y aleatorio (*random*) |

**Observables del artículo que debemos reproducir/comparar:**

1. **Velocidad media global vs N** (Fig. 2): `v̄ = ⟨L_i / 180 s⟩`. Decrece con N; las tres
   configuraciones convergen a N=30. Hallazgo clave: a saturación la velocidad media es **menor que la
   del VDV más lento** (colapso por agrupamientos).
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

- **Ruta unidimensional de un carril con condiciones periódicas**, discretizada en **L celdas**. La
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
  `v_i ← min(v_i, g_i)`. **Variante oficial confirmada: (A) contacto puro.** La (B) se implementa solo
  para validar el NaSch clásico contra la solución analítica (§8).
  - **(A) Contacto puro** *(oficial)*: el vehículo **no frena** mientras no alcance al de adelante.
    - si no alcanzaría al líder este paso → avanza libre;
    - si lo alcanzaría → **colisión**: avanza solo hasta quedar **inmediatamente detrás** del líder
      (cuerpos a contacto, `g = 0`, **sin solaparse**) y **hereda la velocidad del líder** para el paso
      siguiente.
  - **(B) Clásica salvo a distancia 0** *(solo validación)*: `v_i ← min(v_i, g_i)`; si `g_i = 0` toma
    `min(v_i, d_lider)` (acotado por la propia velocidad para que un seguidor lento no “teletransporte”).
  - En ambas, los vehículos en contacto forman **agrupamientos**. Implementado por relajación de
    desplazamientos finales `d_i ← min(deseada_i, g_i + d_lider)` hasta el mayor punto fijo (cada uno
    avanza lo máximo sin atravesar al líder); la velocidad heredada se propaga de adelante hacia atrás.
    En ruta totalmente llena el agrupamiento avanza rígido a la velocidad del más lento.

- **R3 — Frenado aleatorio.** Con probabilidad `p`, si `v_i > 0` → `v_i ← v_i − 1`.
  Si `p = 0` (NaSch determinista) esta regla nunca se aplica. Usa un PRNG **reproducible por realización**.

- **R4 — Movimiento.** `x_i ← (x_i + v_i) mod L`.

### 3.3 Heterogeneidad

Cada agente tiene su **velocidad máxima propia** `v_max,i`, derivada de una velocidad libre
`v_free,i ~ U[90,120] mm/s` (igual que los 30 VDV del artículo). Esto es **imprescindible** para
reproducir las Figs. 2 y 4 y para el estudio de órdenes creciente/decreciente/aleatorio (§6).

### 3.4 Esquema de actualización (decisiones explícitas — Parisi exige colisiones reproducibles)

- Actualización **síncrona** sobre snapshots inmutables (`CollisionContext`): R2 se resuelve a partir de
  los gaps y las velocidades deseadas, y recién después se aplica el resultado a la ruta (no depende del
  orden de iteración). El contrato `CollisionRule.resolve` devuelve, por vehículo, un **`Movimiento`**
  (desplazamiento de este paso + velocidad heredada para el siguiente).
- **Orden confirmado (resuelve la interacción R2/R3 y el no-solapamiento): `R1 (acelerar) → R3 (frenar
  la velocidad deseada) → R2 (proyectar desplazamientos sin solapar) → R4 (mover)`.** Como el frenado
  solo *reduce* el avance, proyectar los contactos al final **garantiza no-solapamiento jamás**. A
  `p = 0` el orden colapsa a `R1→R2→R4`; la **variante B** reproduce así el NaSch canónico y su diagrama
  analítico (§8). *(La variante A homogénea a `p=0` da flujo libre hasta el contacto; "el orden equivale
  al canónico" no significa "A = canónico".)*
- El motor es **100 % determinista dada la realización** (posiciones iniciales + `v_free,i` + secuencia
  reproducible del PRNG). Verificado: 0 solapamientos y reproducibilidad bit-a-bit.

---

## 4. Calibración continuo → malla discreta

La idea es elegir el paso espacial y temporal para que **una corrida sea directamente comparable con el
experimento** (ejes en mm/s y 1/mm) y las velocidades libres 90–120 mm/s caigan en enteros con buena
resolución.

| Cantidad | Símbolo | Valor | Origen |
|---|---|---|---|
| Paso espacial | `Δx` | **0.25 mm** | elegido (resolución de velocidad) |
| Paso temporal | `dt` | **1/24 s ≈ 0.0417 s** | cadencia de cámara (24 fps) → 1 paso = 1 frame |
| Cuanto de velocidad | `Δv = Δx/dt` | **6 mm/s** | derivado |
| Largo de vehículo | `ℓ` | 44 mm = **176 celdas** | artículo |
| Largo de pista | `L` | 1320 mm = **5280 celdas** | `30·ℓ` (cierre exacto a N=30) |
| Velocidad libre | `v_free,i` | `U[90,120]` mm/s | artículo (30 VDV uniformes) |
| Velocidad máx. (malla) | `v_max,i = round(v_free,i/Δv)` | **{15,…,20}** celdas/paso | derivado (6 clases) |
| Densidad global | `ρ = N/L_phys` | hasta **0.0227 1/mm** | derivado (N=30 → contacto) |
| Prob. de frenado | `p` | barrido (§6) | parámetro |

**Notas de calibración:**
- `Δx = 0.25 mm` es la perilla de resolución: más chico → más clases de velocidad pero la malla es más
  grande/lento. 0.25 mm da 6 clases de `v_max` (15–20) y una ruta de 5280 celdas (manejable, N≤30).
- Se fija `L = 30·ℓ = 5280` celdas (1320 mm) en vez de 1313 mm para que **N=30 cierre exactamente a
  contacto** (diferencia 0.5 % con el artículo; consistente con que el artículo también dice "≈ 1313 mm" y
  admite leve solapamiento/desalineación).
- **Sensibilidades obligatorias:** correr al menos comparaciones de control para `L=1313 mm` vs.
  `L=1320 mm`, y documentar si `dt=1/24 s` se usa como dinámica del autómata o como frecuencia de
  muestreo. Si el profesor pide una tasa física de frenado, convertir `p` por paso a `p(dt)=1-exp(-λdt)`.
- **Limitación honesta (va en Discusión del informe):** en NaSch la velocidad está acotada por la
  velocidad *media* libre (`v_max,i`), por lo que el modelo **no** reproduce la cola instantánea de
  hasta ~300 mm/s de la Fig. 4 (que viene del ruido instantáneo del robot vibrante). Esperamos
  reproducir bien la **forma y las tendencias** (PDF de densidad geométrica, corrimiento/angostamiento
  de la PDF de velocidad con N, caída del diagrama fundamental), no la coincidencia absoluta de la cola.

---

## 5. Parámetros vs. condiciones iniciales (distinción explícita — corrección recurrente de Parisi)

- **Parámetros del modelo:** `L`, `ℓ`, `Δx`, `dt`, `p`, `N`, el rango de velocidad libre `[90,120]`,
  la variante de R2, el orden de inserción y el protocolo de corrida.
- **Condiciones iniciales (cambian por realización):** posiciones iniciales de los vehículos, el valor
  concreto sorteado de `v_free,i` por agente, y el identificador reproducible del PRNG.

---

## 6. Matriz de experimentos

**Núcleo (lo que pidió el profe — variar N y p):** protocolo de **N fijo**.

| Estudio | Barrido | Fijo |
|---|---|---|
| Velocidad media vs **N** | `N ∈ {5,10,15,20,25,30}` (+ N finos para FD) | `p = 0.1` (y repetir para otros p) |
| Velocidad media vs **p** | `p ∈ {0, 0.1, 0.2, 0.3, 0.4}` | varios N |
| Validación determinista | `p = 0` | homogéneo (§8) |

- **Variante de R2:** validar primero **B** (clásica salvo 0); luego comparar **A** (contacto puro). El
  *default* del esqueleto es B por orden de implementación; la **primaria experimental** es A (ver Q1/§3.2).
- **Realizaciones:** arrancar con M=30 por combinación y aumentar si la velocidad media no estabiliza
  su error relativo. Reportar M, desvío entre realizaciones y criterio usado; no ocultar M como detalle
  de código.
- **Estacionario:** guardar evolución suficiente y elegir el corte **por inspección** del observable vs.
  tiempo. El corte final (`since_step`) debe quedar en un manifiesto de análisis; no usar descarte fijo
  en porcentaje.
- **`p > 0` para el colapso:** que la velocidad de saturación caiga **por debajo** de la del más lento
  (resultado central de la Fig. 2) solo emerge con frenado aleatorio (`p > 0`); a `p = 0` la saturación
  da exactamente la del más lento. Por eso la matriz incluye `p > 0` y la Discusión no debe atribuir el
  colapso al contacto puro por sí solo.
- **Singularidad N=30:** a N=30 la ruta queda exactamente a contacto (`30·ℓ = L`, ocupación de malla = 1, sin
  celdas libres). Es el punto de máxima densidad pero **singular** y dependiente de la variante
  (B ⇒ congelado, `Q=0`; A ⇒ crucero rígido a la del más lento); conviene no apoyar conclusiones de
  saturación únicamente en ese punto.

**Capa de comparación con el artículo (CONFIRMADA en alcance por el profe):**
- **Órdenes de inserción** `creciente / decreciente / aleatorio` + **protocolo incremental** cada 180 s.
  El artículo estudia explícitamente el efecto de la historia de inserción (Fig. 2); esta capa permite
  superponer sobre Figs. 2–5. Está **implementada** (enums `InsertionOrder`/`RunProtocol`, motor y
  matriz). En el orquestador es opt-in (`--protocol INCREMENTAL_180S`) para no inflar el barrido por
  defecto, pero forma parte del alcance entregable.
  - *Limitación conocida:* cerca de saturación la inserción geométrica en huecos no siempre llega a
    N=30 exacto si el espacio libre se fragmenta por debajo de ℓ (en una corrida de ejemplo se estabilizó
    en 29); los que no entran reintentan en el lote siguiente. El experimento físico los “encaja”; la
    inserción discreta no siempre. Documentado en el código.

**Extensiones (si da el tiempo):**
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

- **`p = 0` determinista, homogéneo y puntual** (`ℓ = 1` celda, `v_max` único), **con la variante B
  (clásica)**: el diagrama fundamental tiene solución analítica `Q(ρ) = min(ρ·v_max, 1−ρ)` (triangular,
  máximo en `ρ_c = 1/(v_max+1)`). Se compara la simulación contra esa curva exacta → valida el motor.
- **Importante (no confundir):** la validación analítica triangular es **solo de la variante B**. La
  variante A (contacto puro) **no** se valida contra esa curva: en el caso homogéneo `p=0` mantiene
  flujo libre hasta el contacto, coherente con el artículo (velocidad casi constante hasta
  `ρ ≈ 0.02`), pero distinta de la clásica. Que el orden `R1→R3→R2→R4` colapse a `R1→R2→R4` a
  `p=0` es una propiedad del **orden**, no implica "A = NaSch canónico".
- **Invariantes (tests):** N se conserva, nunca hay solapamiento de cuerpos, el orden periódico se
  preserva, y con `p=0` la corrida es bit-a-bit reproducible.
- Recién con el motor validado se pasa a la configuración **calibrada/heterogénea** (§4) para comparar
  con el artículo.

---

## 9. Arquitectura del software

### 9.1 Motor (Java / Maven) — `engine/`

Escribe **solo variables físicas**; sin color ni radio (corrección de Parisi en TP2). Módulos:

```
Vehicle            id, posición (cola), velocidad, vMax        (estado puro)
PeriodicTrack      L, ℓ; gaps periódicos; vecino más cercano
CollisionContext   snapshots inmutables para R2
CollisionRule      «interface { resolve(CollisionContext) }»
  ├ ContactoPuro   (variante A, primaria experimental)
  └ ClasicaSalvoCero (variante B; default inicial para validar NaSch clásico)
NaSchEngine        paso síncrono: R1 → R3(rng) → R2(rule) → R4
RandomBrake        PRNG reproducible por realización
Config             parámetros (L, ℓ, Δx, dt, N, p, rango v_free, rule, order, protocol, seed, pasos)
OutputWriter       escribe estado físico por paso (id, x_mm, v_mmps)
Main / CLI         corre UNA simulación dada una config
```

- Representación eficiente: vehículos en lista ordenada por posición (N ≤ 30) → gaps en O(N) por paso
  (no hace falta un array de 5280 celdas).
- **Salida:** un archivo por `(N, p, variante, orden, protocolo, realización)`. Formato compacto:
  bloques por paso de tiempo con `id  x[mm]  v[mm/s]` y cabecera de metadatos. Para decidir
  estacionario por inspección se debe conservar evolución suficiente; cualquier submuestreo se controla
  con `output_every`. `data/` va en `.gitignore`.

### 9.2 Orquestación y análisis (Python) — `analysis/`

```
run_matrix.py    invoca el jar sobre la matriz (N × p × variante × orden × protocolo × realizaciones)
run_io.py        carga archivos de salida
observables.py   velocidad media vs N/p, PDF densidad, PDF velocidad, diagrama fundamental,
                 detección de estacionario por inspección, error correcto entre realizaciones
plots.py         figuras del informe (una figura con curvas de colores; texto grande; log donde ayude)
animate.py       animación de la ruta (línea periódica horizontal); color DERIVADO de la velocidad (post-sim)
```

`analyze.py` no mezcla variantes, órdenes, protocolos ni valores de `p`: el diagrama fundamental queda
separado por esos metadatos. Para `INCREMENTAL_180S`, la velocidad media vs N se calcula con el N
realmente activo en cada paso registrado, agrupado por orden de inserción.

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
└── extras/          FD_VDV.pdf (artículo)        (ya está)
```

- **Nombres de entregables:** `SdS_TPFinal_2026Q1G01S2_Informe.pdf`,
  `SdS_TPFinal_2026Q1G01S2_Presentación.pdf`.
- **Código de grupo:** `G01S2` (confirmado). Nota: los TP2–TP5 previos se entregaron como `G01CS2`;
  para este TP se usa `G01S2`.

---

## 11. Decisiones (confirmadas con el profe el 2026-06-28)

1. **Semántica oficial de la R2:** **A (contacto puro)**. B queda solo para validar el NaSch clásico.
2. **Interacción R2/R3 y `v_líder`:** orden **R1 → R3 → R2 → R4**; la proyección de contactos al final
   garantiza no-solapamiento (el frenado solo reduce el avance). El seguidor, al colisionar, hereda la
   velocidad del líder. *(Decisión tomada por el grupo, coherente y verificada; conviene mencionarla en
   la defensa por si el profe prefiere otra convención — a p=0 es idéntica al NaSch canónico.)*
3. **Alcance de la comparación:** comparar **lo más posible** (cuantitativo donde el modelo lo permita),
   declarando la limitación de la cola instantánea (§4) en la Discusión.
4. **Órdenes de inserción + protocolo incremental:** **en alcance** (implementados; ver §6).
5. **`p`:** por paso de tiempo (criterio de Wikipedia). **`L` para densidad:** 1320 mm.

**Limitaciones/temas menores abiertos:** inserción incremental cerca de saturación (puede quedar en
N=29, §6); solo la variante B a p=0 tiene validación analítica cerrada (el resto se cubre con
invariantes: N conservado, sin solapamiento, orden periódico, reproducibilidad).

---

## 12. Plan de trabajo por etapas

| Hito | Entregable | Estado |
|---|---|---|
| 0 | **Este spec** revisado por el grupo | ✅ completado |
| 1 | Esqueleto Maven `engine/` + Python `analysis/` + README + `.gitignore` | ✅ completado (auditado) |
| 2 | Motor NaSch (R1–R4, variante B) con tests de invariantes (TDD) | ✅ completado |
| 3 | **Validación p=0** contra el diagrama fundamental analítico | ✅ completado |
| 4 | Variante A (contacto puro) + resolución de agrupamientos + tests | ✅ completado |
| 5 | Matriz (N, p, variante, orden, protocolo) + observables Python | ✅ motor+observables listos; **falta correr** las simulaciones |
| 6 | Figuras + animaciones + comparación con el artículo | ✅ código listo; comparación final tras correr barridos y elegir estacionario |
| 7 | Sensibilidades (`dt`, `L`, `Δx`) + doble carril si da el tiempo | pendiente |
| 8 | Informe (GuiaInformes) + presentación (20 min) con links a animaciones | pendiente (tras correr) |

> **Estado:** el **motor y el análisis están implementados y verificados** (39 tests Java + 13 pytest en
> verde; 0 solapamientos; reproducibilidad; flujo corrible que genera figuras del núcleo, incremental
> por orden, diagrama fundamental separado por metadatos y animación).
> Falta **correr** el barrido (lo hace el grupo) y, con esos resultados, escribir informe y presentación.

---

### Apéndice — correcciones de Parisi ya incorporadas al diseño

- Observables **post-simulación**, nunca dentro del motor. · Salida solo con **variables físicas** (sin
  color/radio). · Implementación = del modelo matemático al cómputo (no tipos de archivo). · Resultados:
  animación → evolución temporal → curva respuesta-estímulo, por parámetro; conclusiones al final. ·
  Estacionario **por inspección** (≠ sincronizado). · **"Realizaciones"**, no "seeds". · Cifras
  significativas acordes al error; **desvío bien calculado**. · Una figura con curvas de colores;
  texto de figuras grande; log donde ayude. · Español sin anglicismos. · Nombrar el método (autómata
  celular / dirigido por paso temporal), no "el TP X". · Distinguir **parámetros de condiciones iniciales**.
