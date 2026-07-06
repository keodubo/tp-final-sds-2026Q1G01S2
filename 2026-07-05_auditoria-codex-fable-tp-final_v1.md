# Auditoria Codex sobre rama Fable TP Final SdS

- **Fecha:** 2026-07-05
- **Branch auditado:** `fable/tp-final-auditoria-integral-v1`
- **Baseline:** `main` (`82e6479d24ba9c4c479156fa7df6847693b4856a`)
- **Rango revisado:** `git diff main...HEAD` / `git log main..HEAD`
- **Veredicto inicial:** **no aprobar como entregable todavia**.
- **Estado tras correcciones 2026-07-05:** se corrigieron los bloqueantes principales de
  compilacion visible y varios contratos de motor/analisis. Queda pendiente una verificacion final
  desde un checkout limpio y decidir si se versionan PDFs/figuras finales.

El codigo verifica bastante bien, pero la rama no esta lista como entrega: los `.tex` no compilan desde un checkout limpio, el reporte Fable afirma evidencia que el estado actual contradice, y hay problemas de contrato en motor/analisis que pueden contaminar resultados incrementales.

> Actualizacion 2026-07-05: luego de esta auditoria se aplicaron fixes por subagentes en tres scopes:
> motor/CLI, analisis Python y documentos/LaTeX. Esta seccion conserva la evidencia original y el plan
> de remediacion; ver "Estado post-correccion" al final para el cierre real.

## Jurado usado

Se usaron cinco subagentes read-only con lentes independientes:

| Jurado | Personalidad | Foco |
|---|---|---|
| Fisica/catedra | severo estilo Parisi | contrato del paper, vocabulario, no sobreprometer |
| Motor/CLI | arquitecto de contratos | defaults, `--even-spread`, cabeceras, salida publica |
| Analisis | estadistico esceptico | agrupaciones, estacionario, PDFs, FD, tests |
| Entregables | jurado de defensa | informe, presentacion, compilacion LaTeX, placeholders |
| Reproducibilidad | CI desconfiado | clone limpio, `.gitignore`, artefactos, comandos |

## Hallazgos bloqueantes

### B1. Los entregables LaTeX no compilan desde limpio

**Evidencia**

- [informe/SdS_TPFinal_2026Q1G01S2_Informe.tex](informe/SdS_TPFinal_2026Q1G01S2_Informe.tex:304) referencia `N5_p01_CONTACTO_PURO_FIXED_N_oe1_r1_fotograma.png`.
- [presentacion/SdS_TPFinal_2026Q1G01S2_Presentacion.tex](presentacion/SdS_TPFinal_2026Q1G01S2_Presentacion.tex:190) referencia el mismo patron.
- Los archivos locales reales venian como `N5_p01_CONTACTO_PURO_FIXED_N_r1_fotograma.png`, sin `_oe1_`.
- Los `.tex` tambien pedian nombres legacy de orden fijo, mientras los datos actuales de `FIXED_N`
  venian con `order=RANDOM` y `analyze.py` generaba nombres `*_random_fixed`.
- [.gitignore](.gitignore:17) ignora `figures/*` y [.gitignore](.gitignore:19) ignora `data_anim/`.

**Impacto**

Un evaluador que clone el repo no puede compilar informe/presentacion. Localmente pude generar el PDF de presentacion solo despues de crear 4 alias en carpetas ignoradas:

- `data_anim/N5_p01_CONTACTO_PURO_FIXED_N_oe1_r1_fotograma.png`
- `data_anim/N30_p01_CONTACTO_PURO_FIXED_N_oe1_r1_fotograma.png`
- `figures/evolucion_temporal_contacto_puro_<orden-fijo>_fixed.png`
- `figures/velocidad_media_vs_N_contacto_puro_<orden-fijo>_fixed.png`

**Correccion recomendada**

Alinear nombres entre `run_matrix.py`/`animate.py`/`analyze.py` y los `.tex`, o versionar/publicar los PDFs finales como artefactos de entrega. La ruta mas confiable es agregar un `Makefile` o script `make entrega` que regenere `data`, `figures`, `data_anim` y compile ambos PDFs desde cero.

