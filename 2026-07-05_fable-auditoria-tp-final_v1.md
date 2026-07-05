# Auditoría integral TP Final SdS (NaSch + VDV) — reporte final

- **Base SHA:** `82e6479d24ba9c4c479156fa7df6847693b4856a`
- **Branch:** `fable/tp-final-auditoria-integral-v1`
- **Fecha:** 2026-07-05
- **Alcance:** auditoría adversarial read-only → correcciones de motor/análisis → regeneración de
  datos/figuras/animaciones → informe y presentación finales.

> Nota de continuidad: la fase read-only (panel de jurados) se ejecutó en una sesión previa que se
> interrumpió (corte de energía) justo después de escribir el *gate*, sin haber hecho ninguna edición.
> Esta sesión retomó desde el *gate* y ejecutó todas las correcciones y entregables.

## 1. Panel de subagentes (fase read-only) y veredicto

16 jurados read-only + síntesis + coordinador (evidencia en `.fable-tmp/jurors.json`, `synth.json`,
`gate.md`, `notas-coordinador.md`). **Veredicto global: MIXTO** — el motor **no tiene bug de física**
(NaSch, orden R1→R3→R2→R4, contacto puro y no-solapamiento verificados), pero había:
*datos insuficientes* (nada generado en este checkout), *correcciones de análisis/config* y el
*informe en esqueleto sin presentación*. En esta sesión se agregó 1 subagente ejecutor (rediseño de
animaciones), que devolvió 13 tests verdes y fotogramas defendibles.

Problemas consolidados: 32 (3 bloqueantes, 11 altas, 14 medias, 4 bajas). Todos los de código/análisis
se resolvieron; quedan 2 bloqueantes **externos** (solo el humano puede completarlos, ver §7).

## 2. Cambios por commit (sobre `82e6479`)

| # | Commit | Qué resuelve |
|---|--------|--------------|
| 1 | `test(engine)`: batería RED de contratos CLI, defaults y cabecera | COV-1..6, CLI-01/03, G19 (anclas RED + cobertura) |
| 2 | `fix(engine)`: CONTACTO_PURO por defecto, fail-fast CLI, `--even-spread`, cabecera FIXED_N | CLI-01/02/03, RM-03/G14, G19 |
| 3 | `chore(repro)`: fijar versiones e ignorar documentos de trabajo | G27 |
| 4 | `fix(analysis)`: estacionario data-dependiente, PDFs incrementales por orden, FD coherente | F1/F2, FIG-01/02, EST-1/2, F3, G29 |
| 5 | `feat(analysis)`: rediseño de animaciones/fotogramas hero + tests | ANIM-01..07 |
| 6 | `fix(analysis)`: run_matrix default CONTACTO_PURO, idempotencia, docstring | RM-01/02/04/05 |
| 7 | `data`: regeneración del barrido + figuras + heroes (generados, no versionados) | G01 |
| 8 | `docs(informe)`: informe final | G03/G08/G09/G10/G17/G18/G20/G21/G22/G23, SC-01/02/03 |
| 9 | `docs(presentacion)`: Beamer autocontenida | G02 |
| 10 | `docs(auditoria)`: este reporte | — |

## 3. Correcciones destacadas (motor y análisis)

- **Regla por defecto** ahora `CONTACTO_PURO` (oficial) en `Config.defaults()` y en `run_matrix.py`
  (antes `CLASICA_SALVO_CERO`, variante de validación, corría fuera de su régimen).
- **CLI robusto**: un token suelto sin guion ahora es error (antes revertía a defaults en silencio);
  `--even-spread` habilita la validación analítica por CLI; `--help` documenta `--transient` y
  `--even-spread`.
- **Cabecera**: `FIXED_N` escribe `order=SIN_ORDEN` (antes filtraba el default `RANDOM` y se confundía
  con el protocolo incremental ordenado).
- **detect_stationary** ya no degenera al descarte fijo del 50 % (`n//2`): el suavizado usaba padding de
  ceros que arrastraba los bordes. Ahora el corte depende de los datos (regla de cátedra 5).
- **PDFs incrementales por N activo** (`density_pdf_by_active_n`, `velocity_pdf_by_active_n`): reproducen
  las Figs. 3 y 4 del artículo por orden sin mezclar fases N=5..30.
- **Evolución temporal del incremental** por orden (sin ella no se podía elegir el estacionario por
  inspección) y **diagrama fundamental con criterio consistente** (FIXED: corte por inspección;
  incremental: ventana completa ⟨L_i/180 s⟩).
- **Manifiesto** con `since_step` por fila y M efectivo por punto.
- **Animaciones** rediseñadas: realización, N activo/nominal, sentido de avance, reentrada periódica,
  color anclado a `vfree_max`, fotograma en régimen; funciones puras + `test_animate.py`.

## 4. Matriz de datos regenerada

Comando (desde `analysis/`):

```bash
python3 run_matrix.py --out-dir ../data \
  --rule CONTACTO_PURO CLASICA_SALVO_CERO \
  --protocol FIXED_N INCREMENTAL_180S \
  --order ASCENDING DESCENDING RANDOM \
  --n 5 10 15 20 25 30 --p 0 0.1 0.2 0.3 0.4 \
  --realizations 30 --output-every 10 --skip-existing
```

