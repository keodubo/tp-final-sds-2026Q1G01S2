# Bitácora — Loop de auditoría/corrección TP Final SdS (agente)

**Fecha:** 2026-07-06
**Rama:** `fable/tp-final-auditoria-integral-v1`
**Commit inicial:** `4fde54b` (`docs: agregar loop de subagentes al handoff`)
**Handoff seguido:** `2026-07-06_handoff-tp-final-auditoria_v1.md`
**Entorno:** Linux WSL2. JDK 21 portable (`~/.local/java/jdk-21.0.5+11`), Maven 3.8.7, Python 3.12
(venv aislado con `uv`, numpy 2.5.1 / scipy 1.18.0 / pytest 9.1.1), pdflatex + beamer disponibles.
`sudo` pide password (no se instalan paquetes de sistema).

## Fase 0 — Baseline (antes de corregir)

| Verificación | Resultado baseline | Estado |
|---|---|---|
| `mvn -f engine/pom.xml test` (JAVA_HOME portable) | **57 tests, 0 fallas** | ✅ verde |
| `pytest analysis/tests -q` | **1 falla / 31 pasan** → `np.trapz` removido en NumPy 2.0 | ❌→✅ (ver F1) |
| `pdflatex` presentación (clean checkout) | **FALLA**: falta `N5_..._fotograma.png` (figuras gitignoreadas) | ❌ (P0 B1/A5) |
| `pdflatex` informe (clean checkout) | **FALLA**: mismas figuras faltantes | ❌ (P0 B1/A5) |
| Anti-placeholders (`rg`) | pendiente | ⏳ |

### Cambios locales ajenos
Ninguno: checkout limpio de `origin/fable/tp-final-auditoria-integral-v1`. `git status` limpio al inicio.

## Hallazgos de baseline (pre-loop)

- **F1 [P1] `np.trapz` removido en NumPy 2.0** — `analysis/tests/test_observables.py:127`. Con deps
  flotantes (`numpy>=1.26`) un install fresco trae numpy 2.x y el test rompe.
  **Fix aplicado:** helper version-agnóstico (`np.trapezoid or np.trapz`). Solo test, sin tocar producción.
  **Verificación:** `pytest tests -q` → **32 passed**. ✅
- **F2 [P0] Entregables no compilan desde clean checkout (B1/A5)** — `figures/` y `data_anim/` están
  gitignoreados y vacíos; los `.tex` referencian 16 PNG (11 de análisis + 5 fotogramas hero).
  Dos mismatches de nombres: (a) `FIXED_N` genera `..._sin_orden_fixed.png` pero los `.tex` pedían
  `..._random_fixed.png` (residual de la canonicalización M1); (b) `run_matrix.py`/`animate.py`
  producían fotogramas con `_oe1_`/`_oe10_` pero los `.tex` los piden sin `_oe`.
  **Fix aplicado:**
  1. Sweep CONTACTO_PURO 1350 corridas (900 FIXED + 450 INCREMENTAL, 30 realizaciones) → `data/`.
  2. `analyze.py --since-step 2000 --p-representativo 0.1` → 19 figuras + `manifiesto.csv`; `validacion.py`.
  3. `scripts/generar_entrega.sh`: pipeline reproducible; anima los hero pasando `outfile` sin `_oe`.
  4. `.tex`: `contacto_puro_random_fixed` → `contacto_puro_sin_orden_fixed` (4 refs informe, 2 presentación).
  5. `.gitignore`: se versionan los PDFs finales (ambos); intermedios LaTeX (incl. `.nav/.snm/.vrb`) ignorados.
  6. README: sección "Reproducir la entrega" + hitos actualizados.
  **Verificación:** todas las figuras referenciadas existen; **informe compila (11 págs, 1.44 MB)** y
  **presentación compila (17 págs, 974 KB)** con `pdflatex ×2`, exit 0, sin alias manuales.
  Anti-placeholders: PDFs LIMPIOS (sin COMPLETAR/XXXX/seed/1-44mm/URLs ficticias). ✅ P0 cerrado.

## Fase 0 — Baseline FINAL (post-fixes pre-loop)