### B2. La auditoria Fable sobreafirma verificaciones que no se sostienen

**Evidencia**

- [2026-07-05_fable-auditoria-tp-final_v1.md](2026-07-05_fable-auditoria-tp-final_v1.md:111) afirma `37 PNG + manifiesto.csv`.
- [2026-07-05_fable-auditoria-tp-final_v1.md](2026-07-05_fable-auditoria-tp-final_v1.md:114) afirma que informe/presentacion compilan.
- En el checkout actual, `pdflatex` falla antes de los alias locales por PNG faltante.
- El reporte cita evidencia en `.fable-tmp/...` ([2026-07-05_fable-auditoria-tp-final_v1.md](2026-07-05_fable-auditoria-tp-final_v1.md:15)), pero [.gitignore](.gitignore:31) ignora `.fable-tmp/`.

**Impacto**

El documento de auditoria no es una fuente confiable para aceptar el branch. Un tercero no puede comprobar los "16 jurados" ni reproducir la afirmacion de compilacion.

**Correccion recomendada**

Reescribir ese reporte o reemplazarlo por una auditoria autocontenida con comandos reproducibles, conteos actuales, hash/base y logs de build. Si se conserva evidencia de jurados, versionar un resumen minimo no sensible.

## Hallazgos altos

### A1. `--even-spread` puede generar una corrida falsamente incremental

**Evidencia**

- [engine/src/main/java/ar/edu/itba/sds/Main.java](engine/src/main/java/ar/edu/itba/sds/Main.java:83) llama `initializeEvenlySpread()` si la bandera esta activa.
- [engine/src/main/java/ar/edu/itba/sds/sim/NaSchEngine.java](engine/src/main/java/ar/edu/itba/sds/sim/NaSchEngine.java:126) crea los `config.n()` vehiculos desde el inicio y vacia `pendientes`.

Un jurado probo `--protocol INCREMENTAL_180S --order ASCENDING --n 30 --steps 3 --even-spread`: la cabecera dice incremental, pero la salida ya tiene 30 vehiculos en los pasos 0, 1 y 2. Sin `--even-spread`, empieza en 5.

**Impacto**

La salida parece paper-protocol 5->30, pero no lo es. `analysis/` la acepta como incremental, asi que puede contaminar figuras y conclusiones.

**Correccion recomendada**

Fail-fast si `--even-spread` se combina con `INCREMENTAL_180S`. Si `--even-spread` es solo para validacion triangular, restringirlo/documentarlo con `p=0`, variante B, `FIXED_N`, homogeneo.

### A2. PDFs y diagrama fundamental incrementales usan transitorios como si fueran regimen

**Evidencia**

- [analysis/analyze.py](analysis/analyze.py:140) registra `since_step=0` para `INCREMENTAL_180S`.
- [analysis/analyze.py](analysis/analyze.py:285) fuerza `since_step=0` en PDFs incrementales.
- [analysis/analyze.py](analysis/analyze.py:309) fuerza corte 0 en FD incremental.
- El diseno exige estacionario por inspeccion y manifiesto ([diseno-tp-final-vdv-nasch_v1.md](diseno-tp-final-vdv-nasch_v1.md:184)).

**Impacto**

La Fig. 2 del paper usa ventana completa de 180 s por fase, pero las PDFs y FD que se presentan como regimen quedan mezcladas con transitorios de insercion/empuje. Eso puede mover distribuciones y suavizados, especialmente cerca de las fronteras de lote.

**Correccion recomendada**

Separar productos:

1. velocidad media por fase completa de 180 s para comparacion con Fig. 2;
2. PDFs/FD de regimen con corte por fase `(protocolo, orden, p, N activo)`, guardado en manifiesto.

### A3. `--skip-existing` puede duplicar realizaciones legacy y sesgar errores

**Evidencia**

