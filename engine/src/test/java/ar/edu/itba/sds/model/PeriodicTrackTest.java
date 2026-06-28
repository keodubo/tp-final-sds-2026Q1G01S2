package ar.edu.itba.sds.model;

import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Geometría de la ruta periódica (gaps, vecinos, consistencia). Lógica determinista ya implementada.
 */
class PeriodicTrackTest {

    /** Línea periódica L=20, ℓ=4, 3 vehículos con cola en 0, 8, 14. */
    private PeriodicTrack sample() {
        return new PeriodicTrack(20, 4, List.of(
                new Vehicle(0, 0, 0, 5),
                new Vehicle(1, 8, 0, 5),
                new Vehicle(2, 14, 0, 5)));
    }

    @Test
    void gapAheadCuentaCeldasLibresHastaLaColaDelLider() {
        PeriodicTrack t = sample();
        assertEquals(4, t.gapAhead(0)); // 8 - 0 - 4
        assertEquals(2, t.gapAhead(1)); // 14 - 8 - 4
        assertEquals(2, t.gapAhead(2)); // envoltura: (0 - 14 - 4) mod 20
    }

    @Test
    void nearestGapEsElMinimoEntreAdelanteYAtras() {
        PeriodicTrack t = sample();
        assertEquals(2, t.nearestGap(0)); // min(adelante=4, atras=2)
        assertEquals(2, t.nearestGap(1)); // min(adelante=2, atras=4)
        assertEquals(2, t.nearestGap(2)); // min(adelante=2, atras=2)
    }

    @Test
    void liderYSeguidorSonPeriodicos() {
        PeriodicTrack t = sample();
        assertEquals(1, t.leader(0).id());
        assertEquals(0, t.leader(2).id());   // envoltura
        assertEquals(2, t.follower(0).id()); // envoltura
    }

    @Test
    void contactoDaGapCero() {
        // cola en 0 y 4 con ℓ=4 ⇒ cuerpos [0,3] y [4,7] a contacto
        PeriodicTrack t = new PeriodicTrack(20, 4, List.of(
                new Vehicle(0, 0, 0, 5),
                new Vehicle(1, 4, 0, 5)));
        assertEquals(0, t.gapAhead(0));
    }

    @Test
    void configuracionValidaEsConsistente() {
        assertTrue(sample().isConsistent());
    }

    @Test
    void solapamientoNoEsConsistente() {
        // cuerpos [0,3] y [2,5] se solapan
        PeriodicTrack t = new PeriodicTrack(20, 4, List.of(
                new Vehicle(0, 0, 0, 5),
                new Vehicle(1, 2, 0, 5)));
        assertFalse(t.isConsistent());
    }
}
