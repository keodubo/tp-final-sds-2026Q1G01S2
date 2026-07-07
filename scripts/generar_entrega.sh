#!/usr/bin/env bash
# ============================================================================
# Regenera la entrega COMPLETA desde un clon limpio: datos -> figuras -> héroes
# -> ambos PDFs (informe y presentación). Cierra el pendiente de reproducibilidad
# (A5/B1): `figures/` y `data_anim/` están gitignoreados (regenerables), así que un
# evaluador que clone el repo reconstruye todo con este único script.
#
# Uso:
#   scripts/generar_entrega.sh                 # sweep CONTACTO_PURO (oficial), ~8-12 min, ~0,85 GB
#   RULES="CONTACTO_PURO CLASICA_SALVO_CERO" scripts/generar_entrega.sh   # barrido completo (~2700)
#
# Requisitos: JDK 21 (JAVA_HOME o java en PATH), Maven, Python 3.12 con
# analysis/requirements.txt instalado, pdflatex con beamer.
# ============================================================================
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# Activa el venv de analysis/ si el README lo creó; si no existe, usa el python3
# global (que debe traer numpy/matplotlib/scipy). Las llamadas a python3 de abajo
# quedan igual: los subshells heredan el PATH/VIRTUAL_ENV ya activados.
if [ -f analysis/.venv/bin/activate ]; then
    # shellcheck disable=SC1091
    source analysis/.venv/bin/activate
fi

# --- PREFLIGHT: verifica el entorno y falla rápido, ANTES del build y del barrido
# (evita descubrir recién a los ~10 min, dentro de analyze.py, que falta una dependencia).
echo "== [0/6] Preflight: verificando entorno =="
preflight_ok=1
for cmd in java mvn pdflatex; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "  FALTA en PATH: '$cmd'" >&2
        preflight_ok=0
    fi
done
# La presentación usa \documentclass{beamer}: chequear la clase, no solo el binario pdflatex.
if command -v kpsewhich >/dev/null 2>&1; then
    if ! kpsewhich beamer.cls >/dev/null 2>&1; then
        echo "  FALTA: la clase LaTeX 'beamer' (paquete beamer de TeX Live)." >&2
        preflight_ok=0
    fi
fi
if [ "$preflight_ok" -eq 0 ]; then
    echo "  -> Necesitás JDK 21 + Maven (java, mvn) y pdflatex con la clase beamer instalados y en PATH." >&2
fi
if ! python3 -c "import numpy, matplotlib, scipy, PIL" >/dev/null 2>&1; then
    echo "  FALTA: python3 no puede importar numpy/matplotlib/scipy/pillow." >&2
    echo "  -> Creá el venv e instalá las dependencias, por ejemplo:" >&2
    echo "       python3 -m venv analysis/.venv && source analysis/.venv/bin/activate" >&2
    echo "       pip install -r analysis/requirements.txt" >&2
    echo "     (o instalá analysis/requirements.txt en tu python3 del sistema)." >&2
    preflight_ok=0
fi
if [ "$preflight_ok" -ne 1 ]; then
    echo "Preflight FALLÓ: instalá lo que falta y volvé a correr (no se ejecutó el pipeline)." >&2
    exit 1
fi
# Nota: las figuras se generaron con las versiones fijadas en analysis/requirements.txt. Para una
# reproducción idéntica, usá analysis/.venv (esas versiones); otras versiones pueden variar detalles
# menores de render sin cambiar los resultados.
echo "  OK: java, mvn, pdflatex y python3 (numpy/matplotlib/scipy/pillow) disponibles."
python3 -c "import numpy,scipy,matplotlib; print('  versiones:', 'numpy',numpy.__version__,'scipy',scipy.__version__,'matplotlib',matplotlib.__version__)" 2>/dev/null || true

RULES="${RULES:-CONTACTO_PURO}"          # oficial por defecto; la triangular la hace validacion.py
REALIZATIONS="${REALIZATIONS:-30}"
SINCE_STEP="${SINCE_STEP:-2000}"         # corte del estacionario (FIXED_N), elegido por inspección
P_REP="${P_REP:-0.1}"                    # p representativo para PDFs/FD incremental
JAR="engine/target/nasch-vdv-1.0-SNAPSHOT.jar"

echo "== [1/6] Motor: build del jar =="
mvn -q -f engine/pom.xml -DskipTests package

