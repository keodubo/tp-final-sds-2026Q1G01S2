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
