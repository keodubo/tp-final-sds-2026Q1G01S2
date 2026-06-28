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
        long seed,              // una semilla = una realización
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
                CollisionRuleType.CONTACTO_PURO,
                1L,                            // semilla
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
        if (vehicleLength <= 0) throw new IllegalArgumentException("vehicleLength debe ser > 0");
        if (latticeLength < n * vehicleLength)
            throw new IllegalArgumentException("no entran " + n + " vehículos de " + vehicleLength
                    + " celdas en un anillo de " + latticeLength + " celdas");
        if (brakeProb < 0 || brakeProb > 1) throw new IllegalArgumentException("p debe estar en [0,1]");
        if (outputEvery <= 0) throw new IllegalArgumentException("outputEvery debe ser > 0");
    }
}
