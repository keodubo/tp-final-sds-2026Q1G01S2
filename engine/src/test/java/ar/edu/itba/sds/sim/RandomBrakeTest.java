package ar.edu.itba.sds.sim;

import org.junit.jupiter.api.Test;

import java.util.random.RandomGenerator;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * Invariante canónico de reproducibilidad de R3 (frenado aleatorio): con {@code p=0} el motor NO
 * consume el PRNG (0 extracciones) y con {@code p>0} consume EXACTAMENTE una extracción por
 * invocación. Una regresión que reordenara la condición de {@link RandomBrake#brakes(double)}
 * (p.ej. evaluar {@code nextDouble()} antes de {@code p>0}) rompería silenciosamente el consumo
 * reproducible del generador; este test lo detecta observando solo la conducta.
 *
 * <p>Behavior-only: se envuelve un {@link RandomGenerator} contando las llamadas a
 * {@code nextDouble()}. El delegado es un {@code java.util.Random}, el mismo generador que
 * construye el motor. Sin reflection sobre miembros privados.
 */
class RandomBrakeTest {

    /** Espía que cuenta las extracciones {@code nextDouble()} y delega en el RNG del motor. */
    private static final class ContadorNextDouble implements RandomGenerator {
        private final RandomGenerator delegado = new java.util.Random(42L);
        private int extracciones = 0;

        @Override
        public long nextLong() {
            return delegado.nextLong();
        }

        @Override
        public double nextDouble() {
            extracciones++;
            return delegado.nextDouble();
        }
    }

    /** Espía que devuelve una extracción fija y controlada, para verificar el criterio draw &lt; p. */
    private static final class ExtraccionFija implements RandomGenerator {
        private final double valor;

        ExtraccionFija(double valor) {
            this.valor = valor;
        }

        @Override
        public long nextLong() {
            return 0L;
        }

        @Override
        public double nextDouble() {
            return valor;
        }
    }

    @Test
    void pCeroNoConsumeElPrngYNuncaFrena() {
        ContadorNextDouble espia = new ContadorNextDouble();
        RandomBrake brake = new RandomBrake(espia);

        for (int i = 0; i < 1000; i++) {
            assertFalse(brake.brakes(0.0), "con p=0 nunca debe frenar");
        }
        assertEquals(0, espia.extracciones,
                "con p=0 el frenado aleatorio no debe consumir el PRNG (0 extracciones)");
    }

    @Test
    void pPositivoConsumeExactamenteUnaExtraccionPorInvocacion() {
        ContadorNextDouble espia = new ContadorNextDouble();
        RandomBrake brake = new RandomBrake(espia);

        int invocaciones = 500;
        for (int i = 0; i < invocaciones; i++) {
            brake.brakes(0.3);
        }
        assertEquals(invocaciones, espia.extracciones,
                "con p>0 debe consumir exactamente una extracción del PRNG por invocación");
    }

    @Test
    void frenaSiiLaExtraccionEsMenorQueP() {
        double p = 0.3;
        assertTrue(new RandomBrake(new ExtraccionFija(0.1)).brakes(p),
                "draw < p debe frenar");
        assertFalse(new RandomBrake(new ExtraccionFija(p)).brakes(p),
                "draw = p no debe frenar (la comparación es < estricto)");
        assertFalse(new RandomBrake(new ExtraccionFija(0.9)).brakes(p),
                "draw > p no debe frenar");
    }
}
