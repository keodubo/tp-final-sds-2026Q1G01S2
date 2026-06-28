package ar.edu.itba.sds.io;

import ar.edu.itba.sds.config.Config;
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
        assertTrue(text.contains("12 7 2.0000 18.0000"));
        assertFalse(text.contains("color"));
        assertFalse(text.contains("radio"));
    }
}
