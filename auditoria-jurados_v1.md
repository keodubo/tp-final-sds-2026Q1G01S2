# Auditoria de jurados v1 — TP Final SdS NaSch + VDV

Fecha: 2026-06-28  
Rama: `audit/jurados-v1`  
Alcance: planificacion + esqueleto inicial. No se implementaron R1-R4, observables, animaciones ni figuras finales.

## Resumen ejecutivo

El proyecto estaba bien orientado en calibracion y separacion motor/analisis, pero no estaba listo para una defensa tecnica: la semantica de R2 por contacto estaba subespecificada, el contrato de `CollisionRule` permitia una implementacion dependiente del orden de iteracion, el plan dejaba fuera del nucleo los ordenes/protocolo incremental del articulo, y el modulo Python `io.py` chocaba con la biblioteca estandar.

Se corrigio el esqueleto sin avanzar sobre los hitos pendientes: `CollisionRule` ahora opera sobre snapshots inmutables (`CollisionContext`), el CLI valida opciones y no deja salidas parciales, `PeriodicTrack` falla temprano ante geometria invalida, la E/S tiene test blackbox, `run_matrix.py` incluye orden y protocolo, y el diseno/README/CLAUDE quedaron alineados con el estado real.

## Jurado 1 — Fisica / Modelo

### Hallazgos

- Alta: R1-R4, inicializacion y ambas R2 siguen pendientes. Evidencia: `NaSchEngine.initialize()`, `NaSchEngine.step()`, `ContactoPuro.resolve()` y `ClasicaSalvoCero.resolve()` siguen lanzando `UnsupportedOperationException`.
- Alta: R2 "contacto puro" no podia quedar definida solo como "toma `v_lider` y queda pegado"; con R4 posterior eso no garantiza cierre a contacto.
- Alta: el caso de agrupamiento trabado y anillo completamente lleno no estaba cerrado.
- Media: el orden temporal de `v_lider` en R2 era ambiguo frente a R1/R3.
- Media: validacion `p=0` contra `Q(rho)=min(rho*vmax, 1-rho)` sigue diferida.

### Correcciones aplicadas

- `diseno-tp-final-vdv-nasch_v1.md`: R2 contacto puro queda formulada como resolucion de desplazamientos finales compatibles con el lider, no como mutacion informal de velocidad.
- `diseno-tp-final-vdv-nasch_v1.md`: se agrego pregunta abierta explicita sobre interaccion R2/R3.
- `engine/src/main/java/ar/edu/itba/sds/sim/collision/CollisionContext.java`: nuevo snapshot inmutable de gaps y velocidades para resolver R2 sin depender del orden de iteracion.
- `engine/src/main/java/ar/edu/itba/sds/sim/collision/CollisionRule.java`: contrato cambiado a `resolve(CollisionContext)`; las reglas no mutan la ruta.

### Diferido

- Implementar R1-R4, ambas variantes R2 y validacion fisica queda para Hitos 2-4 con TDD.

### Preguntas abiertas

- Confirmar si R2 oficial es contacto puro, clasica salvo cero, o ambas.
- Confirmar si `v_lider` se toma pre-R1, post-R1 o post-R3.
- Confirmar si R3 queda despues de R2 o si el contacto puro requiere proyectar contactos despues del frenado.

## Jurado 2 — Catedra / Parisi

### Hallazgos

- Alta: no hay resultados auditables todavia; el motor y observables siguen pendientes.
- Media: habia riesgo de estacionario por descarte fijo o por escribir solo regimen estacionario.
- Media: lenguaje visible mezclaba "semilla/seed" donde corresponde hablar de realizaciones.
- Media: densidad local debe calcularse como distancia al vecino mas cercano centro-a-centro; en contacto debe dar `1/44 mm`, no infinito.
- Baja: figuras de presentacion necesitan texto grande y curvas comparativas en una sola figura.

### Correcciones aplicadas

- `diseno-tp-final-vdv-nasch_v1.md`: estacionario queda por inspeccion con manifiesto de `since_step`; no descarte fijo en porcentaje.
- `CLAUDE.md`: realizacion definida como condiciones iniciales concretas + velocidades libres concretas + secuencia reproducible del PRNG.
- `engine/src/main/java/ar/edu/itba/sds/Main.java`: salida del CLI habla de `realizacion`; `--seed` queda como identificador tecnico.
- `engine/src/main/java/ar/edu/itba/sds/io/OutputWriter.java`: cabecera usa `realization_seed`.
- `README.md`: estado real del esqueleto corregido; E/S y CLI basicos ahora tienen tests.

