package ar.edu.itba.sds.sim;

import java.util.random.RandomGenerator;

/**
 * Regla 3 (frenado aleatorio). Encapsula la fuente de aleatoriedad para que la corrida sea
 * reproducible dado el identificador técnico de la realización.
 */
public final class RandomBrake {

    private final RandomGenerator rng;

    public RandomBrake(RandomGenerator rng) {
        this.rng = rng;
    }

    /**
     * ¿Frena este vehículo en este paso? Verdadero con probabilidad {@code p}.
     *
     * <p>El motor decide <b>cuándo</b> invocarlo (p. ej. solo si {@code v>0}); esa convención —y por lo
     * tanto en qué momento se consume un número del PRNG— se fija en el TDD del Hito 2, porque afecta la
     * reproducibilidad bit-a-bit de la realización.
     */
    public boolean brakes(double p) {
        return p > 0 && rng.nextDouble() < p;
    }
}