| Verificación | Resultado |
|---|---|
| `mvn -f engine/pom.xml test` | **57 tests, 0 fallas** ✅ |
| `pytest analysis/tests -q` | **32 passed** ✅ (F1) |
| `pdflatex` informe ×2 | **exit 0, 11 págs** ✅ (F2) |
| `pdflatex` presentación ×2 | **exit 0, 17 págs** ✅ (F2) |
| Anti-placeholders (pdftotext + rg) | **LIMPIO** ✅ |

## Comandos corridos (Fase 0)
```
JAVA_HOME=~/.local/java/jdk-21.0.5+11 mvn -q -f engine/pom.xml test        # 57 verde
uv venv .venv && uv pip install -r requirements.txt                        # venv aislado
pytest tests -q                                                            # 1 fail (trapz) -> 32 pass tras F1
pdflatex ... Presentacion.tex / Informe.tex                                # fallan por figuras faltantes
mvn -DskipTests package                                                    # jar OK
# timing: 1 corrida FIXED ~0.32s, INCREMENTAL ~0.40s
```

## Agentes lanzados

### Ronda 1 — 6 auditores read-only (workflow, 738K tokens, ~15 min)
Personalidades: físico-Parisi, motor-paranoico, estadística-escéptica, editor-académico,
release-reproducibilidad, jurado-adversarial. Reejecutaron cálculos sobre los 1350 datos reales
(velocidades por N/p, checker de solapamiento por frame = 0, error ddof=1 entre realizaciones).

**28 hallazgos: 1 P0, 3 P1, 7 P2, 17 P3.** Backlog deduplicado:

| # | Sev | Dominio | Hallazgo | Fix |
|---|---|---|---|---|
| 1 | P0 | repro | Informe PDF no versionado (README/.gitignore prometen que sí) | commitear PDFs finales |
| 2 | P1 | docs | Figs 8-11 flotan tras Conclusiones/Referencias (floats `[h]`) | `float` + `[H]`/FloatBarrier + clearpage |
| 3 | P1 | docs | "velocidad ≈ libre media (105)" pero datos → gobierna el más lento (~90-95) | reformular + mecanismo de agrupamiento |
| 4 | P2 | repro | `generar_entrega.sh` no activa venv | activar `.venv` si existe + nota README |
| 5 | P2 | analysis | Etiquetas de figuras en inglés (enums) | mapear a español en analyze/animate/plots + regenerar |
| 6 | P2 | analysis | Línea punteada = sugerencia detect_stationary (~420), no el corte 2000 usado | dibujar en since_step + regenerar |
| 7 | P2 | analysis | `output_every` en clave de dedup pero no en agrupamiento (doble conteo latente) | sacar oe de `_logical_run_key` |
| 8 | P2 | docs | p≥0.3 congela a ~0 (gridlock) no declarado | cuantificar en texto/caption |
| 9 | P2 | docs | "reproducen las distribuciones" sobreafirma | → "tendencia de angostamiento" + limitación |
| 10 | P3 | docs | Conteos de tests 39→57, 13→32 (README+diseño) | actualizar o genérico |
| 11 | P3 | analysis | `velocity_pdf` sin guarda de vacío (NaN) | agregar guarda como density_pdf |
| 12 | P3 | engine | Guard muerto `g<0` en PeriodicTrack.isConsistent | eliminar/comentar |
| 13 | P3 | analysis | Leyenda "contacto (1/44 mm)" (lee como mm) | → "1/(44 mm)" en plots + regenerar |
| 14 | P3 | docs | "snapshot" anglicismo | → "instantánea inmutable" |
| 15 | P3 | docs | "Links a animaciones al publicar" (relleno) | redacción neutral cerrada |
| 16 | P3 | docs | Fotogramas hero ilegibles (0.32/0.48 linewidth) | 1 por fila ~0.9 |
| 17 | P3 | docs | write-before-step no documentado en informe | agregar frase en Implementación |
| 18 | P3 | docs | "por punto" sobre-vende trazabilidad del corte | redacción "corte único por inspección" |
| 19 | P3 | docs | README "barrido recomendado" incluye B sobre grilla calibrada | aclarar B = solo validación |
| 20 | P3 | docs | README receta de animación genera nombres `_oe` | alinear con el script |
| 21 | P3 | docs | Estimaciones tiempo/disco inconsistentes (2700 vs 1350) | recalibrar |

Dominios disjuntos → correctores en paralelo: **analysis** (5,6,7,11,13), **docs-informe/pres**
(2,3,8,9,14,15,16,17,18), **docs-README/diseño** (10,19,20,21), **repro** (4), **engine** (12).
Regeneración de figuras + recompilación de PDFs + commits: centralizados por el controlador tras los correctores.

