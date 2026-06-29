package ar.edu.itba.sds.sim.collision;

import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Variante B (clásica salvo a distancia 0). Se prueba el contrato observable de {@code resolve}:
 * desplazamiento y velocidad heredada por vehículo, sobre snapshots armados a mano.
 */
class ClasicaSalvoCeroTest {

    private final ClasicaSalvoCero regla = new ClasicaSalvoCero();

    @Test
    void clampeaAlHuecoComoLaR2Clasica() {
        // ℓ=1, L=25, huecos [3,20], deseadas [8,2].
        CollisionContext ctx = new CollisionContext(25, 1, List.of(3, 20), List.of(8, 2));

        List<Movimiento> mov = regla.resolve(ctx);

        // Seguidor: min(8,3)=3 (no llega al líder, deja hueco). Líder: min(2,20)=2.
        assertEquals(new Movimiento(3, 3), mov.get(0));
        assertEquals(new Movimiento(2, 2), mov.get(1));
    }

    @Test
    void aContactoTomaLaVelocidadDelLiderSinSolaparse() {
        // Seguidor a contacto (hueco 0) detrás de un líder que avanza 2.
        CollisionContext ctx = new CollisionContext(22, 1, List.of(0, 20), List.of(8, 2));

        List<Movimiento> mov = regla.resolve(ctx);

        // Seguidor toma la velocidad del líder (acotada por la suya): min(8, 2)=2 → se mueve pegado.
        assertEquals(new Movimiento(2, 2), mov.get(0));
        assertEquals(new Movimiento(2, 2), mov.get(1));
        // No solapa: desplazamiento_seguidor (2) ≤ hueco (0) + desplazamiento_lider (2).
        assertTrue(mov.get(0).desplazamiento() <= 0 + mov.get(1).desplazamiento());
    }

    @Test
    void rutaTotalmenteLlenaQuedaDetenida() {
        // ℓ=1, L=2, ambos a contacto: NaSch clásico ⇒ todos en 0.
        CollisionContext ctx = new CollisionContext(2, 1, List.of(0, 0), List.of(3, 5));

        List<Movimiento> mov = regla.resolve(ctx);

        assertEquals(new Movimiento(0, 0), mov.get(0));
        assertEquals(new Movimiento(0, 0), mov.get(1));
    }
}