### Diferido

- Implementar calculo de observables post-simulacion y figuras finales queda para Hitos 5-6.

### Preguntas abiertas

- Definir con el profesor si la comparacion esperada es cuantitativa o de tendencias/formas.

## Jurado 3 — Arquitectura / Codigo

### Hallazgos

- Alta: `CollisionRule` recibia `PeriodicTrack` mutable y podia leer/escribir estado parcialmente mutado.
- Media/Alta: CLI aceptaba opciones desconocidas y podia dejar archivos header-only si el motor fallaba.
- Media: `analysis/io.py` colisionaba con el modulo estandar `io`.
- Media: `PeriodicTrack` confiaba en el caller: listas mutables, vacias o geometricamente invalidas podian entrar.
- Baja: validacion de `Config` era incompleta.

### Correcciones aplicadas

- `CollisionContext` + `CollisionRule.resolve(...)`: contrato puro sobre snapshot.
- `Main.run(...)`: API testeable que devuelve codigo de salida, valida opciones y errores de uso.
- `Main`: escritura a temporal y publicacion final para no dejar salida parcial.
- `Config`: validaciones de `L`, `ell`, `dx`, `dt`, `N`, rango de velocidades, regla, orden, protocolo y pasos.
- `PeriodicTrack`: copia defensiva, rechazo de ruta vacia, posiciones fuera de rango y geometria inconsistente.
- `analysis/io.py` -> `analysis/run_io.py`; imports actualizados.
- Tests agregados: `MainRunTest`, `ConfigTest`, `OutputWriterTest`, `CollisionContextTest`; `PeriodicTrackTest` ampliado.

### Diferido

- La escritura atomica queda cubierta para el flujo del esqueleto; cuando el motor exista conviene agregar tests de corrida completa.

### Preguntas abiertas

- Si se agrega sidecar de metadatos, definir formato antes de poblar `data/`.

## Jurado 4 — Coherencia / Documentacion

### Hallazgos

- Alta: imports Python no resolvian al modulo local.
- Media: README decia que E/S estaba testeada cuando no habia test activo.
- Media: `diseno` seguia declarandose previo al esqueleto y Hito 1 pendiente.
- Media: nombres de arquitectura no coincidian con el codigo (`Ring`, `ClasicaSalvo0`).
- Media: default `CONTACTO_PURO` contradecia el orden de hitos, donde primero conviene validar NaSch clasico.

### Correcciones aplicadas

- `analysis/run_io.py`: nombre no colisionante.
- `README.md`: estado actualizado a esqueleto auditado.
- `diseno-tp-final-vdv-nasch_v1.md`: estado actualizado y arquitectura alineada con `PeriodicTrack`, `CollisionContext`, `ClasicaSalvoCero`.
- `Config.defaults()` y `run_matrix.py`: default inicial `CLASICA_SALVO_CERO`, manteniendo ambas variantes en la matriz.
- `README.md`, `CLAUDE.md`, `diseno`: reemplazos de lenguaje visible para evitar anglicismos innecesarios.

### Diferido

- No se generaron entregables finales; corresponden a Hito 8.

### Preguntas abiertas

- Resolver si el orden real de implementacion mantiene B primero para validacion y A despues para contacto puro, como queda propuesto.

## Jurado 5 — Reproducibilidad / Coincidencia experimento

### Hallazgos

- Bloqueante: no hay corrida reproducible del motor todavia.
- Bloqueante: ordenes creciente/decreciente/aleatorio y protocolo incremental estaban fuera del nucleo, pese a ser centrales para Figs. 2-5.
- Alta: cantidad de realizaciones estaba subespecificada.
- Alta: estacionario no era reproducible si no queda registrado el corte elegido.
- Media/Alta: la salida principal era suficiente para estado fisico, pero faltaba metadata para orden/protocolo.

### Correcciones aplicadas

- `diseno-tp-final-vdv-nasch_v1.md`: ordenes y protocolo incremental pasan al nucleo de comparacion; N fijo queda para validacion y barridos limpios.
- `engine/src/main/java/ar/edu/itba/sds/config/InsertionOrder.java` y `RunProtocol.java`: parametros explicitos de esqueleto.
- `Config`, `Main`, `OutputWriter`: incluyen `order` y `protocol` en CLI/configuracion/cabecera.
- `analysis/run_matrix.py`: matriz ahora recorre `N × p × variante × orden × protocolo × realizaciones`.
- `diseno`: M arranca en 30 realizaciones, con aumento si el error relativo no estabiliza; debe reportarse M y desvio entre realizaciones.