### Ronda 1 — 5 correctores por dominio (workflow, 259K tokens, ~6 min) — TODOS los P1/P2/P3 aplicados
- **analysis**: `_ETIQUETAS_ES` en analyze.py/animate.py (texto visible en español, nombres de archivo
  intactos); línea de estacionario dibujada en `since_step` (no la sugerencia); `output_every` fuera de
  `_logical_run_key`; guarda de vacío en `velocity_pdf`; leyenda `1/(44 mm)` en plots.py. +2 tests → **34 pytest**.
- **entregables**: `\usepackage{float}` + `[H]` + `\clearpage` antes de Referencias (ninguna figura tras
  Conclusiones); **P1 física**: meseta a baja densidad = velocidad del **más lento** (~90-95, no la libre 105)
  con mecanismo de agrupamiento; gridlock p≥0.3 cuantificado; "distribuciones"→"tendencia"; snapshot→instantánea;
  links neutrales; fotogramas 0.9 apilados; write-before-step documentado; "por punto"→corte único.
- **docs**: README barrido OFICIAL = CONTACTO_PURO (B solo validación); conteos genéricos; tiempos coherentes
  (1350 ~0.9 GB / 2700 ~1.7 GB); receta hero canónica = script. diseño: hitos actualizados, nota snapshot v1.
- **repro**: `generar_entrega.sh` activa `.venv` si existe.
- **engine**: eliminado guard muerto `g<0` en `PeriodicTrack.isConsistent` (Javadoc actualizado). **57 tests** verdes.

**Centralizado por el controlador tras correctores:**
- Regenerado analyze.py + validacion.py + 5 fotogramas hero con etiquetas en español.
- Quitados enums (ASCENDING/DESCENDING/RANDOM) de la prosa del informe (consistencia español).
- Recompilados ambos PDFs: **informe 14 págs, presentación 17 págs**, exit 0.
- **Verificación:** Java 57 ✓ · pytest 34 ✓ · pdflatex ×2 ambos ✓ · anti-placeholders PDFs LIMPIO ✓ · `git diff --check` limpio.

Estado P0: pendiente el acto de commitear los PDFs finales (se hace en los commits de esta ronda).

## Criterios de cierre (del handoff)
- Sin P0/P1 abiertos; P2/P3 con decisión explícita.
- Java y pytest verdes.
- Informe y presentación compilan (o PDFs finales versionados y justificados).
- Sin placeholders, URLs ficticias ni vocabulario prohibido.
- Resultados no sobreprometen respecto del paper/modelo.

### Ronda 2 — 6 auditores (workflow, 806K tokens, ~15 min)
**14 hallazgos: 0 P0, 0 P1, 5 P2, 9 P3.** Criterio duro (sin P0/P1) CUMPLIDO. Físico/motor/estadística
confirman correctitud (fuzz 200k = 0 solapamientos; números del informe = datos reales). Backlog P2/P3:

| # | Sev | Dom | Hallazgo | Fix |
|---|---|---|---|---|
| 22 | P2 | cross | 3 fotogramas hero incrementales idénticos (todos N=30 lleno) | still_step en fase N=10 + regenerar |
| 23 | P2 | repro | Script no pre-chequea entorno Python (muere tras 10 min) | preflight deps antes del barrido |
| 24 | P2 | docs | Saturación N=30 con más cifras que el error; media no repr. en gridlock | redondear al error; p≥0.3 = congelado (mediana) |
| 25 | P2 | docs | Captions prometen animaciones sin link (data_anim gitignored) | redacción honesta (regenerable con script) |
| 26 | P2 | engine | "p=0 no consume PRNG" sin test behavior-only | RandomBrakeTest con RNG espía |
| 27 | P3 | docs | "snapshot" en pseudocódigo vs "instantánea" en prosa | unificar |
| 28 | P3 | analysis | FD incremental: ticks del eje x se solapan, leyenda tapa curva | MaxNLocator + legend loc + regenerar |
| 29 | P3 | repro | CLAUDE.md nombra PDF "Presentación" con tilde; archivo sin tilde | unificar CLAUDE.md |
| 30 | P3 | repro | `.impeccable/` no en .gitignore | agregar |
| 31 | P3 | repro | Sin checksums de binarios versionados | SHA256SUMS |
| 32 | P3 | analysis | detect_stationary/stationary_cut_step código muerto + comentario inexacto | corregir comentario |
| 33 | P3 | docs | Mecanismo "agrupa a cualquier densidad" sobre-generaliza p=0 vs p=0.1 | precisar redacción |
| 34 | P3 | docs | README llama "MKS" a mm (es SI, no base MKS) | → "SI: mm, mm/s" |
| 35 | P3 | docs | Tamaño en disco 0,9 vs 0,8 GB inconsistente | unificar ~0,85 GB |

