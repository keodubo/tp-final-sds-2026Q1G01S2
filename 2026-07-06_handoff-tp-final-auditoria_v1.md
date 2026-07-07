# Handoff TP Final SdS - Auditoria y correcciones Fable/Codex

**Fecha:** 2026-07-06
**Repo local:** `/Users/keoni/Claude-Workspace/projects/sds-entregas/tp-final-sds-2026Q1G01S2`
**Repo remoto:** `https://github.com/keodubo/tp-final-sds-2026Q1G01S2.git`
**Branch:** `fable/tp-final-auditoria-integral-v1`
**Ultimo commit pusheado:** `7aa5417dc32df88ef8d5532b7f81c1c99f76cfb3` (`auditar y corregir entrega tp final`)

## Resumen corto

Se audito lo hecho por Fable usando las correcciones previas de TP2-TP5 como checklist de errores recurrentes de Parisi. Despues se corrigieron varios problemas de contrato en motor/CLI, analisis Python y documentos/LaTeX. La rama ya fue commiteada y pusheada.

La auditoria canonica para revisar es:

- `/Users/keoni/Claude-Workspace/projects/sds-entregas/tp-final-sds-2026Q1G01S2/2026-07-05_auditoria-codex-fable-tp-final_v1.md`

El resumen Fable actualizado queda en:

- `/Users/keoni/Claude-Workspace/projects/sds-entregas/tp-final-sds-2026Q1G01S2/2026-07-05_fable-auditoria-tp-final_v1.md`

## Verificaciones ya corridas

Antes del commit `7aa5417` se verifico:

```bash
mvn -f engine/pom.xml test
python3 -m pytest analysis/tests -q
pdflatex -interaction=nonstopmode -halt-on-error SdS_TPFinal_2026Q1G01S2_Presentacion.tex
git diff --cached --check
pdftotext presentacion/SdS_TPFinal_2026Q1G01S2_Presentacion.pdf -
```

Resultados:

- Java: 57 tests, 0 fallas.
- Python: 32 tests, 0 fallas.
- Presentacion PDF: compila, 17 paginas, `Author: Grupo G01S2`.
- PDF sin `COMPLETAR`, `XXXX`, `seed`, `sin_orden`, `TODO/FIXME` ni `1/44 mm`.

## Errores encontrados y estado actual

