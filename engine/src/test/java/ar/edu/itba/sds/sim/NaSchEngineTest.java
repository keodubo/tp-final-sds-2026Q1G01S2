package ar.edu.itba.sds.sim;

import ar.edu.itba.sds.config.CollisionRuleType;
import ar.edu.itba.sds.config.Config;
import ar.edu.itba.sds.config.InsertionOrder;
import ar.edu.itba.sds.config.RunProtocol;
import ar.edu.itba.sds.model.PeriodicTrack;
import ar.edu.itba.sds.model.Vehicle;
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

    /**
     * Config homogénea puntual para la validación analítica: ℓ=1, un único vMax, p=0 y Δx=Δt=1
     * (Δv=1, así vfree=vMax ⇒ round(vfree/Δv)=vMax).
     */
    private static Config homogenea(int n, int latticeLength, int vmax) {
        return new Config(
                latticeLength, 1, 1.0, 1.0,
                n, 0.0, vmax, vmax,
                CollisionRuleType.CLASICA_SALVO_CERO, InsertionOrder.RANDOM, RunProtocol.FIXED_N,
                1L, 0, 0, 1);
    }

    /**
     * Config para el protocolo incremental con intervalo corto de test: dt=90 ⇒ pasosPorLote =
     * round(180/90) = 2; Δx=90 ⇒ Δv=1; vfree 3..6 ⇒ vMax 3..6; ℓ=1; L=400 (sobra lugar para insertar).
     */
    private static Config incremental(int target, InsertionOrder orden) {
        return new Config(
                400, 1, 90.0, 90.0,
                target, 0.0, 3.0, 6.0,
                CollisionRuleType.CLASICA_SALVO_CERO, orden, RunProtocol.INCREMENTAL_180S,
                7L, 0, 0, 1);
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
    void ordenDeInsercionOrdenaPorVelocidadLibre() {
        // FIXED_N: los vehículos quedan a lo largo de la ruta en orden de inserción (por vfree).
        // ASCENDING ⇒ vMax no decreciente; DESCENDING ⇒ no creciente (round es monótona).
        assertOrdenEspacialPorVmax(InsertionOrder.ASCENDING, true);
        assertOrdenEspacialPorVmax(InsertionOrder.DESCENDING, false);
    }

    private void assertOrdenEspacialPorVmax(InsertionOrder orden, boolean noDecreciente) {
        Config d = Config.defaults();
        Config cfg = new Config(
                d.latticeLength(), d.vehicleLength(), d.cellSizeMm(), d.timeStepS(),
                30, 0.0, d.freeSpeedMinMmS(), d.freeSpeedMaxMmS(),
                CollisionRuleType.CLASICA_SALVO_CERO, orden, RunProtocol.FIXED_N,
                5L, 0, 0, 1);
        NaSchEngine engine = new NaSchEngine(cfg);
        engine.initialize();

        PeriodicTrack track = engine.track();
        for (int i = 0; i + 1 < track.size(); i++) {
            int actual = track.get(i).vMax();
            int siguiente = track.get(i + 1).vMax();
            if (noDecreciente) {
                assertTrue(actual <= siguiente, "ASCENDING: " + actual + " > " + siguiente);
            } else {
                assertTrue(actual >= siguiente, "DESCENDING: " + actual + " < " + siguiente);
            }
        }
    }

    @Test
    void protocoloIncrementalCreceEnLotesSinSolaparse() {
        Config cfg = incremental(20, InsertionOrder.ASCENDING);
        NaSchEngine engine = new NaSchEngine(cfg);
        engine.initialize();

        assertEquals(5, engine.track().size(), "el protocolo incremental arranca con 5");

        int previo = 5;
        for (int t = 0; t < 200; t++) {
            engine.step();
            int ahora = engine.track().size();
            assertTrue(ahora >= previo, "N no debe decrecer (paso " + t + ")");
            assertTrue(ahora <= 20, "N no debe pasar del objetivo");
            assertTrue(ahora == previo || ahora == previo + 5, "los vehículos entran de a lotes de 5");
            assertTrue(engine.track().isConsistent(), "sin solapamiento al insertar (paso " + t + ")");
            previo = ahora;
        }
        assertEquals(20, engine.track().size(), "debe alcanzar el objetivo N=30/20 por lotes");
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
        for (CollisionRuleType regla : CollisionRuleType.values()) {
            Config cfg = calibrada(12, 0.3, regla, 2026L);
            NaSchEngine engine = new NaSchEngine(cfg);
            engine.initialize();

            for (int t = 0; t < 600; t++) {
                engine.step();
                PeriodicTrack track = engine.track();
                assertEquals(12, track.size(), "N debe conservarse (" + regla + ", paso " + t + ")");
                // isConsistent() exige huecos >= 0, suma correcta y orden cíclico: cubre
                // "sin solapamiento" y "orden periódico preservado".
                assertTrue(track.isConsistent(), "ruta inconsistente con " + regla + " en el paso " + t);
            }
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
    void deterministaReproduceDiagramaFundamentalAnalitico() {
        // Configuración homogénea puntual: ℓ=1, vmax único, p=0, Δx=Δt=1 ⇒ Δv=1.
        // Con condición inicial pareja (huecos iguales g) el estacionario es v̄ = min(vmax, g),
        // así que el flujo Q = ρ·v̄ debe coincidir con el analítico min(ρ·vmax, 1−ρ).
        int vmax = 5;
        int n = 20;
        int[] huecos = {10, 5, 4, 2, 1}; // cubre flujo libre, el pico ρc=1/(vmax+1) y la rama congestionada

        for (int g : huecos) {
            int L = n * (1 + g);          // ℓ=1 ⇒ huecos exactamente g
            Config cfg = homogenea(n, L, vmax);

            NaSchEngine engine = new NaSchEngine(cfg);
            engine.initializeEvenlySpread();

            int transitorio = 50;
            int medicion = 50;
            for (int t = 0; t < transitorio; t++) engine.step();

            long avance = 0;
            for (int t = 0; t < medicion; t++) {
                engine.step();
                for (int i = 0; i < engine.track().size(); i++) {
                    avance += engine.track().get(i).velocity(); // velocidad = desplazamiento del cuadro
                }
            }
            double vMedia = (double) avance / (n * medicion);
            double rho = (double) n / L;
            double qSim = rho * vMedia;
            double qAnalitico = Math.min(rho * vmax, 1.0 - rho);

            assertEquals(qAnalitico, qSim, 1e-9,
                    "diagrama fundamental fuera de tolerancia en ρ=" + rho + " (hueco " + g + ")");
        }
    }

    @Test
    void contactoPuroFormaAgrupamientosSinSolaparse() {
        // Densidad alta y heterogénea con contacto puro y p=0: los rápidos alcanzan a los lentos y
        // forman agrupamientos (aparecen huecos en 0) sin atravesarlos nunca.
        Config cfg = calibrada(25, 0.0, CollisionRuleType.CONTACTO_PURO, 123L);
        NaSchEngine engine = new NaSchEngine(cfg);
        engine.initialize();

        boolean huboContacto = false;
        for (int t = 0; t < 1000; t++) {
            engine.step();
            PeriodicTrack track = engine.track();
            assertTrue(track.isConsistent(), "contacto puro no debe solapar (paso " + t + ")");
            for (int i = 0; i < track.size(); i++) {
                if (track.gapAhead(i) == 0) huboContacto = true;
            }
        }
        assertTrue(huboContacto, "se esperaban agrupamientos a contacto (hueco 0) con contacto puro");
    }
}