### Ronda 2 — 4 correctores por dominio (workflow, 186K tokens) — todos los P2 + P3 valiosos aplicados
- **analysis**: `nearest_frame_index` + `still_step` (fotograma incremental en fase N=10; los 3 ahora
  se distinguen por orden, md5 distintos); FD con `MaxNLocator(5)` + leyenda `loc='lower left'`;
  comentario exacto + helper sin uso removido. +3 tests → **37 pytest**.
- **engine**: `RandomBrakeTest` (RNG espía: p=0 → 0 extracciones; p>0 → 1; frena sii draw<p). **60 tests**.
- **entregables**: cifras al error (~45±14); p≥0,3 congelado (mediana ~0); mecanismo a baja densidad
  preciso (alcance repetido, no agrupamiento permanente); snapshot→instantanea; captions honestos.
- **config**: preflight en `generar_entrega.sh` (falla rápido si falta entorno); SHA256SUMS; README
  "SI: mm, mm/s" y disco ~0,85 GB; CLAUDE.md nombre sin tilde; `.impeccable/` en .gitignore.

**Centralizado:** regeneradas figuras (FD legible) + 3 fotogramas incrementales en fase N=10;
recompilados PDFs (informe 14 págs, presentación 17); `SHA256SUMS` generado y verificado (3/3 OK).

**Verificación ronda 2:** `mvn test` **60** ✓ · `pytest` **37** ✓ · `pdflatex ×2` ambos ✓ ·
anti-placeholders PDFs LIMPIO ✓ · `git diff --check` limpio ✓.

**Commits ronda 2:** `c1c37d0`..`e049d0b` (analysis / engine / entregables / config+SHA / bitácora).

## Estado de cierre
- Ronda 2 de auditoría: **0 P0, 0 P1** (criterio duro cumplido). Todos los P2 corregidos; P3 corregidos
  o con decisión (el "L=1320 vs 5280" de CLAUDE.md es la misma longitud en mm vs celdas, no es inconsistencia).
- Ronda 3 de auditoría lanzada como confirmación de convergencia/regresiones.
- 15 commits nuevos sobre `4fde54b`, sin pushear (esperando OK del grupo).

### Ronda 3 — auditoría (5/6 auditores; el editor tuvo error de reintentos del tool)
**7 hallazgos: 1 P1, 3 P2, 3 P3** (uno del jurado fue output malformado, descartado). Los técnicos
(motor: fuzz 200k = 0 solapamientos; estadística: 0 hallazgos; físico: recomputó datos) confirman
**convergencia y sin regresiones** de los P0/P1 previos. Nuevos:
- **P1 (regresión):** `still_step` implementado/testeado pero NO cableado en `generar_entrega.sh` → la
  regeneración canónica dejaba los 3 hero incrementales idénticos (N=30). **Fix:** cablear still_step
  (fase N=10) en el script y el README; verificado (3 md5 distintos).
- **P2:** descripción de la PDF de velocidad invertida ("más marcada en creciente" → es DECRECIENTE).
  Verificado con datos (creciente casi N-independiente 89.8→89.3; decreciente 116→81). **Fix** informe+pres.
- **P3:** SHA no determinista (pdfTeX embebe fecha) → el script recalcula SHA256SUMS al final.
- **P3:** preflight no chequeaba versiones/pillow → agregado pillow + reporte de versiones.
- **P3:** Limitaciones PDF velocidad (moda 84-90, no puebla 30-65) → reformulado.

**Verificación ronda 3:** PDFs recompilan (14/17 págs) ✓ · SHA -c OK ✓ · anti-placeholders LIMPIO ✓ ·
still_step del script correcto (INC→6480) ✓ · pytest 37 / mvn 60 (sin cambios de código de prod) ✓.
**Commits:** `9cc87d9` (entregables), `6b0ea7e` (repro).

