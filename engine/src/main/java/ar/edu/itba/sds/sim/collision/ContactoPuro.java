package ar.edu.itba.sds.sim.collision;

import ar.edu.itba.sds.model.PeriodicTrack;

/**
 * Variante A — «contacto puro» (primaria; es la que modela el mecanismo del experimento).
 *
 * <p>Sin anticipación: un vehículo mantiene su velocidad mientras no alcance al de adelante.
 * <ul>
 *   <li>si {@code v ≤ gapAhead} → avanza libre (no se toca la velocidad);</li>
 *   <li>si {@code v > gapAhead} → colisión: toma la velocidad del líder ({@code v ← v_lider}) y queda
 *       a contacto. El cierre a contacto se resuelve de forma consistente con el movimiento (R4).</li>
 * </ul>
 * Los vehículos en contacto forman clusters que se mueven a la velocidad del que va al frente; en una
 * ruta totalmente llena, todos a la mínima. La resolución de clusters (orden de recorrido de la
 * ruta, manejo del caso totalmente trabado) se fija con TDD.
 *
 * <p>TODO (Hito 4 — TDD): implementar. Tests de invariantes: sin solapamiento, N conservado,
 * orden periódico preservado, y reproducción del «la velocidad de saturación es menor que la del más
 * lento» del paper.
 */
public final class ContactoPuro implements CollisionRule {
    @Override
    public void apply(PeriodicTrack track) {
        throw new UnsupportedOperationException("TODO Hito 4: implementar Regla 2 de contacto puro con TDD");
    }
}