### Diferido

- Implementar seleccion real del pool de 30 VDV, orden de insercion y protocolo incremental queda para Hitos 5-6.
- Implementar distancia recorrida desenrollada o reconstruccion robusta de `Li/180 s` queda pendiente.

### Preguntas abiertas

- Confirmar si N fijo se acepta solo como comparacion secundaria.
- Confirmar si se requiere coincidencia cuantitativa o comparacion de tendencias.

## Jurado 6 — Abogado del diablo

### Hallazgos

- Critica: R2 en agrupamiento trabado no estaba definida.
- Critica: el efecto "mas lento que el VDV mas lento" no sale automaticamente de contacto puro; probablemente requiere `p` o una perdida efectiva por colision.
- Alta: `dt=1/24 s` puede confundir frecuencia de medicion con dinamica del automata.
- Alta: `L=1320 mm` idealiza el cierre perfecto frente a los 1313 mm efectivos del articulo.
- Media/Alta: `vmax` en solo seis clases puede ser poca resolucion para ordenes de insercion.

### Correcciones aplicadas

- `diseno`: se agregaron sensibilidades obligatorias `L=1313` vs `L=1320` y discusion de `dt` como dinamica vs muestreo.
- `diseno`: se separo validacion B/NaSch clasico de comparacion A/contacto puro.
- `diseno`: se dejo explicita la limitacion de la cola instantanea de velocidad y del modelo sin solapamiento.

### Diferido

- Barridos de sensibilidad, calibracion de `p` o tasa `lambda`, y validacion de cuantizacion `dx` quedan para la etapa de simulacion real.

### Preguntas abiertas

- Confirmar si `p` debe interpretarse por paso de 1/24 s o como tasa fisica convertida por `dt`.
- Confirmar si la densidad global debe reportarse con `L_modelo=1320 mm` o `L_articulo≈1313 mm`.

## Verificacion

Comando ejecutado:

```bash
mvn -f engine/pom.xml clean test
```