- [analysis/run_matrix.py](analysis/run_matrix.py:43) cambio los tags a incluir `_oe{output_every}`.
- [analysis/run_matrix.py](analysis/run_matrix.py:120) solo saltea si existe exactamente el nuevo nombre.
- [analysis/analyze.py](analysis/analyze.py:187) carga todos los `*.txt`.
- [analysis/analyze.py](analysis/analyze.py:148) usa `len(rs)` como M.

**Impacto**

El `data/` local tiene 2700 archivos legacy sin `_oe`. Si se vuelve a correr con `--skip-existing`, no los reconoce y puede generar duplicados con nuevo nombre. Despues `analyze.py` los cuenta como realizaciones adicionales, inflando M y sesgando errores.

**Correccion recomendada**

Exigir `--out-dir` limpio o detectar duplicados por clave logica `(protocolo, regla, orden, p, N, realizacion_id, output_every)`. Si hay duplicado, fallar con mensaje claro.

### A4. Placeholders incompatibles con entrega

**Evidencia**

- [presentacion/SdS_TPFinal_2026Q1G01S2_Presentacion.tex](presentacion/SdS_TPFinal_2026Q1G01S2_Presentacion.tex:31) contenia un placeholder de nombres y legajos.
- [presentacion/SdS_TPFinal_2026Q1G01S2_Presentacion.tex](presentacion/SdS_TPFinal_2026Q1G01S2_Presentacion.tex:199) contenia una URL ficticia de YouTube.
- [informe/SdS_TPFinal_2026Q1G01S2_Informe.tex](informe/SdS_TPFinal_2026Q1G01S2_Informe.tex:308) y [informe/SdS_TPFinal_2026Q1G01S2_Informe.tex](informe/SdS_TPFinal_2026Q1G01S2_Informe.tex:375) contenian URLs ficticias.

**Impacto**

El PDF se veia como maqueta, no como entregable final. `pdfinfo` del PDF generado mantenia autores incompletos.

**Correccion recomendada**

Completar autores/legajos y reemplazar links por URLs reales no listadas, o quitar la promesa de video hasta tenerlos.

### A5. Los artefactos de resultados no son reproducibles desde el repo

**Evidencia**

- [.gitignore](.gitignore:15) ignora `data/*`.
- [.gitignore](.gitignore:17) ignora `figures/*`.
- [.gitignore](.gitignore:19) ignora `data_anim/`.
- [README.md](README.md:171) todavia dice que falta correr el barrido, mientras la auditoria Fable afirma que ya fue corrido.

**Impacto**

No hay una frontera clara entre "codigo que genera resultados" y "resultados usados en el informe". El repo no permite verificar los graficos del PDF sin depender del estado local.

**Correccion recomendada**

Elegir una politica:

- trackear PDFs finales y, como minimo, `figures/manifiesto.csv` + checksums de datos;
- o no trackear resultados, pero agregar un script reproducible de generacion completa y tiempos esperados;
- alinear README, informe y auditoria con esa politica.

## Hallazgos medios

### M1. `order` en `FIXED_N` puede fragmentar datasets

Java escribe `order=SIN_ORDEN` para `FIXED_N` ([OutputWriter.java](engine/src/main/java/ar/edu/itba/sds/io/OutputWriter.java:45)), pero `analyze.py` agrupa por el `order` literal ([analysis/analyze.py](analysis/analyze.py:54)). Datasets viejos con `order=RANDOM` quedan separados de los nuevos `SIN_ORDEN`.

**Correccion:** canonicalizar en analisis: si `protocol == FIXED_N`, usar siempre `SIN_ORDEN`; test behavior-only que mezcle headers legacy y nuevos sin fragmentar M.

### M2. `--p-representativo` cae silenciosamente a otro `p`

[analysis/analyze.py](analysis/analyze.py:215) y [analysis/analyze.py](analysis/analyze.py:265) convierten el `p` pedido a `None` si falta en un grupo. Eso puede producir figuras rotuladas o comparadas como `p=0.1` en unas variantes y otro `p` en otras.

**Correccion:** fail-fast por grupo o emitir warning/manifiesto explicito de faltantes.

