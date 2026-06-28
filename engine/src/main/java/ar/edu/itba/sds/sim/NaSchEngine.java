package ar.edu.itba.sds.sim;

import ar.edu.itba.sds.config.Config;
import ar.edu.itba.sds.model.PeriodicTrack;
import ar.edu.itba.sds.sim.collision.ClasicaSalvoCero;
import ar.edu.itba.sds.sim.collision.CollisionRule;
import ar.edu.itba.sds.sim.collision.ContactoPuro;

import java.util.Random;

/**
 * Motor de Nagel-Schreckenberg con la Regla 2 modificada. Actualización síncrona por paso de
 * tiempo, en orden <b>R1 → R2 → R3 → R4</b>. Es 100 % determinista dada la semilla de la
 * configuración (condiciones iniciales + secuencia del PRNG).
 */
public final class NaSchEngine {

    private final Config config;
    private final Random rng;
    private final CollisionRule collisionRule;
    private final RandomBrake brake;
    private PeriodicTrack track;

    public NaSchEngine(Config config) {
        this.config = config;
        this.rng = new Random(config.seed());
        this.collisionRule = ruleFor(config);
        this.brake = new RandomBrake(rng);
    }

    private static CollisionRule ruleFor(Config config) {
        return switch (config.collisionRule()) {
            case CONTACTO_PURO -> new ContactoPuro();
            case CLASICA_SALVO_CERO -> new ClasicaSalvoCero();
        };
    }

    /** Estado actual de la ruta (null antes de {@link #initialize()}). */
    public PeriodicTrack track() {
        return track;
    }

    public Config config() {
        return config;
    }

    /**
     * Construye el estado inicial: ubica {@code N} vehículos sin solapar en la ruta (posiciones
     * iniciales a partir del PRNG), sortea la velocidad libre de cada uno en
     * {@code [freeSpeedMin, freeSpeedMax]} y la mapea a {@code vMax_i = round(vfree_i / Δv)}.
     *
     * <p>TODO (Hito 2 — TDD). Test de invariantes: ruta consistente (sin solapamiento), N
     * vehículos, cada {@code vMax_i} en el rango esperado.
     */
    public void initialize() {
        throw new UnsupportedOperationException("TODO Hito 2: implementar la condición inicial con TDD");
    }

    /**
     * Avanza un paso de tiempo (actualización síncrona):
     * <ol>
     *   <li><b>R1</b> acelerar: {@code v ← min(v+1, vMax)} para todos;</li>
     *   <li><b>R2</b> resolver colisiones según {@link CollisionRule} (sobre la configuración inicial del paso);</li>
     *   <li><b>R3</b> frenar con probabilidad {@code p}: si {@code brake.brakes(p)} y {@code v>0}, {@code v ← v-1};</li>
     *   <li><b>R4</b> mover: {@code x ← (x + v) mod L}, manteniendo el orden periódico.</li>
     * </ol>
     *
     * <p>TODO (Hito 2 — TDD). Tests: N conservado, ruta consistente tras el paso, y con
     * configuración homogénea + p=0 la corrida es bit-a-bit reproducible y el diagrama fundamental
     * coincide con el resultado analítico.
     */
    public void step() {
        throw new UnsupportedOperationException("TODO Hito 2: implementar el paso síncrono R1–R4 con TDD");
    }
}
