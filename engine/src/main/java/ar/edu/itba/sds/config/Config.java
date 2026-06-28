package ar.edu.itba.sds.config;

/**
 * Parámetros de una corrida del modelo. Todas las cantidades del lattice están en celdas y pasos;
 * los métodos derivados convierten a unidades físicas (mm, mm/s) según la calibración.
 *
 * <p>Distinción (correción recurrente de la cátedra): aquí viven los <b>parámetros</b>. Las
 * <b>condiciones iniciales</b> (posiciones iniciales y el valor concreto de cada velocidad libre)
 * se derivan de {@link #seed()} dentro del motor, no se fijan acá.
 */
public record Config(
        int latticeLength,      // L  [celdas]
        int vehicleLength,      // ℓ  [celdas]
        double cellSizeMm,      // Δx [mm]
        double timeStepS,       // dt [s]
        int n,                  // N  cantidad de vehículos
        double brakeProb,       // p  probabilidad de frenado aleatorio (R3)
        double freeSpeedMinMmS, // velocidad libre mínima [mm/s]
        double freeSpeedMaxMmS, // velocidad libre máxima [mm/s]
        CollisionRuleType collisionRule,
        InsertionOrder insertionOrder,
        RunProtocol protocol,
        long seed,              // identificador reproducible de la realización
        int steps,              // pasos totales de la corrida
        int transientSteps,     // referencia informativa; el estacionario se decide por inspección
        int outputEvery         // se escribe la salida cada k pasos (1 = todos)
) {

    /** Configuración por defecto calibrada al experimento (ver documento de diseño). */
    public static Config defaults() {
        return new Config(
                5280,                          // L = 30·ℓ
                176,                           // ℓ = 44 mm / 0.25 mm
                0.25,                          // Δx
                1.0 / 24.0,                    // dt (24 fps)
                10,                            // N
                0.1,                           // p
                90.0, 120.0,                   // velocidad libre U[90,120] mm/s
                CollisionRuleType.CLASICA_SALVO_CERO, // default = variante de validación (Hito 2); la primaria experimental es CONTACTO_PURO
                InsertionOrder.RANDOM,
                RunProtocol.FIXED_N,                  // núcleo: N fijo (variar N y p); el incremental es opt-in
                1L,                            // identificador reproducible
                10_000,                        // pasos
                2_000,                         // transitorio (informativo)
                1                              // escribir cada paso
        );
    }

    // --- Derivados (calibración) ---

    /** Cuanto de velocidad Δv = Δx/dt [mm/s]. Por defecto 6 mm/s. */
    public double velocityQuantumMmS() {
        return cellSizeMm / timeStepS;
    }

    /** Longitud física de la pista [mm]. */
    public double trackLengthMm() {
        return latticeLength * cellSizeMm;
    }

    /** Densidad global ρ = N / L_fis [1/mm]. */
    public double densityPerMm() {
        return n / trackLengthMm();
    }

    /** Validación básica de consistencia de los parámetros. */
    public Config {
        if (latticeLength <= 0) throw new IllegalArgumentException("latticeLength debe ser > 0");
        if (vehicleLength <= 0) throw new IllegalArgumentException("vehicleLength debe ser > 0");
        if (cellSizeMm <= 0) throw new IllegalArgumentException("dx debe ser > 0");
        if (timeStepS <= 0) throw new IllegalArgumentException("dt debe ser > 0");
        if (n <= 0) throw new IllegalArgumentException("N debe ser > 0");
        if (latticeLength < n * vehicleLength)
            throw new IllegalArgumentException("no entran " + n + " vehículos de " + vehicleLength
                    + " celdas en una ruta periódica de " + latticeLength + " celdas");
        if (brakeProb < 0 || brakeProb > 1) throw new IllegalArgumentException("p debe estar en [0,1]");
        if (freeSpeedMinMmS <= 0) throw new IllegalArgumentException("vfree-min debe ser > 0");
        if (freeSpeedMaxMmS < freeSpeedMinMmS)
            throw new IllegalArgumentException("vfree-max debe ser >= vfree-min");
        if (collisionRule == null) throw new IllegalArgumentException("collisionRule no puede ser null");
        if (insertionOrder == null) throw new IllegalArgumentException("insertionOrder no puede ser null");
        if (protocol == null) throw new IllegalArgumentException("protocol no puede ser null");
        if (steps < 0) throw new IllegalArgumentException("steps debe ser >= 0");
        if (transientSteps < 0) throw new IllegalArgumentException("transient debe ser >= 0");
        if (outputEvery <= 0) throw new IllegalArgumentException("outputEvery debe ser > 0");
    }
}
