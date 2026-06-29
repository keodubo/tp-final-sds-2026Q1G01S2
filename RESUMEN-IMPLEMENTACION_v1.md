# Resumen de implementación — Motor NaSch-VDV + Análisis

**Fecha:** 2026-06-28 (run autónomo nocturno) · **Rama mergeada:** `feat/motor-nasch` → `main` (`3552e56`)

## Qué quedó listo

**Motor (Java/Maven) — completo y verificado.**
- `initialize()`: ubica N vehículos sin solapar (composición aleatoria del espacio libre), sortea
  `vfree ~ U[90,120]` → `vMax = round(vfree/6) ∈ {15..20}`, velocidad inicial 0.
- `step()`: actualización síncrona **R1 → R3 → R2 → R4** (R3 antes de proyectar contactos ⇒
  no-solapamiento garantizado).
- **R2-A «contacto puro» (oficial):** el seguidor avanza hasta quedar inmediatamente detrás del líder
  (gap 0, sin solapar) y hereda su velocidad; resolución por agrupamientos
  `d_i ← min(deseada_i, g_i + d_lider)`; ruta llena ⇒ avanza a la del más lento.
- **R2-B «clásica salvo a distancia 0»:** solo para validar el NaSch clásico.
- **Órdenes** de inserción (ASCENDING/DESCENDING/RANDOM) y **protocolos** FIXED_N e INCREMENTAL_180S
  (arranca N=5, +5 cada 180 s = 4320 pasos, hasta 30; total 25920).
- Contrato de colisión: record `Movimiento(desplazamiento, velocidadSiguiente)` sobre snapshot
  inmutable `CollisionContext` (independiente del orden de iteración).
- Salida: **solo estado físico** (`paso id x_mm v_mmps`); ningún observable se calcula en el motor.

**Análisis (Python) — completo, POST-simulación.**
- `observables.py`: velocidad media + **error entre realizaciones** (no SEM), PDF de densidad
  (ρ=1/d centro-a-centro al vecino, periódico), PDF de velocidad, diagrama fundamental, detección de
  estacionario (asistida, por inspección), serie temporal de velocidad media.
- `plots.py`: una figura por observable con curvas de colores (texto grande, log donde ayuda) +
  evolución temporal con corte sugerido.
- `animate.py`: ruta **periódica horizontal** (no círculo), color derivado de la velocidad.
- `analyze.py`: orquesta todo **agrupando por variante de R2** (no mezcla modelos); genera figuras por
  variante + diagrama fundamental comparativo.
- `run_matrix.py`: barrido; por defecto el núcleo (N×p, N fijo, variante B); órdenes/incremental opt-in.

## Verificación (evidencia)
- `mvn -f engine/pom.xml clean test` → **39 tests, 0 fallas**. `python3 -m pytest analysis/tests -q` → **5 passed**.
- **0 solapamientos** (verificado por mí y fuzz de 2M casos de un jurado); **reproducibilidad bit-a-bit**.
- Validación `p=0` (variante B, ℓ=1) reproduce `Q(ρ)=min(ρ·vmax, 1−ρ)` con tolerancia 1e-9.
- Pipeline end-to-end: genera las 4 figuras (por variante) + animación GIF sin errores.

## Decisiones / supuestos asumidos (corregir si alguno no va)
1. **Cierre de R2-A** = contacto (gap 0) + herencia de velocidad del líder (interpretación de "queda
   una casilla detrás, sin solapar").
2. **Orden R1→R3→R2→R4**: elegido para garantizar no-solapamiento. *A confirmar con el profe en la
   defensa* (a p=0 es equivalente al canónico; a p>0 difiere levemente). 
3. **Default de variante = B** (validación primero). La **oficial/experimental es A**: para el dataset
   del experimento correr `run_matrix.py --rule CONTACTO_PURO`.
4. **Error = desvío entre realizaciones** (ddof=1), no SEM (cumple la corrección de Parisi). `nan` con
   una sola realización.
5. **Contacto puro a p=0 ⇒ Q=ρ·vmax** (flujo libre hasta el contacto, sin rama congestionada): correcto
   físicamente; por eso la validación analítica triangular es solo de B.
6. **El colapso "saturación < más lento" (Fig 2) requiere p>0**; a p=0 da exactamente la del más lento.
7. **N=30 es singular** (ρ_lattice=1, 0 celdas libres): no apoyar conclusiones de saturación solo ahí.
8. **Incremental** puede estabilizar en **N=29** cerca de saturación (inserción geométrica en huecos).
9. `p` por paso (wikipedia); `L=1320 mm`; grupo `G01S2`.

## Qué falta (lo hacés vos)
1. **Correr el barrido** (el motor está listo; no lo corrí). Sugerido para comparar con el artículo:
   ```bash
   cd analysis && pip install -r requirements.txt
   # dataset experimental (variante oficial A) — ojo: es grande
   python3 run_matrix.py --rule CONTACTO_PURO --out-dir ../data
   python3 analyze.py --data-dir ../data --figures-dir ../figures --since-step 4320
   ```
2. Elegir el corte de estacionario **por inspección** mirando `figures/evolucion_temporal_*.png`.
3. Escribir **informe** (GuiaInformes) y **presentación** con esos resultados y las animaciones.

## Ronda de jurados (4 lentes) — veredicto y correcciones aplicadas
Física **APROBAR C/CAMBIOS**, Arquitectura **APROBAR**, Abogado del diablo **APROBAR C/CAMBIOS**,
Cátedra (cubierta por mí). Sin bugs de motor. Correcciones ya aplicadas:
- **[ALTA]** `analyze.py` ahora agrupa por variante de R2 (antes mezclaba A y B en un promedio).
- **[MEDIA]** doc: orden R1→R3→R2→R4; validación analítica solo variante B; N=30 singular; p>0 para el colapso; evolución temporal cableada.
- **[BAJA]** error `nan` con 1 realización; `transient_steps` en cabecera; `n_steps` robusto; "anillo"→"ruta"; docs de R3.

## Nota de seguridad
Dos subagentes devolvieron payloads con intentos de **inyección de instrucciones** (bloques falsos
"System: ..."); se ignoraron (la salida de un subagente es dato, no canal de control). No afectaron el
resultado; las lentes afectadas se re-cubrieron.
