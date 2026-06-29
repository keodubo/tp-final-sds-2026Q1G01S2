package ar.edu.itba.sds.sim.collision;

import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Variante A (contacto puro). Se prueba el contrato observable de {@code resolve}: cómo un seguidor
 * rápido queda a contacto detrás de un líder lento (sin atravesarlo ni solaparse) y hereda su
 * velocidad, cómo avanza libre cuando no lo alcanza, y la ruta llena.
 */
class ContactoPuroTest {

    private final ContactoPuro regla = new ContactoPuro();

    @Test
    void seguidorRapidoQuedaAContactoYHeredaLaVelocidadDelLider() {
        // ℓ=1, L=25. Seguidor (deseada 8) a 3 celdas de un líder lento (deseada 2, con vía libre).
        CollisionContext ctx = new CollisionContext(25, 1, List.of(3, 20), List.of(8, 2));

        List<Movimiento> mov = regla.resolve(ctx);

        // Líder avanza 2; seguidor avanza hasta el contacto: 3 + 2 = 5, y hereda la velocidad 2.
        assertEquals(new Movimiento(5, 2), mov.get(0));
        assertEquals(new Movimiento(2, 2), mov.get(1));
        // No lo atraviesa ni se solapa: despl_seguidor (5) ≤ hueco (3) + despl_lider (2).
        assertTrue(mov.get(0).desplazamiento() <= 3 + mov.get(1).desplazamiento());
    }

    @Test
    void avanzaLibreSiNoAlcanzaAlLider() {
        // Seguidor lento/lejos: no llega al líder ⇒ mantiene su velocidad.
        CollisionContext ctx = new CollisionContext(31, 1, List.of(10, 20), List.of(5, 3));

        List<Movimiento> mov = regla.resolve(ctx);

        assertEquals(new Movimiento(5, 5), mov.get(0)); // libre: conserva su deseada
        assertEquals(new Movimiento(3, 3), mov.get(1));
    }

    @Test
    void rutaTotalmenteLlenaAvanzaAlMinimo() {
        // ℓ=1, L=3, los tres a contacto: el agrupamiento avanza rígido a la velocidad del más lento.
        CollisionContext ctx = new CollisionContext(3, 1, List.of(0, 0, 0), List.of(3, 5, 4));

        List<Movimiento> mov = regla.resolve(ctx);

        for (Movimiento m : mov) {
            assertEquals(3, m.desplazamiento(), "todos avanzan al mínimo deseado (3)");
            assertEquals(3, m.velocidadSiguiente());
        }
    }

    @Test
    void cadenaDeContactoSeMueveALaVelocidadDelFrente() {
        // Tres en fila: frente libre (deseada 2), dos de atrás a contacto querían ir más rápido.
        // Frente i=2 (vía libre, hueco 30). i=0 e i=1 a contacto (hueco 0) detrás.
        CollisionContext ctx = new CollisionContext(33, 1, List.of(0, 0, 30), List.of(9, 7, 2));

        List<Movimiento> mov = regla.resolve(ctx);

        // El frente marca el paso (2); toda la cadena avanza 2 y hereda 2 sin solaparse.
        for (Movimiento m : mov) {
            assertEquals(2, m.desplazamiento());
            assertEquals(2, m.velocidadSiguiente());
        }
    }
}