| ID | Error | Estado | Donde mirar |
|---|---|---|---|
| B1 | Entregables LaTeX no compilaban por nombres de assets desalineados (`_oe`, `sin_orden`). | Parcialmente corregido. Los `.tex` apuntan a nombres locales reales y el PDF de presentacion esta versionado. Pero desde un clon limpio los `.tex` todavia dependen de `figures/` y `data_anim/`, que estan ignorados. | Auditoria B1; `presentacion/*.tex`; `informe/*.tex`; `.gitignore` |
| B2 | La auditoria Fable sobreafirmaba evidencia no reproducible. | Corregido en parte. Se agrego auditoria Codex autocontenida y se actualizo el resumen Fable para no esconder contradicciones. | `2026-07-05_auditoria-codex-fable-tp-final_v1.md`; `2026-07-05_fable-auditoria-tp-final_v1.md` |
| A1 | `--even-spread` podia crear una corrida falsamente incremental. | Corregido. Ahora falla si se combina con `INCREMENTAL_180S`; hay test behavior-only. | `engine/src/main/java/ar/edu/itba/sds/Main.java`; `engine/src/test/java/ar/edu/itba/sds/MainCliContractTest.java` |
| A2 | PDFs y diagrama fundamental incrementales usan transitorios como si fueran regimen estacionario. | Pendiente metodologico. La Fig. 2 puede usar ventana completa de 180 s, pero PDFs/FD deberian tener corte estacionario por fase si se presentan como estacionarios. | Auditoria A2; `analysis/analyze.py`; informe seccion Resultados/Limitaciones |
| A3 | `--skip-existing` podia duplicar realizaciones legacy y sesgar errores. | Mitigado en analisis. `analyze.py` detecta duplicados por clave logica y falla. Queda decidir si `run_matrix.py` debe exigir out-dir limpio. | `analysis/analyze.py`; `analysis/tests/test_analyze.py` |
| A4 | Placeholders y URLs ficticias en entrega. | Corregido. Se removieron placeholders de autores y links `XXXX`; se dejo texto neutral para animaciones. | `informe/*.tex`; `presentacion/*.tex`; README |
| A5 | Resultados no reproducibles desde el repo por `data/`, `figures/`, `data_anim/` ignorados. | Pendiente. El PDF de presentacion esta versionado, pero no hay pipeline de reproduccion completa ni checksums de datos/figuras. | `.gitignore`; README; auditoria A5 |
| M1 | `order` en `FIXED_N` podia fragmentar datasets (`RANDOM` vs `SIN_ORDEN`). | Corregido. `analysis/analyze.py` canonicaliza `FIXED_N` a `SIN_ORDEN`. | `analysis/analyze.py`; tests |
| M2 | `--p-representativo` podia caer silenciosamente a otro `p`. | Corregido. Ahora falla si el `p` pedido falta en un grupo. | `analysis/analyze.py`; tests |
| M3 | Frontera incremental: la salida se escribe antes de `step()`, entonces el lote nuevo aparece una muestra despues. | Documentado/testeado, no cambiado. El contrato actual queda explicitado en test. Si quieren otra semantica, cambiar motor y tests. | `MainCliContractTest.salidaIncrementalNoAdelantaElLoteEnLaFronteraEscritaAntesDelPaso` |
| M4 | Frase peligrosa: `p=0` parecia igualar contacto puro con NaSch canonico. | Corregido. Ahora se aclara que solo variante B coincide con NaSch canonico/triangular. | informe, presentacion, diseno |
| M5 | Notacion dimensional incorrecta `1/44 mm`. | Corregido a `1/(44 mm)` / `0.0227 mm^-1`. | informe, presentacion, diseno, auditorias |
| M6 | Test de PDF de densidad podia pasar con NaN. | Corregido. Test exige finitud e integral aproximada. | `analysis/tests/test_observables.py` |
| M7 | Documentacion/dependencias menores: default desactualizado, anglicismos, etc. | Parcialmente corregido. Default `CONTACTO_PURO` y vocabulario principal corregidos. `pytest>=8.0` sigue flotante si quieren fijar dependencias. | `diseno-tp-final-vdv-nasch_v1.md`; `analysis/requirements.txt` |

## Pendientes recomendados para corregir

1. **Reproducibilidad de entrega.** Decidir una politica:
   - versionar PDFs finales y checksums/manifiesto de figuras, o
   - agregar un `make entrega`/script que regenere `data`, `figures`, `data_anim` y compile informe+presentacion desde cero.

2. **Regimen estacionario en incremental.**
   - Mantener Fig. 2 con ventana completa de 180 s si se quiere comparabilidad con el paper.
   - Para PDFs de densidad/velocidad y FD incremental, definir corte estacionario por fase o declarar explicitamente que no son solo estacionario.

3. **Informe final PDF.**
   - La presentacion PDF quedo versionada.
   - El informe `.tex` compila localmente, pero el PDF final del informe no fue versionado en el commit. Si la entrega requiere PDF, generarlo y decidir si se commitea.

4. **Artefactos locales no trackeados.**
   - Quedaron fuera del commit:
     - `presentacion/SdS_TPFinal_2026Q1G01S2_Presentacion.nav`
     - `presentacion/SdS_TPFinal_2026Q1G01S2_Presentacion.snm`
     - `tmp/`
   - Son auxiliares/QA local. No borrarlos sin confirmar con el grupo.

5. **Datos/figuras.**
   - Si tu objetivo es reauditar resultados numericos, no alcanza con mirar el PDF: hay que revisar `figures/manifiesto.csv`, `data/`, `data_anim/` y la matriz de corridas real. Esos directorios pueden estar ignorados y depender del estado local.

## Plan guia de implementacion con subagentes

Esta seccion es una base operativa para que otro agente pueda continuar. **No debe seguirla al pie de la letra si el estado real del repo muestra un camino mejor**, pero debe respetar los invariantes del TP y los guardrails. La parte obligatoria esta al final: despues de implementar/corregir, debe lanzar una auditoria con 6 subagentes de personalidades distintas y repetir el ciclo auditoria -> correccion -> auditoria hasta que no queden hallazgos relevantes.

### Supuestos y guardrails

