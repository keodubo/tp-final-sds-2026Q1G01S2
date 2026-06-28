package ar.edu.itba.sds.sim.collision;

import java.util.List;

/**
 * Variante A — «contacto puro» (primaria; es la que modela el mecanismo del experimento).
 *
 * <p>Sin anticipación: un vehículo mantiene su velocidad mientras no alcance al de adelante.
 * <ul>
 *   <li>si {@code v ≤ gapAhead} → avanza libre (no se toca la velocidad);</li>
 *   <li>si {@code v > gapAhead} → colisión: toma la velocidad del líder ({@code v ← v_lider}) y queda
 *       a contacto. El cierre a contacto exige resolver desplazamientos finales compatibles con
 *       el líder, no una mutación parcial de la velocidad del seguidor.</li>
 * </ul>
 * Los vehículos en contacto forman agrupamientos que se mueven a la velocidad del que va al frente;
 * en una ruta totalmente llena, todos a la mínima. La resolución de agrupamientos (orden de recorrido de la
 * ruta, manejo del caso totalmente trabado y compatibilidad con R3) se fija con TDD después de
 * confirmar la semántica con el profesor.
 *
 * <p>TODO (Hito 4 — TDD): implementar. Tests de invariantes: sin solapamiento, N conservado,
 * orden periódico preservado, y reproducción del «la velocidad de saturación es menor que la del más
 * lento» del artículo.
 */
public final class ContactoPuro implements CollisionRule {
    @Override
    public List<Integer> resolve(CollisionContext context) {
        throw new UnsupportedOperationException("TODO Hito 4: implementar Regla 2 de contacto puro con TDD");
    }
}
