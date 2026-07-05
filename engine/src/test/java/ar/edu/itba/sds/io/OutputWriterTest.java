package ar.edu.itba.sds.io;

import ar.edu.itba.sds.config.CollisionRuleType;
import ar.edu.itba.sds.config.Config;
import ar.edu.itba.sds.config.InsertionOrder;
import ar.edu.itba.sds.config.RunProtocol;
import ar.edu.itba.sds.model.PeriodicTrack;
import ar.edu.itba.sds.model.Vehicle;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

class OutputWriterTest {

    @TempDir
    Path tmp;

    @Test
    void escribeSoloEstadoFisicoEnUnidadesFisicas() throws Exception {
        Path out = tmp.resolve("run.txt");
        Config cfg = Config.defaults();
        PeriodicTrack track = new PeriodicTrack(20, 4, List.of(
                new Vehicle(7, 8, 3, 5)
        ));

        try (OutputWriter writer = new OutputWriter(out, cfg)) {
            writer.writeStep(12, track);
        }

        String text = Files.readString(out);
        assertTrue(text.contains("# columnas: paso id x_mm v_mmps"));
        assertTrue(text.contains("realizacion_id=1"));
        assertFalse(text.contains("realization_seed"));
        assertTrue(text.contains("12 7 2.0000 18.0000"));
        assertFalse(text.contains("color"));
        assertFalse(text.contains("radio"));
    }

    @Test
    void cabeceraFixedNNoRotulaUnOrdenDeInsercionReal() throws Exception {
        // En FIXED_N no hay historia de inserción: el orden es irrelevante. La cabecera no debe
        // filtrar el default RANDOM (se confundiría con el protocolo incremental ordenado).
        Path out = tmp.resolve("fixed.txt");
        Config cfg = new Config(5280, 176, 0.25, 1.0 / 24.0, 10, 0.1, 90.0, 120.0,
                CollisionRuleType.CONTACTO_PURO, InsertionOrder.RANDOM, RunProtocol.FIXED_N,
                1L, 10, 2000, 1);
        try (OutputWriter writer = new OutputWriter(out, cfg)) {
            writer.writeStep(0, new PeriodicTrack(5280, 176, List.of(new Vehicle(0, 0, 0, 18))));
        }
        String text = Files.readString(out);
        assertTrue(text.contains("order=SIN_ORDEN"), "FIXED_N no debe rotular un orden real");
        assertFalse(text.contains("order=RANDOM"), "no debe filtrar el default RANDOM");
    }

    @Test
    void cabeceraIncrementalConservaElOrdenDeInsercion() throws Exception {
        // En INCREMENTAL_180S el orden SÍ importa (ascending/descending/random): debe registrarse.
        Path out = tmp.resolve("inc.txt");
        Config cfg = new Config(5280, 176, 0.25, 1.0 / 24.0, 30, 0.1, 90.0, 120.0,
                CollisionRuleType.CONTACTO_PURO, InsertionOrder.ASCENDING, RunProtocol.INCREMENTAL_180S,
                1L, 10, 2000, 1);
        try (OutputWriter writer = new OutputWriter(out, cfg)) {
            writer.writeStep(0, new PeriodicTrack(5280, 176, List.of(new Vehicle(0, 0, 0, 18))));
        }
        assertTrue(Files.readString(out).contains("order=ASCENDING"), "el orden incremental debe registrarse");
    }
}