### M3. Frontera incremental no es exactamente ventana completa de 180 s

[Main.java](engine/src/main/java/ar/edu/itba/sds/Main.java:93) escribe el estado antes de `engine.step()`, y [NaSchEngine.java](engine/src/main/java/ar/edu/itba/sds/sim/NaSchEngine.java:167) inserta lotes dentro de `step()`. En la frontera, el registro de `t=4320` todavia pertenece a N viejo; N nuevo aparece en el siguiente registro. El informe dice ventana completa por fase ([informe](informe/SdS_TPFinal_2026Q1G01S2_Informe.tex:289)).

**Correccion:** insertar antes de escribir en la frontera o documentar ventanas semiabiertas y guardar `fase`/`N_activo` explicito.

### M4. Frase peligrosa: `p=0` parece igualar contacto puro con NaSch canonico

[informe](informe/SdS_TPFinal_2026Q1G01S2_Informe.tex:129) dice que con `p=0` el esquema coincide con NaSch canonico. Eso solo es cierto para el orden de reglas o para variante B; contacto puro A no valida contra la triangular.

**Correccion:** "con `p=0` el orden se reduce a R1->R2->R4; solo la variante B coincide con NaSch canonico".

### M5. Notacion dimensional de densidad de contacto

Aparecia notacion dimensional ambigua para la densidad de contacto en [presentacion](presentacion/SdS_TPFinal_2026Q1G01S2_Presentacion.tex:228) e [informe](informe/SdS_TPFinal_2026Q1G01S2_Informe.tex:347). Como densidad debe ser `1/(44 mm)` o `0.0227 mm^{-1}`.

**Correccion:** reemplazar por `1/(44\,\mathrm{mm}) = 0.0227\,\mathrm{mm}^{-1}`.

### M6. Test de PDF de densidad pasa aunque haya NaN

[analysis/tests/test_observables.py](analysis/tests/test_observables.py:116) solo verifica shape. En mi corrida `pytest` paso con `RuntimeWarning: invalid value encountered in divide`; podria pasar aunque una curva de PDF sea todo NaN.

**Correccion:** usar posiciones validas y assertar `np.isfinite(pdf).all()` + integral aproximada.

### M7. Documentacion y dependencias menores

- [diseno](diseno-tp-final-vdv-nasch_v1.md:179) todavia dice que el default inicial es B, pero el default actual es `CONTACTO_PURO`.
- [analysis/requirements.txt](analysis/requirements.txt:11) deja `pytest>=8.0` flotante.
- Hay anglicismos residuales (`vibration-driven vehicles`, `random`, identificador tecnico de PRNG) en entregables; pueden defenderse tecnicamente, pero la instruccion local pide espanol sin anglicismos.

## PDF de presentacion generado

La presentacion no compilaba inicialmente por assets faltantes. Para inspeccion visual, hice lo siguiente:

1. Regenere `validacion_triangular.png` con `python3 validacion.py`.
2. Ejecute `python3 analyze.py --data-dir ../data --figures-dir ../figures`; lo interrumpi despues de que genero los assets necesarios para el deck porque el analisis completo siguio varios minutos y estaba en `np.convolve` de FD.
3. Cree 4 alias locales en carpetas ignoradas para empatar nombres esperados por el `.tex`.
4. Compile `presentacion/SdS_TPFinal_2026Q1G01S2_Presentacion.tex` dos veces con `pdflatex`.

Resultado:

- PDF generado: `presentacion/SdS_TPFinal_2026Q1G01S2_Presentacion.pdf`
- `pdfinfo`: 17 paginas, 912594 bytes.
- `pdftotext` todavia detectaba placeholders y una URL ficticia.
- Contact sheet renderizada para QA visual: `tmp/pdfs/presentacion-contact-sheet.png`.

Conclusion: el PDF generado sirve para revisar layout, pero **no prueba reproducibilidad limpia** porque dependio de alias no versionados.

## Verificaciones ejecutadas por Codex

