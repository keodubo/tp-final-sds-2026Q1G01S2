# CLAUDE.md — TP Final SdS (Nagel-Schreckenberg + VDV)

Instrucciones para trabajar en este repo. **Leé primero el documento de diseño**
`diseno-tp-final-vdv-nasch_v1.md` y el artículo `extras/FD_VDV.pdf`.

## Qué es esto

Autómata celular de **Nagel-Schreckenberg** (R2 modificada por contacto) en una **ruta periódica 1D**
(la pista circular del experimento se modela como una línea periódica: lo que sale por un extremo
reentra por el otro; la curvatura no entra en el modelo), calibrado para reproducir el experimento de
*vibration-driven vehicles* (Hexbug) de Patterson & Parisi, y comparar observables. Materia 72.25
(ITBA, Prof. Daniel Parisi). Grupo G01S2.

## Stack y comandos

- **Motor:** Java 21 + Maven, en `engine/`. `cd engine && mvn clean package`. Jar ejecutable.
- **Análisis/animación:** Python 3.12 en `analysis/` (`numpy`, `matplotlib`, `scipy`).
- **Tests:** JUnit 5 (`mvn test`). TDD para toda lógica del modelo (ver `superpowers:test-driven-development`).

## El modelo (referencia rápida)

Ruta periódica de `L` celdas; vehículos extendidos de `ℓ` celdas; velocidad entera `v∈{0..vmax_i}`
(celdas/paso). Paso síncrono, en orden **R1 → R3 → R2 → R4** (R3 antes de proyectar contactos ⇒
no-solapamiento garantizado):

- **R1 Aceleración:** `v ← min(v+1, vmax_i)`.
- **R3 Frenado aleatorio:** con prob `p`, `v ← max(0, v-1)`. `p=0` ⇒ determinista (no consume PRNG).
- **R2 Colisión (modificada):** dos variantes (`CollisionRule`); **oficial = contacto puro**:
  - *Contacto puro* (A, oficial): si no alcanza al líder avanza libre; si lo alcanzaría queda
    inmediatamente detrás (gap 0, sin solapar) y **hereda la velocidad del líder**. Resuelto por
    agrupamientos (desplazamientos finales `d_i ← min(deseada, g_i+d_lider)`).
  - *Clásica salvo a distancia 0* (B, solo validación): `v ← min(v, gap)`, si `gap=0` → `min(v, d_lider)`.
- **R4 Movimiento:** `x ← (x+v) mod L`.

El contrato de `CollisionRule.resolve` usa snapshots (`CollisionContext`) y devuelve un
`Movimiento(desplazamiento, velocidadSiguiente)`; no muta la ruta. **Validación analítica `Q(ρ)=min(ρ·vmax,1−ρ)`
solo aplica a la variante B**; la A (contacto puro) no se valida contra esa curva. En el caso
homogéneo `p=0`, A mantiene flujo libre hasta el contacto.

Cada vehículo tiene su `vmax_i` (heterogéneo) derivado de una velocidad libre `~U[90,120] mm/s`.

## Calibración (constantes)

`Δx=0.25 mm`, `dt=1/24 s`, `Δv=Δx/dt=6 mm/s`, `ℓ=176 celdas (44 mm)`, `L=5280 celdas (=30·ℓ)`,
`vmax_i = round(vfree_i/6) ∈ {15..20}`, `ρ = N/L_phys` (hasta 0.0227 1/mm a N=30).

## Reglas de la cátedra (NO violar — son correcciones repetidas de Parisi)

1. **Observables siempre post-simulación**, desde los archivos de salida. NUNCA dentro del motor.
2. El motor escribe **solo variables físicas** (`id, x[mm], v[mm/s]`). Sin color ni radio. El color
   (para animaciones) se deriva de la velocidad **después**.
3. Sección *Implementación* del informe = del modelo matemático al cómputo. No tipos de archivo ni
   post-proceso ni condiciones iniciales.
4. *Resultados* por parámetro: animación → evolución temporal → **curva respuesta-estímulo**.
   Conclusiones solo al final; no concluir mientras se muestran animaciones.
5. **Estacionario** se detecta por inspección (no descarte fijo en %). Estacionario ≠ sincronizado.
6. Decir **"realizaciones"**, no "seeds". Distinguir **parámetros** de **condiciones iniciales**.
7. Cifras significativas acordes al error; **desvío bien calculado** (no promedio-de-promedios).
8. Figuras: **una sola** con curvas de colores para comparar; texto de la figura del mismo tamaño
   que el resto; escala log donde ayude.
9. **Español**, sin anglicismos. Nombrar el método (autómata celular / dirigido por paso temporal),
   no "el TP X".

## Convenciones del repo

- Entregables: `SdS_TPFinal_2026Q1G01S2_Informe.pdf`, `SdS_TPFinal_2026Q1G01S2_Presentación.pdf`.
- Documentos de trabajo: `YYYY-MM-DD_tema_vN.md`.
- Una **realización** = condiciones iniciales concretas + velocidades libres concretas + secuencia
  reproducible del PRNG. En CLI puede seguir existiendo `--seed` como identificador técnico.
- `data/` y `figures/` generados van fuera de git (ver `.gitignore`).

## Temas a documentar en la defensa

No reabrir las decisiones ya confirmadas (R2 oficial A, orden R1→R3→R2→R4, órdenes+incremental en
alcance, `p` por paso, `L=1320`, error entre realizaciones, observables post-simulación). Sí documentar:
contrato temporal exacto de salida en la frontera incremental, sensibilidad de `dt`, `L` y `Δx`, y
nivel de coincidencia cuantitativa que den los barridos reales.
