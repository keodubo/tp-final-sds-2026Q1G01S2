package ar.edu.itba.sds.sim.collision;

import java.util.List;

/**
 * Variante B — «clásica salvo a distancia 0».
 *
 * <p>Para cada vehículo: {@code v ← min(v, gapAhead)} (R2 clásica anticipatoria), salvo cuando ya
 * está a contacto ({@code gapAhead == 0}), en cuyo caso toma la velocidad del líder
 * ({@code v ← v_lider}) en vez de quedar en 0. El {@code min(v, gap)} garantiza por sí solo que no
 * haya solapamiento.
 *
 * <p>TODO (Hito 2 — TDD): implementar. Tests de invariantes: sin solapamiento, N conservado,
 * y con la configuración homogénea + p=0 el diagrama fundamental debe dar el resultado analítico.
 */
public final class ClasicaSalvoCero implements CollisionRule {
    @Override
    public List<Movimiento> resolve(CollisionContext context) {
        throw new UnsupportedOperationException("TODO Hito 2: implementar Regla 2 clásica-salvo-0 con TDD");
    }
}