| Comando / accion | Resultado |
|---|---|
| `git rev-parse main`, `git merge-base main HEAD`, `git log main..HEAD` | baseline `82e6479`, 10 commits Fable |
| `git diff --stat main...HEAD` | 20 archivos, 1660 inserciones, 274 borrados |
| `mvn -q -f engine/pom.xml clean package` | OK |
| `python3 -m pytest analysis/tests -q` | 29 passed, 1 warning NumPy |
| `python3 validacion.py` | `validacion_triangular.png`, error max `1.11e-16` |
| `python3 analyze.py --data-dir ../data --figures-dir ../figures` | interrumpido tras generar assets necesarios; seguia en FD/convolve |
| `pdflatex` presentacion antes de alias | falla por PNG faltante |
| `pdflatex` presentacion despues de alias | OK x2, 17 paginas |
| `pdftoppm` + inspeccion visual | PDF no vacio; placeholders visibles |
| `git diff --check main...HEAD` | limpio |

## Estado post-correccion

Correcciones aplicadas despues de la auditoria:

- Motor/CLI: `--even-spread` ahora falla si se combina con `INCREMENTAL_180S`; se agrego un test
  behavior-only y se documento la semantica actual de frontera incremental `write-before-step`.
- Analisis: `FIXED_N` canonicaliza `order` a `SIN_ORDEN`, se detectan corridas duplicadas por clave
  logica, `--p-representativo` deja de caer silenciosamente a otro `p`, y el test de PDF de densidad
  exige valores finitos e integral aproximada.
- Documentos/LaTeX: se corrigieron nombres de assets a los generados reales, se removieron placeholders
  y URLs ficticias, se corrigio la notacion `1/(44 mm)`, se aclaro el alcance de `p=0`, y el
  diseno ya declara `CONTACTO_PURO` como default actual.

Queda pendiente:

- Ejecutar verificacion final integrada desde este worktree y, si se quiere una entrega autocontenida,
  decidir si los PDFs finales/figuras deben versionarse o regenerarse por un target reproducible.
- El hallazgo sobre PDFs/FD incrementales con `since_step=0` sigue siendo una decision metodologica
  pendiente: la velocidad media de Fig. 2 puede usar ventana completa de 180 s, pero PDFs/FD de regimen
  deberian tener corte estacionario por fase si se los presenta como estacionarios.

## Estado del workspace tras la auditoria inicial

Se agrego este archivo de auditoria. Ademas quedaron artefactos generados para inspeccion:

- `presentacion/SdS_TPFinal_2026Q1G01S2_Presentacion.pdf`
- `presentacion/SdS_TPFinal_2026Q1G01S2_Presentacion.nav`
- `presentacion/SdS_TPFinal_2026Q1G01S2_Presentacion.snm`
- `tmp/pdfs/presentacion-contact-sheet.png`
- figuras regeneradas/alias en `figures/` y `data_anim/` (ignoradas por git)

Nota historica: esta frase aplicaba al primer cierre read-only. En el pase posterior si se modificaron
`engine/`, `analysis/` y documentos/LaTeX mediante subagentes correctores.

## Plan de remediacion recomendado

1. **Primero arreglar reproducibilidad de entrega.** Alinear nombres de assets y hacer que informe/presentacion compilen desde `git archive HEAD` sin estado local oculto.
2. **Cerrar bugs de contrato.** Bloquear `--even-spread + INCREMENTAL_180S`, canonicalizar `FIXED_N` a `SIN_ORDEN`, y detectar duplicados legacy en `data/`.
3. **Separar productos de analisis incremental.** Fig. 2 por ventana completa; PDFs/FD con corte estacionario por fase y manifiesto.
4. **Limpiar entregables.** Completar nombres/legajos, links reales o removerlos, corregir la densidad de contacto a `1/(44 mm)`, aclarar `p=0`/NaSch canonico, actualizar default del diseno.
5. **Reauditar en limpio.** Correr desde un clone/archive limpio: build motor, barrido o fixture reducido, generacion de figuras, compilacion de ambos PDFs, y comparacion de conteos/checksums.