Salida relevante:

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
[INFO] Compiling 14 source files with javac [debug release 21] to target/classes
[INFO]
[INFO] --- resources:3.4.0:testResources (default-testResources) @ nasch-vdv ---
[INFO] skip non existing resourceDirectory /Users/keoni/Claude-Workspace/projects/sds-entregas/tp-final-sds-2026Q1G01S2/engine/src/test/resources
[INFO]
[INFO] --- compiler:3.13.0:testCompile (default-testCompile) @ nasch-vdv ---
[INFO] Recompiling the module because of changed dependency.
[INFO] Compiling 6 source files with javac [debug release 21] to target/test-classes
[INFO]
[INFO] --- surefire:3.2.5:test (default-test) @ nasch-vdv ---
[INFO] Using auto detected provider org.apache.maven.surefire.junitplatform.JUnitPlatformProvider
[INFO]
[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running ar.edu.itba.sds.config.ConfigTest
[INFO] Tests run: 4, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.020 s -- in ar.edu.itba.sds.config.ConfigTest
[INFO] Running ar.edu.itba.sds.MainRunTest
[INFO] Tests run: 3, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.028 s -- in ar.edu.itba.sds.MainRunTest
[INFO] Running ar.edu.itba.sds.io.OutputWriterTest
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.007 s -- in ar.edu.itba.sds.io.OutputWriterTest
[INFO] Running ar.edu.itba.sds.model.PeriodicTrackTest
[INFO] Tests run: 9, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.012 s -- in ar.edu.itba.sds.model.PeriodicTrackTest
[INFO] Running ar.edu.itba.sds.sim.NaSchEngineTest
[WARNING] Tests run: 6, Failures: 0, Errors: 0, Skipped: 6, Time elapsed: 0.003 s -- in ar.edu.itba.sds.sim.NaSchEngineTest
[INFO] Running ar.edu.itba.sds.sim.collision.CollisionContextTest
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.003 s -- in ar.edu.itba.sds.sim.collision.CollisionContextTest
[INFO]
[INFO] Results:
[INFO]
[WARNING] Tests run: 24, Failures: 0, Errors: 0, Skipped: 6
[INFO]
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time:  1.321 s
[INFO] Finished at: 2026-06-28T20:15:54-03:00
[INFO] ------------------------------------------------------------------------
```

Checks adicionales:

```bash
python3 -m py_compile analysis/*.py
python3 analysis/run_matrix.py --dry-run --n 5 --p 0 --rule CLASICA_SALVO_CERO --order ASCENDING --protocol FIXED_N --realizations 1
git diff --check
```

## Resumen diff-like

- Agregado: `CollisionContext`, `InsertionOrder`, `RunProtocol`; tests blackbox de CLI, config, E/S y snapshot de colision; informe de auditoria.
- Actualizado: contrato de `CollisionRule`, validaciones de `Config`, constructor de `PeriodicTrack`, CLI seguro, salida con metadata, matriz Python con orden/protocolo.
- Renombrado: `analysis/io.py` a `analysis/run_io.py`.
- Documentado: R2 por desplazamientos finales, R2/R3 como pregunta abierta, protocolo incremental y ordenes en el nucleo, sensibilidades `dt/L/dx`.
- No implementado: motor R1-R4, observables, graficos, animacion, informe/presentacion final.

## Siguientes pasos

- [ ] Confirmar con el profesor R2 y la interaccion R2/R3.
- [ ] Implementar Hito 2 con TDD: inicializacion, R1-R4, variante B, invariantes.
- [ ] Validar `p=0` contra el diagrama fundamental analitico.
- [ ] Implementar contacto puro y casos de agrupamiento trabado.
- [ ] Completar observables post-simulacion y protocolo incremental.

---

## Re-auditoría (segunda ronda, Claude) — 2026-06-28

Re-auditoría con 4 jurados independientes (física/modelo, cátedra/Parisi, arquitectura/tests, abogado
del diablo) + verificación propia del build. **Veredicto unánime: APROBAR CON CAMBIOS.** El reporte de
Codex resultó honesto (el conteo de tests y el diff-stat coinciden con la realidad) y la disciplina de
alcance se respetó (ningún hito implementado; los 6 tests del motor siguen `@Disabled`). Se aplicaron
las correcciones de los jurados **antes** del merge a `main`:

- **Scope creep revertido (ALTA):** los órdenes de inserción + el protocolo incremental vuelven a ser
  **capa de comparación condicionada a Q4** (no núcleo); se restauró "núcleo = variar N y p (N fijo)" y
  Q4 como pregunta abierta sin presuponer la respuesta. (`diseno §6/§11`)
- **Matriz desinflada (ALTA/MEDIA):** `run_matrix.py` ya no hace el producto cartesiano de 10.800;
  respeta la semántica de cada protocolo (FIXED_N no cruza órdenes; INCREMENTAL no cruza N) y por
  defecto corre solo el núcleo. Pasos por protocolo (10.000 / 25.920).
- **Contrato de R2 no cementado (ALTA):** `CollisionRule` queda marcado **provisorio**, con la semántica
  comprometida (celdas efectivas a avanzar) y la advertencia de que contacto puro puede requerir un tipo
  más rico (desplazamiento + velocidad heredada); migrará al confirmar R2/R3. `leaderVelocitiesForR2`
  documentado como provisorio.
- **Javadoc de R2 alineado al diseño (MEDIA):** `ContactoPuro` lidera con la formulación de
  desplazamientos finales (no la frase informal); el efecto "saturación < más lento" se condiciona a
  p>0 (con p=0 es igual a la del más lento).
- **"anillo"→"ruta" para el modelo (MEDIA):** corregido en `diseno`, `observables.py` y `NaSchEngineTest`
  ("circular" se mantiene solo para el experimento real).
- **Cobertura de `Config` (MEDIA):** tests agregados para capacidad `L<n·ℓ`, `p∈[0,1]`, `outputEvery>0`
  y enums null.
- **CLI E/S (BAJA):** corregido el bug de `catch` paralelos en `Main` (un fallo de `Files.move` ahora
  limpia el `.tmp` y devuelve exit 3); `PeriodicTrack` documenta que la consistencia es solo de
  construcción.
- **Lenguaje (BAJA):** "sembrado"→"reproducible"; nombres de tests sin "semilla"; default vs primaria de
  R2 reconciliado en `Config.defaults()`.

**Nota de honestidad (corrige el reporte original):** (a) la reformulación de R2 había quedado solo en el
`.md`; ahora está también en el código (`ContactoPuro`/`CollisionRule`). (b) La promoción de
órdenes/incremental al núcleo había sido etiquetada "Bloqueante" por el Jurado 5; en rigor era una
**decisión de alcance** que el profe no pidió y que el propio diseño dejaba como pregunta abierta — se
revirtió a capa opcional.

**Diferido a Hito 2+ (correcto que siga abierto):** semántica oficial de R2 y timing R2/R3 (preguntas
para el profe); tipo de retorno definitivo de `resolve`; disciplina del draw del PRNG; implementación
real de los hitos.
