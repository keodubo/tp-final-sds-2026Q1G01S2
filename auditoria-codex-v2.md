# Auditoría Codex v2 — TP Final SdS NaSch + VDV

Fecha: 2026-06-28  
Rama: `audit/codex-v2`  
Alcance: auditoría y corrección de la implementación mergeada. No se corrió el barrido completo de simulaciones.

## Resumen ejecutivo

El motor Java no mostró contraejemplos en R1→R3→R2→R4, contacto puro, agrupamientos, ruta llena ni validación `p=0` de la variante B. Los riesgos fuertes estaban en la capa de análisis y en la documentación: `analyze.py` descartaba el protocolo incremental, el diagrama fundamental mezclaba valores de `p`, el corte de estacionario sugerido se graficaba como índice y no como paso real con `output_every != 1`, y los comandos de “dataset experimental” corrían N fijo en vez del protocolo del artículo.

Se corrigió el análisis para separar variante, orden, protocolo y `p`; se agregó velocidad media incremental por N activo y orden de inserción; se corrigió `N=1` en observables de vecino; se reforzó la cobertura Java de `CONTACTO_PURO + INCREMENTAL_180S`; y se alinearon README, resumen, diseño y CLAUDE con las decisiones confirmadas.

## Jurado 1 — Física / Modelo

### Hallazgos

- **Alta:** la comparación con el artículo quedaba sin análisis incremental por orden. `run_matrix.py` podía generar `INCREMENTAL_180S`, pero `analysis/analyze.py` filtraba solo `FIXED_N`.
- **Media:** las PDFs de densidad/velocidad elegían automáticamente el menor `p`; con los defaults eso era `p=0`, poco representativo para el colapso experimental.
- **Media:** la afirmación “contacto puro a `p=0` ⇒ `Q=ρ·vmax`” estaba demasiado generalizada para documentación de defensa.
- **Baja:** no había contraejemplos del motor para no-solapamiento, ruta llena o agrupamientos. Los tests y probes de jurados no encontraron fallas.

### Correcciones aplicadas

- `analysis/analyze.py`: análisis incremental por N activo y orden, separado por `(regla2, order, p)`.
- `analysis/analyze.py`: `select_representative_p` elige el menor `p>0` disponible, o un `--p-representativo` explícito.
- `README.md`, `CLAUDE.md`, `RESUMEN-IMPLEMENTACION_v1.md`, `diseno-tp-final-vdv-nasch_v1.md`: la afirmación de flujo libre queda acotada al caso homogéneo `p=0`; no se usa como validación global de A.

### Diferido

- No se corrió el barrido completo. La comparación cuantitativa real queda para el grupo con los datos generados.

### Preguntas abiertas

- Contrato temporal exacto de salida en la frontera incremental: estado antes o después del paso cuando entra un lote.

## Jurado 2 — Cátedra / Parisi

### Hallazgos

- **Alta:** el comando sugerido como experimental corría `FIXED_N` por default, no el protocolo del artículo con órdenes creciente/decreciente/aleatorio.
- **Alta:** el flujo por defecto calculaba observables con `since_step=0`; eso incluye el cuadro inicial y no reemplaza la inspección de estacionario.
- **Media:** persistían anglicismos visibles y un estado documental que sobreprometía comparación final.
- **Baja:** quedaban rastros visibles de `seed`/`realization_seed`; la cátedra pidió hablar de realizaciones.

### Correcciones aplicadas

- `README.md` y `RESUMEN-IMPLEMENTACION_v1.md`: el comando experimental ahora usa `--rule CONTACTO_PURO --protocol INCREMENTAL_180S --order ASCENDING DESCENDING RANDOM`.
- `README.md`: flujo en dos pasadas: generar figuras/evolución temporal, inspeccionar estacionario, y repetir con `--since-step <paso_elegido>`.
- `engine/src/main/java/ar/edu/itba/sds/io/OutputWriter.java`: cabecera cambia a `realizacion_id`.
- Documentación principal: “pipeline”→“flujo”, “single-lane”→“un carril”, “lattice” visible→“malla”.

### Diferido

- El informe y la presentación final no se escribieron, por alcance explícito.

### Preguntas abiertas

- El corte estacionario final debe elegirlo el grupo mirando `figures/evolucion_temporal_*.png` una vez corrido el barrido.

## Jurado 3 — Arquitectura / Código / Tests

### Hallazgos