- Trabajar en la rama `fable/tp-final-auditoria-integral-v1` o en una rama nueva derivada de ella.
- No borrar `tmp/`, `.nav`, `.snm`, `data/`, `figures/` ni `data_anim/` sin confirmacion explicita del grupo.
- No usar `git reset --hard`, `git checkout -- <path>` ni comandos destructivos para "limpiar" el repo.
- Si hay cambios locales ajenos, preservarlos y trabajar alrededor. Antes de editar, correr:

```bash
git status --short --branch
git log -1 --oneline --decorate
```

- Si se implementan fixes, hacer commits pequenos y revertibles por dominio. No pushear salvo que el duenio lo pida.
- Tests nuevos o modificados: unit-level, blackbox y behavior-only. No testear privados, strings internos, orden exacto de colaboradores ni detalles de framework.
- No prometer "perfecto" por intuicion. En este handoff, "perfecto" significa:
  - sin hallazgos P0/P1 abiertos;
  - P2/P3 documentados con decision explicita;
  - Java y pytest verdes;
  - informe y presentacion compilan o los PDFs finales versionados estan justificados;
  - no hay placeholders, URLs ficticias ni vocabulario prohibido;
  - los resultados no sobreprometen respecto del paper ni del modelo.

### Contexto obligatorio a leer

El agente controlador debe leer, como minimo:

```text
CLAUDE.md
README.md
diseno-tp-final-vdv-nasch_v1.md
extras/FD_VDV.pdf
2026-07-05_auditoria-codex-fable-tp-final_v1.md
2026-07-05_fable-auditoria-tp-final_v1.md
auditoria-jurados_v1.md
RESUMEN-IMPLEMENTACION_v1.md
informe/SdS_TPFinal_2026Q1G01S2_Informe.tex
presentacion/SdS_TPFinal_2026Q1G01S2_Presentacion.tex
analysis/*.py
analysis/tests/*.py
engine/src/main/java/ar/edu/itba/sds/**/*.java
engine/src/test/java/ar/edu/itba/sds/**/*.java
```

Puntos canonicos que no se deben romper:

- R2 oficial: contacto puro A. Variante B queda para validacion del NaSch canonico.
- Orden del paso: `R1 -> R3 -> R2 -> R4`.
- Observables siempre post-simulacion desde archivos de salida.
- Motor Java solo escribe estado fisico: `id`, `x[mm]`, `v[mm/s]`.
- `p` es probabilidad por paso.
- `L=1320 mm` / `5280` celdas como default de entrega; si se explora `1313 mm`, debe documentarse como sensibilidad.
- Una realizacion = condiciones iniciales + velocidades libres + secuencia reproducible del PRNG.
- Estacionario se decide por inspeccion, no por descarte fijo silencioso.

### Fase 0 - Estado base y bitacora

1. Crear o actualizar una bitacora de ejecucion, por ejemplo:

```text
YYYY-MM-DD_tp-final-agent-loop-ledger_v1.md
```

2. Registrar:
   - branch y commit inicial;
   - cambios locales no relacionados;
   - comandos corridos;
   - hallazgos por severidad;
   - agentes lanzados;
   - fixes aplicados;
   - criterios de cierre.

3. Correr verificacion base antes de corregir:

```bash
mvn -f engine/pom.xml test
python3 -m pytest analysis/tests -q
cd presentacion && pdflatex -interaction=nonstopmode -halt-on-error SdS_TPFinal_2026Q1G01S2_Presentacion.tex && pdflatex -interaction=nonstopmode -halt-on-error SdS_TPFinal_2026Q1G01S2_Presentacion.tex
cd ../informe && pdflatex -interaction=nonstopmode -halt-on-error SdS_TPFinal_2026Q1G01S2_Informe.tex && pdflatex -interaction=nonstopmode -halt-on-error SdS_TPFinal_2026Q1G01S2_Informe.tex
```

4. Correr chequeos de texto:

```bash
rg -n 'COMPLETAR|XXXX|1/44 mm|seed|sin_orden|TODO|FIXME' \
  README.md diseno-tp-final-vdv-nasch_v1.md informe presentacion \
  2026-07-05_auditoria-codex-fable-tp-final_v1.md \
  2026-07-05_fable-auditoria-tp-final_v1.md
```

Si algo falla, no corregir a ciegas: registrar el fallo, leer el archivo responsable y clasificar si es P0/P1/P2.

### Fase 1 - Plan de correccion recomendado

