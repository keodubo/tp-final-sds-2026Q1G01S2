# Handoff para Keo — TP Final SdS listo para entrega (falta solo lo del grupo)

**Fecha:** 2026-07-07
**Rama:** `fable/tp-final-auditoria-integral-v1` (pusheada)
**De:** Nico (sesión de auditoría/corrección con Claude Code, siguiendo tu handoff del 2026-07-06)

## TL;DR

Corrí el loop completo que dejaste en `2026-07-06_handoff-tp-final-auditoria_v1.md`: **4 rondas de
auditoría (6 lentes: Parisi/motor/estadística/editor/release/jurado) + 2 rondas de correctores por
dominio + una lectura editorial final.** La entrega quedó **sin P0/P1/P2** (la última ronda dio 0) y con
todos los P3 corregidos o aceptados con decisión explícita.

**Verificación (reproducible):** Java **60 tests** · Python **37 pytest** · informe **14 págs** +
presentación **17 págs** compilan (`pdflatex ×2`) · `sha256sum -c SHA256SUMS` OK · sin placeholders/URLs
ficticias · `git diff --check` limpio.

**Vos solo tenés que cerrar 2 cosas del grupo** (abajo) y entregar. Todo el detalle del loop está en la
bitácora `2026-07-06_tp-final-agent-loop-ledger_v1.md` (24 commits chicos por dominio sobre `4fde54b`).

---

## ✅ Lo que se hizo (para que sepas qué cambió)

- **Reproducibilidad (cerraba el P0):** el informe/presentación NO compilaban desde un clon limpio
  (figuras gitignoreadas + nombres desalineados). Ahora hay **`scripts/generar_entrega.sh`** que regenera
  TODO desde cero (motor → 1350 corridas → 19 figuras → 5 fotogramas → ambos PDFs), los **PDFs finales
  están versionados**, y hay **`SHA256SUMS`** de los binarios. `data/`, `figures/`, `data_anim/` siguen
  gitignoreados (regenerables).
- **Física (2 correcciones importantes, verificadas contra `data/`):**
  1. La meseta a baja densidad la gobierna el **agente más lento** (~90-95 mm/s), no la velocidad libre
     media (105). En una pista de un carril sin adelantamiento todo se agrupa detrás del más lento.
  2. El angostamiento/corrimiento de la PDF de velocidad con N es marcado en el orden **decreciente**
     (antes decía "creciente", estaba invertido). El creciente es casi N-independiente.
- **Honestidad:** gridlock a p≥0,3 cuantificado (~0 mm/s); "reproduce las distribuciones" → "la
  tendencia"; pico del modelo 84-90 vs 65 del experimento; N=30 singular; validación triangular solo B.
- **Figuras:** rótulos/leyendas en **español**; diagrama fundamental legible; los **3 fotogramas
  incrementales** ahora se toman en **fase N=10** (antes salían idénticos en N=30 lleno).
- **Motor:** test del invariante "p=0 no consume PRNG" (`RandomBrakeTest`); guard muerto eliminado.
- **Docs/repro:** preflight en el script (falla rápido si falta el entorno), conteos genéricos, unidades
  SI, tiempos/disco coherentes, `.gitignore` de scratch, etc.

---

## ⬅️ Lo que FALTA (solo vos / el grupo puede hacerlo)

### 1. Nombres y legajos en la carátula  ⟵ **lo principal**
Hoy informe y presentación dicen solo **"Grupo G01S2"** (decisión de no inventar datos personales).

- **Informe:** `informe/SdS_TPFinal_2026Q1G01S2_Informe.tex`, línea ~37:
  ```latex
  \author{Grupo G01S2 \\
          72.25 Simulación de Sistemas --- ITBA --- 2026, primer cuatrimestre}
  ```
  Reemplazá por, p. ej.:
  ```latex
  \author{Apellido, Nombre (leg. XXXXX) \and Apellido, Nombre (leg. XXXXX) \\
          Grupo G01S2 --- 72.25 Simulación de Sistemas --- ITBA --- 2026, primer cuatrimestre}
  ```
- **Presentación:** `presentacion/SdS_TPFinal_2026Q1G01S2_Presentacion.tex`, línea ~31:
  ```latex
  \author[Grupo G01S2]{Grupo G01S2}
  ```
  Poné los integrantes (p. ej. `\author[G01S2]{Nombre Apellido \and Nombre Apellido}`).
- Después: `cd informe && pdflatex ...Informe.tex` (×2) e ídem presentación, y **recalculá los checksums**
  (o corré `scripts/generar_entrega.sh`, que ya recalcula `SHA256SUMS` al final).
- ⚠️ Si la cátedra acepta entrega anonimizada, no toques nada.

### 2. Links de las animaciones
Los captions son honestos hoy: *"Se muestra un fotograma representativo; la animación completa se regenera
con `scripts/generar_entrega.sh`."* (informe Figs. 1 y 6; presentación diapo de dinámica).

- Si suben las animaciones (los GIF/MP4 salen en `data_anim/` al correr el script), reemplazá esa frase
  por el link real (YouTube no listado, o el que use la cátedra). Sin link, dejá la frase como está
  (no rompe nada y no promete lo que no hay).

### 3. Pulidos P3 OPCIONALES (no bloquean la aprobación — decidilos vos)
- **Separador decimal:** la prosa usa coma (0,1) y las figuras de matplotlib usan punto (0.1). Un jurado
  quisquilloso lo marca. Arreglarlo exige configurar locale + regenerar las 19 figuras. Lo dejé aceptado.
- **Media página en blanco (pág. 8 del informe):** efecto de `[H]` (la Fig. 6 no entra y flota). Tocar
  los floats arriesga reintroducir "figuras después de Referencias" (bug ya cerrado). Bajo impacto.

---

## 🔁 Cómo verificar / regenerar (todo reproducible)

```bash
git switch fable/tp-final-auditoria-integral-v1

# Motor (necesita JDK 21; en la máquina de Nico está en ~/.local/java/jdk-21.0.5+11)
mvn -f engine/pom.xml test                       # 60 tests

# Análisis (venv)
python3 -m venv analysis/.venv && source analysis/.venv/bin/activate
pip install -r analysis/requirements.txt
python3 -m pytest analysis/tests -q              # 37 passed

# Regenerar la entrega COMPLETA desde cero (datos+figuras+PDFs, ~8-12 min, ~0,85 GB)
scripts/generar_entrega.sh

# Verificar integridad de los binarios versionados
sha256sum -c SHA256SUMS
```

Si NO querés regenerar: los **PDFs finales ya están versionados** (`informe/*.pdf`, `presentacion/*.pdf`),
se abren sin compilar nada. Solo recompilá si tocás los `.tex` (p. ej. para agregar los nombres).

---

## 📌 Estado del repo

- 24 commits sobre `4fde54b`, atómicos por dominio (analysis / engine / entregables / repro / docs).
- Bitácora completa del loop: `2026-07-06_tp-final-agent-loop-ledger_v1.md`.
- Nada roto: `mvn test`, `pytest`, ambos `pdflatex` y `sha256sum -c` en verde.
- **Próximo paso sugerido:** agregás nombres/legajos (y links si publican), recompilás, y hacés el merge a
  `main` (o entregás los PDFs directamente). Si preferís, se puede abrir un PR de esta rama a `main`.
