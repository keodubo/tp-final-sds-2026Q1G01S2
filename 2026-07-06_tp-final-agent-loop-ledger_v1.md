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
(pendiente — fase obligatoria de 6 auditores tras cerrar baseline y generar entregables)

## Criterios de cierre (del handoff)
- Sin P0/P1 abiertos; P2/P3 con decisión explícita.
- Java y pytest verdes.
- Informe y presentación compilan (o PDFs finales versionados y justificados).
- Sin placeholders, URLs ficticias ni vocabulario prohibido.
- Resultados no sobreprometen respecto del paper/modelo.