2700 corridas = 1800 `FIXED_N` (6 N × 5 p × 2 reglas × 30) + 900 `INCREMENTAL_180S`
(5 p × 2 reglas × 3 órdenes × 30). `output_every=10`; `steps` 10000 (fijo) / 25920 (incremental).
Heroes de animación en `../data_anim` (5 corridas dedicadas). Datos y figuras están **fuera de git**
(gitignored); se regeneran con el comando de arriba + `analyze.py`.

Figuras (desde `analysis/`):

```bash
python3 analyze.py --data-dir ../data --figures-dir ../figures --since-step 2000 --p-representativo 0.1
python3 validacion.py --figures-dir ../figures    # diagrama triangular analítico
```

`since_step` (FIXED) = 2000 pasos, elegido por inspección de la evolución temporal; el incremental usa
ventana completa por fase. Registrado por punto en `figures/manifiesto.csv`.

## 5. Comparación contra el paper (Patterson & Parisi, 2023)

- **Fig. 2** (velocidad vs N por orden): reproducida — decreciente > aleatorio > creciente a densidad
  baja/media, convergencia a saturación (`velocidad_media_incremental_*`).
- **Figs. 3/4** (PDF densidad/velocidad por orden): reproducidas por N activo — pico en 1/44 mm,
  angostamiento con N (`pdf_densidad_incremental_*`, `pdf_velocidad_incremental_*`).
- **Fig. 5D** (FD por orden): reproducida — aleatorio acotado entre creciente y decreciente.
- **Validación variante B**: diagrama triangular `Q(ρ)=min(ρ·vmax,1−ρ)` a precisión de máquina
  (`validacion_triangular.png`) + test JUnit a 1e-9.

**No sobreclaim (documentado en Limitaciones del informe):** el modelo no reproduce la cola de densidad
>1/44 mm (solapamiento/desalineación); N=30 es singular y depende de L=1320 vs ~1313 del paper; la caída
por debajo del más lento requiere p>0 y su mecanismo (frenado del cúmulo rígido) difiere del experimento.

## 6. Verificación final

| Verificación | Resultado |
|--------------|-----------|
| `mvn -f engine/pom.xml clean test` | **55 tests, 0 fallas** (40 previos + 15 nuevos) |
| `pytest analysis/tests` | **29 passed** (13 previos + 16 nuevos) |
| `java -jar …jar --help` | exit 0 |
| Corridas en `data/` | **2700** (1,7 GB) |
| Filas de `figures/manifiesto.csv` | 240 (+ cabecera); `since_step` por fila (2000 FIXED / 0 incremental) |
| Figuras generadas | **37** PNG + `manifiesto.csv` |
| Heroes (fotograma+GIF+MP4) | 5 (N=5, N=30, y 3 órdenes incrementales) |
| Validación triangular | error máx `|Q_sim − Q_teo| = 1,1·10⁻¹⁶` |
| Informe / Presentación | compilan (pdflatex ×2) sin error |

**Chequeo anti-sobreclaim (verificado figura por figura contra el texto):**
- vel-vs-N incremental: descendente > aleatorio > creciente a densidad baja/media; las tres
  convergen a ≈81 mm/s en N=30 (< 90 mm/s, el más lento), a p=0,1. ✔ coincide con el texto.
- FD incremental: el aleatorio queda acotado entre creciente y descendente; caída en 1/44 mm. ✔
- vel-vs-N FIXED: casi plana hasta N=25; en N=30 el colapso depende de p (p=0 → ≈90 = el más
  lento; p≥0,2 → colapso fuerte). ✔ coincide con el texto (colapso requiere p>0).
- Evolución temporal: estacionario alcanzado a ≈20 s; el corte por inspección (since_step=2000
  pasos ≈ 83 s) es conservador. ✔
- PDF de densidad: pico en 1/44 mm que se acentúa con N; sin cola por encima del contacto
  (limitación documentada). ✔

## 7. Bloqueantes externos (solo el humano)

1. **Nombres y legajos** del grupo G01S2 (portada del informe y diapositiva de título). Placeholder
   `[COMPLETAR: nombres y legajos]` en ambos `.tex` (decisión del usuario: completar antes de entregar).
2. **5 links de YouTube** para las animaciones hero (N=5, N=30 y 3 órdenes incrementales). Hoy
   `youtu.be/XXXX`; el usuario sube los GIF/MP4 (generados) y pega los links.

## 8. Reproducir desde cero

```bash
git switch fable/tp-final-auditoria-integral-v1
# Motor
mvn -f engine/pom.xml clean test && mvn -f engine/pom.xml -q -DskipTests package
# Entorno Python
python3 -m venv .venv && . .venv/bin/activate && pip install -r analysis/requirements.txt
# Datos + figuras (ver §4). Luego:
cd informe && pdflatex -interaction=nonstopmode SdS_TPFinal_2026Q1G01S2_Informe.tex  # x2
cd ../presentacion && pdflatex -interaction=nonstopmode SdS_TPFinal_2026Q1G01S2_Presentacion.tex  # x2
```

## 9. Rollback

```bash
git switch main            # la rama fable/ no toca main
git branch -D fable/tp-final-auditoria-integral-v1   # descartar todo (opcional)
```

Los commits son atómicos por intención; se puede revertir cualquiera con `git revert <sha>`.
