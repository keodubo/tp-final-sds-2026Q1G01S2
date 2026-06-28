package ar.edu.itba.sds.sim;

import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;

/**
 * Contrato de invariantes del motor — son los tests a escribir <b>primero</b> (TDD) cuando se
 * implementen {@link NaSchEngine#initialize()}, {@link NaSchEngine#step()} y las reglas de colisión.
 * Están deshabilitados hasta el Hito 2/4 para que la build quede en verde.
 */
class NaSchEngineTest {

    @Test
    @Disabled("Hito 2: la condición inicial deja una ruta consistente y N vehículos")
    void initializeDejaRutaConsistente() { }

    @Test
    @Disabled("Hito 2: vMax_i = round(vfree_i / Δv) cae en el rango esperado {15..20}")
    void velocidadesMaximasEnRango() { }

    @Test
    @Disabled("Hito 2: cada paso conserva N y deja la ruta consistente (sin solapamiento)")
    void cadaPasoConservaNySinSolapamiento() { }

    @Test
    @Disabled("Hito 2: con el mismo identificador de realización la corrida es bit-a-bit reproducible")
    void mismaRealizacionMismaCorrida() { }

    @Test
    @Disabled("Hito 3: homogéneo + p=0 reproduce el diagrama fundamental analítico Q(ρ)=min(ρ·vmax, 1-ρ)")
    void deterministaReproduceDiagramaFundamentalAnalitico() { }

    @Test
    @Disabled("Hito 4/5: con p>0 (stop-and-go) la velocidad de saturación cae por debajo de la del más "
            + "lento; con p=0 el cluster va exactamente a la del más lento. Confirmar antes de testearlo como propiedad")
    void contactoPuroColapsaConFrenadoAleatorio() { }
}
