package ar.edu.itba.sds.sim.collision;

import ar.edu.itba.sds.model.PeriodicTrack;

import java.util.ArrayList;
import java.util.List;

/**
 * Snapshot inmutable para resolver la Regla 2 sin depender del orden de iteración ni de mutaciones
 * parciales sobre la ruta. La implementación del motor debe construirlo luego de R1 y aplicar el
 * resultado de {@link CollisionRule#resolve(CollisionContext)} recién al terminar el cálculo de R2.
 *
 * <p>{@code leaderVelocitiesForR2} es un campo <b>provisorio</b> que deja explícita una decisión
 * pendiente con el profesor: la velocidad del líder usada por R2 puede venir pre-R1, post-R1 o post-R3.
 * A propósito <b>no</b> se valida su coherencia con la velocidad real del líder (eso depende de la
 * convención aún no confirmada); cuando se fije la semántica, este campo se deriva de
 * {@code velocitiesAfterR1} o se reemplaza, y el contrato deja de necesitarlo.
 */
public record CollisionContext(
        int latticeLength,
        int vehicleLength,
        List<Integer> gapsAhead,
        List<Integer> velocitiesAfterR1,
        List<Integer> leaderVelocitiesForR2
) {

    public CollisionContext {
        if (latticeLength <= 0) throw new IllegalArgumentException("latticeLength debe ser > 0");
        if (vehicleLength <= 0) throw new IllegalArgumentException("vehicleLength debe ser > 0");
        gapsAhead = List.copyOf(gapsAhead);
        velocitiesAfterR1 = List.copyOf(velocitiesAfterR1);
        leaderVelocitiesForR2 = List.copyOf(leaderVelocitiesForR2);
        int n = gapsAhead.size();
        if (n == 0) throw new IllegalArgumentException("debe haber al menos un vehículo");
        if (velocitiesAfterR1.size() != n || leaderVelocitiesForR2.size() != n) {
            throw new IllegalArgumentException("todos los snapshots deben tener tamaño N");
        }
    }

    public static CollisionContext from(
            PeriodicTrack track,
            List<Integer> velocitiesAfterR1,
            List<Integer> leaderVelocitiesForR2
    ) {
        List<Integer> gaps = new ArrayList<>(track.size());
        for (int i = 0; i < track.size(); i++) {
            gaps.add(track.gapAhead(i));
        }
        return new CollisionContext(
                track.latticeLength(),
                track.vehicleLength(),
                gaps,
                velocitiesAfterR1,
                leaderVelocitiesForR2
        );
    }

    public int size() {
        return gapsAhead.size();
    }
}
