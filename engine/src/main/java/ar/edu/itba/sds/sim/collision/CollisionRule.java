package ar.edu.itba.sds.sim.collision;

import ar.edu.itba.sds.model.PeriodicTrack;

/**
 * Regla 2 (resolución de colisión). Se aplica sobre las velocidades <b>ya aceleradas por R1</b>
 * y antes del frenado aleatorio (R3) y el movimiento (R4). Modifica las velocidades de los
 * vehículos de la ruta para impedir solapamientos; <b>no</b> los mueve.
 */
public interface CollisionRule {
    void apply(PeriodicTrack track);
}