### Ronda 4 — auditoría de CIERRE (5/6 auditores; editor con error recurrente del tool → corrido aparte)
**6 hallazgos: 0 P0, 0 P1, 0 P2, 6 P3.** Físico-Parisi: "sin P0/P1, sin P2, sin regresiones — convergencia
confirmada" (recomputó las saturaciones contra datos; todas coinciden). Motor: fuzz + 60 tests + SHA -c OK.
Estadística: todos los checks estadísticos OK. **CONVERGENCIA: no quedan P0/P1/P2.**
Los 6 P3 (todos corregidos):
- preflight no chequeaba beamer.cls → agregado (kpsewhich).
- README ruta `docs/Guias...` inexistente → aclarado que es guía externa de la cátedra.
- informe: "constructor valida no-solapamiento en cada paso" → preciso (constructor en init/inserción;
  pasos ordinarios por construcción de R2).
- "MKS" residual en docstrings de plots.py/animate.py → "SI (mm, mm/s)".
- diseño: nombre de presentación con tilde → sin tilde; duración 20 min → ~10-15 min (consistente).

**Verificación ronda 4:** informe recompila (14 págs) ✓ · SHA -c OK ✓ · pytest 37 ✓ · script bash -n ✓ ·
sin residuos MKS/tilde ✓. **Commits:** `c037ee6`, `0f8de62`.

## CIERRE DEL LOOP
- **4 rondas de auditoría (6 lentes) + 2 rondas de correctores por dominio.** Ronda 4: **0 P0/P1/P2**;
  todos los P3 corregidos. Criterio de parada del handoff CUMPLIDO.
- Verificación final: **Java 60 tests · Python 37 pytest · informe 14 págs + presentación 17 págs compilan ·
  SHA256SUMS -c OK · anti-placeholders LIMPIO · git diff --check limpio.**
- **21 commits** sobre `4fde54b`, **sin pushear** (esperando OK del grupo). El editor-académico se corrió
  aparte como confirmación editorial final.

### Editor académico (corrido aparte, texto plano) — confirmación editorial final
Leyó ambos PDF completos. **"No hay nada de nivel P0/P1/P2; solo detalles cosméticos P3; ninguno obliga
a corrección para aprobar."** Confirmó: estructura de Resultados correcta, Conclusiones solo al final,
ninguna figura tras Referencias, "realizaciones" sin "seed", coherencia texto↔figura, sin placeholders.

P3 corregidos: cita cruzada 3A/4A unificada; "La CLI" → "la herramienta de línea de comandos";
"24 fps" → "24 cuadros/s". Commit `45878b5`.

### P3 aceptados con decisión explícita (no bloqueantes; handoff permite cerrar con P3 decididos)
- **Separador decimal**: prosa usa coma (0,1), las figuras de matplotlib usan punto (0.1). Convención de
  la herramienta, ampliamente tolerada; corregirlo exige configurar locale + regenerar las 19 figuras.
  DECISIÓN: aceptado; queda como pulido OPCIONAL para el grupo.
- **Media página en blanco (pág. 8 del informe)**: efecto de `[H]` (Fig. 6 no entra y flota). DECISIÓN:
  aceptado; ajustar floats arriesga reintroducir "figuras tras Referencias" (el P1 ya cerrado). Bajo impacto.
- **Recuadros de info pequeños en la diapo 9**: redundantes con los rótulos N=5/N=30; los bloques de color
  se leen. Aceptado.
- **"PDF"/"preprint"**: abreviaturas/términos estándar; aceptados.

### BLOQUEANTE EXTERNO (solo el grupo)
- **Nombres y legajos en la carátula**: informe/presentación muestran solo "Grupo G01S2". El grupo debe
  agregar nombres+legajos (o confirmar que la cátedra acepta entrega anonimizada). Links de animaciones a
  YouTube igual: agregarlos al publicar (hoy los captions son honestos y neutrales).

## CIERRE FINAL
Loop CONVERGIDO. Ronda 4 + editor: **0 P0/P1/P2**. P3 corregidos o aceptados con decisión. 23 commits
sobre `4fde54b`, **sin pushear**. Verificación final: Java 60 · pytest 37 · ambos PDF compilan (14/17 págs)
· SHA256SUMS -c OK · anti-placeholders LIMPIO · git diff --check limpio.