- **Alta:** `analysis/analyze.py` promediaba/curvaba datos con metadatos insuficientes: variante sí, pero no orden/protocolo/`p`.
- **Media:** `detect_stationary()` devolvía índice de muestra, pero `plot_time_evolution()` usa pasos reales. Con `output_every != 1`, la línea vertical quedaba desplazada.
- **Media:** faltaba cobertura de `CONTACTO_PURO + INCREMENTAL_180S`.
- **Baja/Media:** `N=1` generaba una densidad local artificial `1/L`, aunque no existe vecino más cercano.

### Correcciones aplicadas

- `analysis/analyze.py`: `group_fixed_runs`, `group_fundamental_runs`, `incremental_speed_by_order`, `stationary_cut_step`.
- `analysis/observables.py`: pasos con menos de dos vehículos no aportan densidad local; `density_pdf` devuelve `NaN` explícito y `fundamental_diagram` devuelve vacío.
- `analysis/tests/test_analyze.py`, `analysis/tests/test_observables.py`, `analysis/tests/test_plots.py`: tests de comportamiento para los casos anteriores.
- `engine/src/test/java/ar/edu/itba/sds/sim/NaSchEngineTest.java`: incremental cubre ambas variantes de R2.

### Diferido

- Sidecar/manifiesto completo por corrida (`id,vFree,vMax,x0`, comando, commit) sería útil antes del barrido grande, pero no se implementó porque cambia formato de entrega y no era imprescindible para mantener tests/verificación.

### Preguntas abiertas

- Si se decide persistir un manifiesto de realización completo, definir formato antes de poblar `data/`.

## Jurado 4 — Abogado del diablo

### Hallazgos

- **Alta:** el diagrama fundamental mezclaba todos los `p` dentro de cada variante, produciendo una curva que no representaba ningún experimento concreto.
- **Media:** docs de estado estaban demasiado optimistas: “comparación con el artículo” sonaba terminada aunque faltaba correr barridos y elegir estacionario.
- **Media:** `CLAUDE.md` todavía listaba como pendientes decisiones que el pedido marcó confirmadas.
- **Media:** reproducibilidad técnica depende de `--seed`, pero la realización completa no queda persistida fuera de la secuencia reproducible.

### Correcciones aplicadas

- `analysis/analyze.py`: diagrama fundamental separado por `(regla2, order, protocol, p)`.
- `README.md`, `diseno-tp-final-vdv-nasch_v1.md`: Hito 6 queda como código listo; comparación final requiere correr el barrido y elegir estacionario.
- `CLAUDE.md`: reemplaza “Pendientes a confirmar” por “Temas a documentar en la defensa”; no reabre R2, orden de reglas, alcance incremental, `p`, `L`, error ni post-simulación.

### Diferido

- No se cambió la semántica de salida antes/después de `step()` para incremental. Se deja como contrato a documentar porque cambiarlo puede alterar archivos existentes y la interpretación de `steps`.

### Preguntas abiertas

- Definir si el estado guardado en la frontera incremental debe representar el instante previo o posterior a la inserción.

## Resumen diff-like

- **Agregado:** `analysis/tests/test_analyze.py`, `analysis/tests/test_plots.py`, `auditoria-codex-v2.md`.
- **Actualizado:** `analysis/analyze.py` separa variante/orden/protocolo/`p`, agrega incremental por N activo y convierte corte a paso real.
- **Actualizado:** `analysis/observables.py` trata `N=1` como sin vecino para densidad local/diagrama fundamental.
- **Actualizado:** `analysis/plots.py` acepta curvas etiquetadas por texto para órdenes de inserción.
- **Actualizado:** `OutputWriter` usa `realizacion_id`; tests Java cubren `CONTACTO_PURO + INCREMENTAL_180S`.
- **Documentado:** comandos correctos para dataset experimental, flujo de estacionario por inspección, estado honesto de hitos, y decisiones confirmadas.

## Commits

- `03a176d fix(analysis): separate experimental metadata`
- `ca44665 test(engine): cover incremental contact variant`
- `6973e98 docs: align audit v2 decisions`
- `docs: add codex v2 audit report`

Todos incluyen:

```text
Co-Authored-By: Codex <noreply@openai.com>
```

## Verificación

Comando:

```bash
mvn -f engine/pom.xml clean test
```

Salida:

```text
[INFO] Scanning for projects...
[INFO] 
[INFO] ---------------------< ar.edu.itba.sds:nasch-vdv >----------------------
[INFO] Building NaSch-VDV 1.0-SNAPSHOT
[INFO]   from pom.xml
[INFO] --------------------------------[ jar ]---------------------------------
[INFO] 
[INFO] --- clean:3.2.0:clean (default-clean) @ nasch-vdv ---
[INFO] Deleting /Users/keoni/Claude-Workspace/projects/sds-entregas/tp-final-sds-2026Q1G01S2/engine/target
[INFO] 
[INFO] --- resources:3.4.0:resources (default-resources) @ nasch-vdv ---
[INFO] skip non existing resourceDirectory /Users/keoni/Claude-Workspace/projects/sds-entregas/tp-final-sds-2026Q1G01S2/engine/src/main/resources
[INFO] 
[INFO] --- compiler:3.13.0:compile (default-compile) @ nasch-vdv ---
[INFO] Recompiling the module because of changed source code.
[INFO] Compiling 15 source files with javac [debug release 21] to target/classes
[INFO] 
[INFO] --- resources:3.4.0:testResources (default-resources) @ nasch-vdv ---
[INFO] skip non existing resourceDirectory /Users/keoni/Claude-Workspace/projects/sds-entregas/tp-final-sds-2026Q1G01S2/engine/src/test/resources
[INFO] 
[INFO] --- compiler:3.13.0:testCompile (default-testCompile) @ nasch-vdv ---
[INFO] Recompiling the module because of changed dependency.
[INFO] Compiling 8 source files with javac [debug release 21] to target/test-classes
[INFO] 
[INFO] --- surefire:3.2.5:test (default-test) @ nasch-vdv ---
[INFO] Using auto detected provider org.apache.maven.surefire.junitplatform.JUnitPlatformProvider
[INFO] 
[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running ar.edu.itba.sds.config.ConfigTest
[INFO] Tests run: 8, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.059 s -- in ar.edu.itba.sds.config.ConfigTest
[INFO] Running ar.edu.itba.sds.MainRunTest
[INFO] Tests run: 3, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.042 s -- in ar.edu.itba.sds.MainRunTest
[INFO] Running ar.edu.itba.sds.io.OutputWriterTest
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.001 s -- in ar.edu.itba.sds.io.OutputWriterTest
[INFO] Running ar.edu.itba.sds.model.PeriodicTrackTest
[INFO] Tests run: 9, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.008 s -- in ar.edu.itba.sds.model.PeriodicTrackTest
[INFO] Running ar.edu.itba.sds.sim.NaSchEngineTest
[INFO] Tests run: 9, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.032 s -- in ar.edu.itba.sds.sim.NaSchEngineTest
[INFO] Running ar.edu.itba.sds.sim.collision.CollisionContextTest
[INFO] Tests run: 2, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.002 s -- in ar.edu.itba.sds.sim.collision.CollisionContextTest
[INFO] Running ar.edu.itba.sds.sim.collision.ClasicaSalvoCeroTest
[INFO] Tests run: 3, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.007 s -- in ar.edu.itba.sds.sim.collision.ClasicaSalvoCeroTest
[INFO] Running ar.edu.itba.sds.sim.collision.ContactoPuroTest
[INFO] Tests run: 4, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.003 s -- in ar.edu.itba.sds.sim.collision.ContactoPuroTest
[INFO] 
[INFO] Results:
[INFO] 
[INFO] Tests run: 39, Failures: 0, Errors: 0, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time:  1.541 s
[INFO] Finished at: 2026-06-28T22:38:49-03:00
[INFO] ------------------------------------------------------------------------
```

Comando:

```bash
python3 -m pytest analysis/tests -q
```

Salida:

```text
.............                                                            [100%]
13 passed in 0.68s
```

Checks adicionales:

```bash
python3 -m py_compile analysis/*.py
python3 analysis/analyze.py --data-dir <tmp>/data --figures-dir <tmp>/figures --fd-window 2
git diff --check
```

Resultado: compilación Python sin salida, análisis sintético incremental generó `velocidad_media_incremental_*.png` y `diagrama_fundamental.png`, y `git diff --check` sin salida.

## Próximas acciones

- [ ] Correr el barrido real con `CONTACTO_PURO + INCREMENTAL_180S + ASCENDING/DESCENDING/RANDOM`.
- [ ] Inspeccionar evolución temporal y fijar `--since-step`.
- [ ] Recalcular figuras finales con el corte elegido.
- [ ] Definir si se agrega un manifiesto completo por realización antes de poblar `data/`.