Usar los pendientes actuales como backlog inicial:

| Area | Recomendacion default | Alternativa | Riesgo si se ignora | Rollback |
|---|---|---|---|---|
| Reproducibilidad | Agregar un flujo documentado `make entrega` o script equivalente que regenere datos/figuras/PDFs desde cero o desde un manifiesto versionado. | Versionar PDFs finales y un manifiesto con checksums de datos/figuras si no hay tiempo para regeneracion completa. | Otro clon puede no reconstruir la entrega. | Revertir script/manifiesto y conservar PDFs finales versionados. |
| Estacionario incremental | Separar en el analisis las metricas de ventana completa de 180 s de las metricas declaradas como estacionarias. | Mantener ventana completa, pero explicitar en informe/presentacion que no es estacionario puro. | Sobreafirmar regimen estacionario en PDFs/FD. | Revertir cambios de analisis y dejar solo aclaracion metodologica. |
| Informe PDF | Compilar dos veces, revisar `pdftotext`, decidir si se versiona `SdS_TPFinal_2026Q1G01S2_Informe.pdf`. | No versionar PDF si el flujo de build es reproducible y documentado. | Entrega incompleta si el campus pide PDF. | Quitar PDF del commit si el grupo decide no versionar binarios. |
| Datos ignorados | Definir politica: ignorados regenerables o artefactos finales versionados con manifiesto. | Mantener ignorados, pero documentar comandos exactos y espacio/tiempo esperado. | Figuras del PDF no son auditables. | Volver a `.gitignore` previo y conservar solo docs. |
| `run_matrix.py --skip-existing` | Exigir out-dir limpio o manifestar duplicados por clave logica antes de correr. | Dejar la proteccion en `analyze.py` si el orquestador queda fuera de alcance. | Sesgo silencioso por corridas legacy. | Revertir validacion del orquestador; mantener test de analisis. |
| Dependencias Python | Fijar rangos razonables si se busca reproducibilidad. | Dejar flotante si priorizan facilidad de instalacion. | Futuras versiones rompen figuras/tests. | Revertir `requirements.txt`. |

### Fase 2 - Subagentes de implementacion sugeridos

Estos agentes son guia. El controlador puede reagrupar si detecta dependencias, pero debe evitar que dos agentes editen los mismos archivos al mismo tiempo.

1. **Agente Reproducibilidad/Entrega**
   - Objetivo: cerrar A5/B1 y los pendientes de reproducibilidad de entrega.
   - Archivos probables: `README.md`, `.gitignore`, posible `Makefile` o `scripts/`, `informe/`, `presentacion/`.
   - Debe decidir entre pipeline regenerable o manifiesto versionado.
   - Verificacion: build de informe/presentacion, `git diff --check`, chequeo anti-placeholders.

2. **Agente Estacionario/Observables**
   - Objetivo: evitar que PDFs/FD incrementales usen transitorios como estacionario sin aclararlo.
   - Archivos probables: `analysis/analyze.py`, `analysis/observables.py`, `analysis/tests/test_analyze.py`, informe.
   - Tests: behavior-only sobre salidas pequenas sinteticas que distingan ventana completa vs corte estacionario.
   - Verificacion: `python3 -m pytest analysis/tests -q`.

3. **Agente Motor/CLI**
   - Objetivo: revisar contratos de `Main`, `Config`, `OutputWriter`, incremental y duplicados.
   - Archivos probables: `engine/src/main/java/...`, `engine/src/test/java/...`.
   - Tests: comportamiento observable de CLI/salida, no detalles privados.
   - Verificacion: `mvn -f engine/pom.xml test`.

4. **Agente Documentos/PDF**
   - Objetivo: alinear informe y presentacion con Parisi, paper y diseno.
   - Archivos probables: `informe/*.tex`, `presentacion/*.tex`, README, auditorias.
   - Debe revisar PDFs compilados con `pdftotext`, no solo TeX.
   - Verificacion: `pdflatex` dos veces, `pdftotext`, chequeo anti-placeholders.

5. **Agente QA final**
   - Objetivo: despues de fixes, correr matriz de verificacion liviana y revisar diff.
   - Archivos: todos los modificados.
   - Debe reportar: comandos, resultados, cambios no relacionados, riesgos residuales.

### Fase 3 - Matriz de verificacion minima

Antes de declarar cierre:

