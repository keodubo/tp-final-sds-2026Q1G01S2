package ar.edu.itba.sds.sim;

import java.util.random.RandomGenerator;

/**
 * Regla 3 (frenado aleatorio). Encapsula la fuente de aleatoriedad para que la corrida sea
 * reproducible dada la semilla (una realización).
 */
public final class RandomBrake {

    private final RandomGenerator rng;

    public RandomBrake(RandomGenerator rng) {
        this.rng = rng;
    }

    /** ¿Frena este vehículo en este paso? Verdadero con probabilidad {@code p}. */
    public boolean brakes(double p) {
        return p > 0 && rng.nextDouble() < p;
    }
}