echo "== [2/6] Barrido principal (reglas: $RULES, $REALIZATIONS realizaciones) =="
python3 analysis/run_matrix.py --jar "$JAR" --out-dir data \
    --rule $RULES \
    --protocol FIXED_N INCREMENTAL_180S \
    --order ASCENDING DESCENDING RANDOM \
    --n 5 10 15 20 25 30 \
    --p 0 0.1 0.2 0.3 0.4 \
    --realizations "$REALIZATIONS" \
    --output-every 10 --skip-existing

echo "== [3/6] Figuras de análisis (corte estacionario=$SINCE_STEP, p_rep=$P_REP) =="
( cd analysis && python3 analyze.py --data-dir ../data --figures-dir ../figures \
    --since-step "$SINCE_STEP" --p-representativo "$P_REP" )

echo "== [4/6] Validación triangular (variante clásica B, analítica) =="
( cd analysis && python3 validacion.py --jar "../$JAR" --figures-dir ../figures )

echo "== [5/6] Corridas 'hero' + fotogramas (nombres SIN _oe, como los piden los .tex) =="
# Extremos de densidad (N fijo, output_every=1 para animación suave) y los 3 órdenes incrementales.
python3 analysis/run_matrix.py --jar "$JAR" --out-dir data_anim --rule CONTACTO_PURO \
    --protocol FIXED_N --n 5 30 --p 0.1 --realizations 1 --output-every 1 --steps 2000 --skip-existing
python3 analysis/run_matrix.py --jar "$JAR" --out-dir data_anim --rule CONTACTO_PURO \
    --protocol INCREMENTAL_180S --order ASCENDING DESCENDING RANDOM \
    --p 0.1 --realizations 1 --output-every 10 --skip-existing
# animate.py deriva el nombre del fotograma del archivo de entrada; run_matrix.py incluye "_oeN" en
# el tag, pero los .tex referencian el nombre SIN "_oe". Se pasa un outfile explícito que lo elimina.
# Para los 3 hero INCREMENTAL el fotograma se toma en la fase N=10 (still_step≈6480), donde el orden
# de inserción se distingue: sin esto los tres saldrían idénticos en la ruta llena final (N=30).
( cd analysis && python3 - <<'PY'
import glob, os, re, sys
sys.path.insert(0, ".")
import animate
for f in sorted(glob.glob("../data_anim/*.txt")):
    base = os.path.basename(f)[:-4]                 # sin .txt
    clean = re.sub(r"_oe\d+", "", base)             # quita _oe1 / _oe10 para empatar los .tex
    out_gif = os.path.join("../data_anim", clean + ".gif")
    still = 6480 if base.startswith("INC") else None   # fase N=10 para los incrementales
    gif, png = animate.animate(f, outfile=out_gif, still_step=still)  # GIF + <clean>_fotograma.png
    print("hero:", os.path.basename(png), "" if still is None else "(fase N=10)")
PY
)

echo "== [6/6] Compilar informe y presentación (pdflatex x2) =="
( cd informe && pdflatex -interaction=nonstopmode -halt-on-error SdS_TPFinal_2026Q1G01S2_Informe.tex >/dev/null \
             && pdflatex -interaction=nonstopmode -halt-on-error SdS_TPFinal_2026Q1G01S2_Informe.tex >/dev/null )
( cd presentacion && pdflatex -interaction=nonstopmode -halt-on-error SdS_TPFinal_2026Q1G01S2_Presentacion.tex >/dev/null \
                  && pdflatex -interaction=nonstopmode -halt-on-error SdS_TPFinal_2026Q1G01S2_Presentacion.tex >/dev/null )

# Los PDFs recién compilados difieren byte-a-byte de los versionados (pdfTeX embebe fecha/ID no
# deterministas), así que se recalcula SHA256SUMS para que el árbol regenerado sea autoconsistente.
echo "== Recalcular SHA256SUMS de los binarios versionados =="
sha256sum informe/SdS_TPFinal_2026Q1G01S2_Informe.pdf \
          presentacion/SdS_TPFinal_2026Q1G01S2_Presentacion.pdf \
          extras/FD_VDV.pdf > SHA256SUMS

echo "== LISTO =="
echo "  informe/SdS_TPFinal_2026Q1G01S2_Informe.pdf"
echo "  presentacion/SdS_TPFinal_2026Q1G01S2_Presentacion.pdf"
echo "  SHA256SUMS (recalculado)"