```bash
git status --short --branch
git diff --check
mvn -f engine/pom.xml test
python3 -m pytest analysis/tests -q

cd presentacion
pdflatex -interaction=nonstopmode -halt-on-error SdS_TPFinal_2026Q1G01S2_Presentacion.tex
pdflatex -interaction=nonstopmode -halt-on-error SdS_TPFinal_2026Q1G01S2_Presentacion.tex
pdftotext SdS_TPFinal_2026Q1G01S2_Presentacion.pdf -

cd ../informe
pdflatex -interaction=nonstopmode -halt-on-error SdS_TPFinal_2026Q1G01S2_Informe.tex
pdflatex -interaction=nonstopmode -halt-on-error SdS_TPFinal_2026Q1G01S2_Informe.tex
pdftotext SdS_TPFinal_2026Q1G01S2_Informe.pdf -
```

Chequeos textuales:

```bash
rg -n 'COMPLETAR|XXXX|1/44 mm|seed|sin_orden|TODO|FIXME' \
  README.md diseno-tp-final-vdv-nasch_v1.md informe presentacion \
  2026-07-05_auditoria-codex-fable-tp-final_v1.md \
  2026-07-05_fable-auditoria-tp-final_v1.md
```

Si se tocaron datos/figuras, agregar:

```bash
python3 analysis/analyze.py --data-dir data --figures-dir figures
```

o justificar por que no se puede correr por costo/ausencia de datos locales.

## Prompt maestro para dejar corriendo el loop de subagentes

Copiar y pegar este prompt en un agente nuevo desde la raiz del repo. La primera parte es guia flexible; la fase final de seis auditores es obligatoria.

