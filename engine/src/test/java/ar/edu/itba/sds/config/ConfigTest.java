package ar.edu.itba.sds.config;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class ConfigTest {

    @Test
    void rechazaCantidadNoPositivaDeVehiculos() {
        Config d = Config.defaults();

        assertThrows(IllegalArgumentException.class, () -> new Config(
                d.latticeLength(), d.vehicleLength(), d.cellSizeMm(), d.timeStepS(),
                0, d.brakeProb(), d.freeSpeedMinMmS(), d.freeSpeedMaxMmS(),
                d.collisionRule(), d.insertionOrder(), d.protocol(),
                d.seed(), d.steps(), d.transientSteps(), d.outputEvery()
        ));
    }

    @Test
    void rechazaCalibracionFisicaNoPositiva() {
        Config d = Config.defaults();

        assertThrows(IllegalArgumentException.class, () -> new Config(
                d.latticeLength(), d.vehicleLength(), 0.0, d.timeStepS(),
                d.n(), d.brakeProb(), d.freeSpeedMinMmS(), d.freeSpeedMaxMmS(),
                d.collisionRule(), d.insertionOrder(), d.protocol(),
                d.seed(), d.steps(), d.transientSteps(), d.outputEvery()
        ));
        assertThrows(IllegalArgumentException.class, () -> new Config(
                d.latticeLength(), d.vehicleLength(), d.cellSizeMm(), 0.0,
                d.n(), d.brakeProb(), d.freeSpeedMinMmS(), d.freeSpeedMaxMmS(),
                d.collisionRule(), d.insertionOrder(), d.protocol(),
                d.seed(), d.steps(), d.transientSteps(), d.outputEvery()
        ));
    }

    @Test
    void rechazaRangoDeVelocidadLibreInvalido() {
        Config d = Config.defaults();

        assertThrows(IllegalArgumentException.class, () -> new Config(
                d.latticeLength(), d.vehicleLength(), d.cellSizeMm(), d.timeStepS(),
                d.n(), d.brakeProb(), 120.0, 90.0,
                d.collisionRule(), d.insertionOrder(), d.protocol(),
                d.seed(), d.steps(), d.transientSteps(), d.outputEvery()
        ));
    }

    @Test
    void rechazaCantidadNegativaDePasos() {
        Config d = Config.defaults();

        assertThrows(IllegalArgumentException.class, () -> new Config(
                d.latticeLength(), d.vehicleLength(), d.cellSizeMm(), d.timeStepS(),
                d.n(), d.brakeProb(), d.freeSpeedMinMmS(), d.freeSpeedMaxMmS(),
                d.collisionRule(), d.insertionOrder(), d.protocol(),
                d.seed(), -1, d.transientSteps(), d.outputEvery()
        ));
    }
}
