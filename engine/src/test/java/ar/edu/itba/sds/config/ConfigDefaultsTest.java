package ar.edu.itba.sds.config;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Ancla la configuración por defecto: la regla oficial del experimento y la calibración
 * no-negociable. Estos valores son correcciones repetidas de la cátedra, así que se fijan por test
 * para que un cambio accidental de default rompa la compilación de la batería.
 */
class ConfigDefaultsTest {

    @Test
    void laReglaPorDefectoEsLaOficialContactoPuro() {
        // CONTACTO_PURO es la variante oficial del experimento; CLASICA_SALVO_CERO es solo validación
        // (NaSch clásico, p=0 homogéneo). El default no debe correr la variante de validación.
        assertEquals(CollisionRuleType.CONTACTO_PURO, Config.defaults().collisionRule());
    }

    @Test
    void anclaLaCalibracionNoNegociable() {
        Config d = Config.defaults();
        assertEquals(5280, d.latticeLength(), "L = 30·ℓ celdas");
        assertEquals(176, d.vehicleLength(), "ℓ = 44 mm / 0.25 mm");
        assertEquals(0.25, d.cellSizeMm(), "Δx = 0.25 mm");
        assertEquals(1.0 / 24.0, d.timeStepS(), 1e-12, "dt = 1/24 s (24 fps)");
        assertEquals(6.0, d.velocityQuantumMmS(), 1e-12, "Δv = Δx/dt = 6 mm/s");
        assertEquals(1320.0, d.trackLengthMm(), 1e-9, "L_fis = 1320 mm");
        assertEquals(90.0, d.freeSpeedMinMmS(), "vfree ∈ [90,120] mm/s");
        assertEquals(120.0, d.freeSpeedMaxMmS(), "vfree ∈ [90,120] mm/s");
    }
}