```markdown
Estas trabajando en el repo:

`/Users/keoni/Claude-Workspace/projects/sds-entregas/tp-final-sds-2026Q1G01S2`

Objetivo: dejar el TP Final SdS G01S2 listo para entrega, corrigiendo de principio a fin motor, analisis, reproducibilidad, informe y presentacion. Usa el handoff `2026-07-06_handoff-tp-final-auditoria_v1.md` como base. No lo sigas mecanicamente si el repo contradice algo: manda el estado real del checkout.

Instrucciones obligatorias:

1. Usa `superpowers:using-superpowers`.
2. Lee `CLAUDE.md` antes de tocar nada.
3. Lee `README.md`, `diseno-tp-final-vdv-nasch_v1.md`, `extras/FD_VDV.pdf`, las auditorias `2026-07-05_*`, `auditoria-jurados_v1.md`, informe y presentacion.
4. No borres archivos ni limpies auxiliares sin confirmacion.
5. Tests nuevos/modificados: unit-level, blackbox, behavior-only.
6. Si hay cambios locales ajenos, preservalos.
7. Trabaja con commits pequenos y revertibles. No pushees salvo instruccion explicita.
8. Mantene una bitacora `YYYY-MM-DD_tp-final-agent-loop-ledger_v1.md` con hallazgos, fixes, comandos y estado.

Plan guia:

1. Hacer baseline:
   - `git status --short --branch`
   - `git log -1 --oneline --decorate`
   - `mvn -f engine/pom.xml test`
   - `python3 -m pytest analysis/tests -q`
   - compilar presentacion e informe dos veces con `pdflatex`
   - revisar PDFs con `pdftotext`
   - correr chequeo anti-placeholders con `rg`

2. Corregir backlog inicial si sigue vigente:
   - reproducibilidad de datos/figuras/PDFs;
   - estacionario vs ventana completa en incremental;
   - informe PDF final;
   - politica de artefactos ignorados;
   - proteccion contra duplicados legacy/out-dir sucio;
   - dependencias Python si afectan reproducibilidad;
   - cualquier desalineacion entre paper, diseno, README, informe y presentacion.

3. Para cada fix:
   - escribir o ajustar test behavior-only cuando aplique;
   - implementar el minimo cambio;
   - correr el test especifico;
   - correr la suite relevante;
   - revisar diff;
   - registrar en la bitacora;
   - commit local pequeno.

4. Cuando creas que esta corregido, NO cierres todavia. Ejecuta obligatoriamente el loop de seis auditores.

Fase obligatoria: auditoria con 6 subagentes de personalidades distintas

Despacha en paralelo 6 subagentes read-only. Cada uno debe devolver hallazgos con severidad, evidencia `archivo:linea`, razonamiento, fix recomendado y verificacion necesaria. Si no encuentra nada, debe decir `SIN HALLAZGOS` y explicar que reviso.

Subagente 1 - Fisico experimental severo
- Personalidad: actua como Parisi corrigiendo con lupa de metodologia experimental.
- Foco: fidelidad al paper Patterson & Parisi, VDV, protocolo incremental 180 s, ordenes de insercion, densidad, velocidad, estacionario, limitaciones.
- Debe leer: `extras/FD_VDV.pdf`, `diseno-tp-final-vdv-nasch_v1.md`, informe, presentacion, README.
- Preguntas: el texto sobrepromete? se confunde contacto puro con NaSch canonico? se usa bien `1/(44 mm)`? se aclara N=30 singular? se distingue parametros de condiciones iniciales?

Subagente 2 - Ingeniera de motor paranoica
- Personalidad: piensa en invariantes, contratos y casos borde.
- Foco: Java, CLI, `Config`, `NaSchEngine`, `CollisionRule`, incremental, `OutputWriter`.
- Debe leer: `engine/src/main/java`, `engine/src/test/java`, README, diseno.
- Preguntas: puede haber solapamiento? `R1 -> R3 -> R2 -> R4` esta preservado? `p=0` no consume PRNG? `--even-spread` no falsea incremental? salida fisica solamente? frontera incremental documentada?

Subagente 3 - Estadistica/analisis esceptica
- Personalidad: desconfia de promedios, errores y agrupamientos.
- Foco: Python, observables, errores entre realizaciones, duplicados, metadata, estacionario, PDFs, FD.
- Debe leer: `analysis/*.py`, `analysis/tests/*.py`, auditorias, informe.
- Preguntas: hay promedio-de-promedios? se mezclan `rule/order/protocol/p`? se detectan duplicados? `p-representativo` falla si falta? las PDFs no aceptan NaN? los cortes estacionarios son explicitos?

Subagente 4 - Editor academico implacable
- Personalidad: corrector de informe/presentacion que prioriza claridad y defensa oral.
- Foco: LaTeX, estructura Resultados, conclusiones solo al final, terminologia en espanol, figuras, captions, links, placeholders.
- Debe leer: `informe/*.tex`, `presentacion/*.tex`, PDFs compilados si existen, `README.md`, `CLAUDE.md`.
- Preguntas: hay anglicismos evitables? las figuras tienen unidades? el relato sigue animacion -> evolucion temporal -> curva respuesta-estimulo? hay afirmaciones sin respaldo?

Subagente 5 - Release/reproducibilidad obsesiva
- Personalidad: no acepta entregas que solo funcionan en la laptop actual.
- Foco: build reproducible, `.gitignore`, datos/figuras, checksums, README, comandos, dependencias.
- Debe leer: `.gitignore`, README, `analysis/requirements.txt`, scripts, estado de `data/`, `figures/`, `data_anim/`, `informe`, `presentacion`.
- Preguntas: desde un clon limpio se puede generar o auditar lo entregado? que binarios deben versionarse? hay manifiesto de figuras? las instrucciones tienen versiones/tiempo/disco esperados?

Subagente 6 - Jurado adversarial de defensa
- Personalidad: profesor exigente que busca la pregunta que haria caer la entrega.
- Foco: coherencia global entre codigo, paper, informe, presentacion, auditorias y README.
- Debe leer: todo lo anterior a nivel de integracion.
- Preguntas: si el docente pregunta "por que este p?", "por que L=1320?", "que valida B?", "que no reproduce el modelo?", "como decidieron estacionario?", la entrega responde sin contradicciones?

Formato requerido de cada auditor:

| Severidad | Hallazgo | Evidencia | Riesgo | Fix recomendado | Verificacion |
|---|---|---|---|---|---|

Severidades:
- P0: rompe correccion cientifica, compila mal, entrega incompleta o resultado no reproducible.
- P1: afirmacion peligrosa, sesgo metodologico, test/contrato importante faltante.
- P2: mejora importante pero no bloqueante.
- P3: estilo, claridad o mantenimiento menor.

Despues de recibir los 6 reportes:

1. Consolidar en la bitacora un unico backlog deduplicado.
2. Si hay P0/P1, NO cerrar.
3. Despachar nuevos subagentes de correccion por dominio. No reutilices los auditores como correctores sin darles un prompt nuevo y scope cerrado.
4. Cada corrector debe:
   - modificar solo su scope;
   - agregar tests behavior-only si aplica;
   - correr comandos especificos;
   - devolver diff summary, pruebas y riesgos.
5. Integrar fixes uno por uno, revisar conflictos y correr suites relevantes.
6. Al terminar fixes, correr la matriz minima:
   - `git diff --check`
   - `mvn -f engine/pom.xml test`
   - `python3 -m pytest analysis/tests -q`
   - `pdflatex` dos veces para presentacion e informe
   - `pdftotext` de PDFs
   - `rg` anti-placeholders
7. Volver a despachar 6 auditores nuevos. Dales el estado actualizado, la bitacora y el diff desde el ultimo ciclo.
8. Repetir auditoria -> correccion -> verificacion hasta que:
   - los 6 auditores devuelvan `SIN HALLAZGOS` o solo P3 aceptados;
   - no haya P0/P1 abiertos;
   - los P2 tengan fix aplicado o decision explicita del grupo;
   - todas las verificaciones esten verdes;
   - el diff final este revisado.

Criterio de parada:

- No declares "perfecto" si solo se acabo el tiempo o el presupuesto.
- Si quedas bloqueado por falta de datos, PDF imposible de compilar, dependencia faltante o decision academica, deja el bloqueo exacto, los comandos, el error y la decision que necesita el grupo.
- Si cierras, entrega:
  - resumen diff-like;
  - commits locales creados;
  - comandos corridos y resultados;
  - hallazgos cerrados;
  - riesgos residuales;
  - proximo paso humano.
```

## Comandos utiles para continuar

```bash
cd /Users/keoni/Claude-Workspace/projects/sds-entregas/tp-final-sds-2026Q1G01S2
git status --short --branch
git log -1 --oneline --decorate
mvn -f engine/pom.xml test
python3 -m pytest analysis/tests -q
```

Compilar presentacion:

```bash
cd /Users/keoni/Claude-Workspace/projects/sds-entregas/tp-final-sds-2026Q1G01S2/presentacion
pdflatex -interaction=nonstopmode -halt-on-error SdS_TPFinal_2026Q1G01S2_Presentacion.tex
pdflatex -interaction=nonstopmode -halt-on-error SdS_TPFinal_2026Q1G01S2_Presentacion.tex
```

Compilar informe:

```bash
cd /Users/keoni/Claude-Workspace/projects/sds-entregas/tp-final-sds-2026Q1G01S2/informe
pdflatex -interaction=nonstopmode -halt-on-error SdS_TPFinal_2026Q1G01S2_Informe.tex
pdflatex -interaction=nonstopmode -halt-on-error SdS_TPFinal_2026Q1G01S2_Informe.tex
```

Chequeo anti-placeholders:

```bash
rg -n 'COMPLETAR|XXXX|1/44 mm|seed|sin_orden|TODO|FIXME' \
  informe presentacion README.md diseno-tp-final-vdv-nasch_v1.md \
  2026-07-05_auditoria-codex-fable-tp-final_v1.md \
  2026-07-05_fable-auditoria-tp-final_v1.md
```

## Suggested skills

- `superpowers:using-superpowers`: arrancar siguiendo skills del entorno.
- `superpowers:dispatching-parallel-agents`: lanzar los 6 auditores read-only en paralelo.
- `superpowers:subagent-driven-development`: ejecutar fixes con subagentes y revisiones por tarea.
- `superpowers:verification-before-completion`: antes de decir que algo esta listo, correr comandos frescos.
- `superpowers:test-driven-development`: si se cambia motor o analisis, agregar/ajustar tests behavior-only.
- `review`: si el siguiente paso es auditar la rama sin editar.
- `pdf`: si se inspeccionan PDFs finales o se comparan contra el `.tex`.

## Criterio de cierre sugerido

Antes de entregar o pedir aprobacion:

- `git status` sin cambios inesperados.
- Java y pytest verdes.
- Informe y presentacion compilan o los PDFs finales estan versionados.
- No quedan placeholders ni URLs ficticias.
- El texto no sobrepromete: contacto puro A no es la validacion triangular; el colapso bajo el mas lento requiere `p>0`; el punto `N=30` es singular; los observables salen post-simulacion.
