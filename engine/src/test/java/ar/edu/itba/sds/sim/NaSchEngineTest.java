package ar.edu.itba.sds.sim;

import ar.edu.itba.sds.config.CollisionRuleType;
import ar.edu.itba.sds.config.Config;
import ar.edu.itba.sds.config.InsertionOrder;
import ar.edu.itba.sds.config.RunProtocol;
import ar.edu.itba.sds.model.PeriodicTrack;
import ar.edu.itba.sds.model.Vehicle;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Invariantes del motor (TDD). La geometría sin solapamiento se verifica con
 * {@link PeriodicTrack#isConsistent()} y el orden periódico se chequea explícitamente.
 */
class NaSchEngineTest {

    /** Config calibrada (Δv=6, vfree U[90,120]) con N chico para los tests de invariantes. */
    private static Config calibrada(int n, double p, CollisionRuleType regla, long seed) {
        Config d = Config.defaults();
        return new Config(
                d.latticeLength(), d.vehicleLength(), d.cellSizeMm(), d.timeStepS(),
                n, p, d.freeSpeedMinMmS(), d.freeSpeedMaxMmS(),
                regla, d.insertionOrder(), RunProtocol.FIXED_N,
                seed, d.steps(), d.transientSteps(), d.outputEvery());
    }

    // ------------------------------------------------------------------
    // Hito 2: condición inicial
    // ------------------------------------------------------------------

    @Test
    void initializeDejaRutaConsistente() {
        Config cfg = calibrada(10, 0.1, CollisionRuleType.CLASICA_SALVO_CERO, 42L);
        NaSchEngine engine = new NaSchEngine(cfg);
        engine.initialize();

        PeriodicTrack track = engine.track();
        assertEquals(10, track.size());
        assertTrue(track.isConsistent(), "la ruta inicial no debe tener solapamiento");
        for (int i = 0; i < track.size(); i++) {
            Vehicle v = track.get(i);
            assertEquals(0, v.velocity(), "la velocidad inicial debe ser 0");
            assertTrue(v.position() >= 0 && v.position() < cfg.latticeLength());
        }
    }

    @Test
    void initializeEvenlySpreadDejaRutaConsistente() {
        Config cfg = calibrada(7, 0.0, CollisionRuleType.CLASICA_SALVO_CERO, 1L);
        NaSchEngine engine = new NaSchEngine(cfg);
        engine.initializeEvenlySpread();

        PeriodicTrack track = engine.track();
        assertEquals(7, track.size());
        assertTrue(track.isConsistent());
    }

    @Test
    void velocidadesMaximasEnRango() {
        // Calibración: vfree ~ U[90,120], Δv=6 ⇒ vMax = round(vfree/6) ∈ {15..20}.
        Config cfg = calibrada(30, 0.1, CollisionRuleType.CLASICA_SALVO_CERO, 7L);
        NaSchEngine engine = new NaSchEngine(cfg);
        engine.initialize();

        PeriodicTrack track = engine.track();
        for (int i = 0; i < track.size(); i++) {
            int vMax = track.get(i).vMax();
            assertTrue(vMax >= 15 && vMax <= 20, "vMax fuera de {15..20}: " + vMax);
        }
    }

    // ------------------------------------------------------------------
    // Hito 2/3: dinámica (pendiente)
    // ------------------------------------------------------------------

    @Test
    void cadaPasoConservaNySinSolapamiento() {
        Config cfg = calibrada(12, 0.3, CollisionRuleType.CLASICA_SALVO_CERO, 2026L);
        NaSchEngine engine = new NaSchEngine(cfg);
        engine.initialize();

        for (int t = 0; t < 600; t++) {
            engine.step();
            PeriodicTrack track = engine.track();
            assertEquals(12, track.size(), "N debe conservarse (paso " + t + ")");
            // isConsistent() exige huecos >= 0, suma correcta y orden cíclico: cubre
            // "sin solapamiento" y "orden periódico preservado".
            assertTrue(track.isConsistent(), "ruta inconsistente en el paso " + t);
        }
    }

    @Test
    void mismaRealizacionMismaCorrida() {
        Config cfg = calibrada(15, 0.25, CollisionRuleType.CLASICA_SALVO_CERO, 99L);

        NaSchEngine a = new NaSchEngine(cfg);
        NaSchEngine b = new NaSchEngine(cfg);
        a.initialize();
        b.initialize();
        assertEquals(snapshot(a.track()), snapshot(b.track()), "condición inicial idéntica");

        for (int t = 0; t < 400; t++) {
            a.step();
            b.step();
            assertEquals(snapshot(a.track()), snapshot(b.track()),
                    "la corrida debe ser idéntica bit-a-bit en el paso " + t);
        }
    }

    /** Estado de la ruta como lista de [id, posición, velocidad] ordenada por id (comparable). */
    private static java.util.List<java.util.List<Integer>> snapshot(PeriodicTrack track) {
        java.util.List<java.util.List<Integer>> filas = new java.util.ArrayList<>();
        for (int i = 0; i < track.size(); i++) {
            Vehicle v = track.get(i);
            filas.add(java.util.List.of(v.id(), v.position(), v.velocity()));
        }
        filas.sort(java.util.Comparator.comparingInt(f -> f.get(0)));
        return filas;
    }

    @Test
    @Disabled("Hito 3: homogéneo + p=0 reproduce el diagrama fundamental analítico Q(ρ)=min(ρ·vmax, 1-ρ)")
    void deterministaReproduceDiagramaFundamentalAnalitico() { }

    @Test
    @Disabled("Hito 4/5: contacto puro forma agrupamientos sin atravesar al líder")
    void contactoPuroFormaAgrupamientos() { }
}
