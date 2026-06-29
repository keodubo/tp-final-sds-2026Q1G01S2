package ar.edu.itba.sds.sim.collision;

import ar.edu.itba.sds.model.PeriodicTrack;

import java.util.ArrayList;
import java.util.List;

/**
 * Snapshot inmutable para resolver la Regla 2 sin depender del orden de iteración ni de mutaciones
 * parciales sobre la ruta. El motor lo construye luego de aplicar R1 (aceleración) y R3 (frenado
 * aleatorio) sobre las velocidades, y recién después aplica el resultado de
 * {@link CollisionRule#resolve(CollisionContext)}.
 *
 * <p>{@code desiredVelocities} es la <b>velocidad deseada</b> de cada vehículo: cuánto querría avanzar
 * este paso (post-R1 y post-R3). La regla la usa como tope y la proyecta contra los huecos para que
 * nunca haya solapamiento. Trabajar contra este snapshot deja la actualización síncrona: el resultado
 * no depende de en qué orden el motor recorra los vehículos.
 *
 * <p>Las listas se indexan por la posición periódica del vehículo (índice {@code i+1} = líder de
 * {@code i}, con envoltura), igual que {@link PeriodicTrack}.
 */
public record CollisionContext(
        int latticeLength,
        int vehicleLength,
        List<Integer> gapsAhead,
        List<Integer> desiredVelocities
) {

    public CollisionContext {
        if (latticeLength <= 0) throw new IllegalArgumentException("latticeLength debe ser > 0");
        if (vehicleLength <= 0) throw new IllegalArgumentException("vehicleLength debe ser > 0");
        gapsAhead = List.copyOf(gapsAhead);
        desiredVelocities = List.copyOf(desiredVelocities);
        int n = gapsAhead.size();
        if (n == 0) throw new IllegalArgumentException("debe haber al menos un vehículo");
        if (desiredVelocities.size() != n) {
            throw new IllegalArgumentException("todos los snapshots deben tener tamaño N");
        }
    }

    /**
     * Arma el contexto a partir de la geometría actual de la ruta (huecos) y de las velocidades
     * deseadas ya calculadas por el motor (post-R1 y post-R3).
     */
    public static CollisionContext from(PeriodicTrack track, List<Integer> desiredVelocities) {
        List<Integer> gaps = new ArrayList<>(track.size());
        for (int i = 0; i < track.size(); i++) {
            gaps.add(track.gapAhead(i));
        }
        return new CollisionContext(
                track.latticeLength(),
                track.vehicleLength(),
                gaps,
                desiredVelocities
        );
    }

    public int size() {
        return gapsAhead.size();
    }
}
