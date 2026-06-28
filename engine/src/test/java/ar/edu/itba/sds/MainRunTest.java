package ar.edu.itba.sds;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.io.ByteArrayOutputStream;
import java.io.PrintStream;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.*;

class MainRunTest {

    @TempDir
    Path tmp;

    @Test
    void opcionDesconocidaFallaSinCrearSalida() {
        Path out = tmp.resolve("salida.txt");
        Result result = run("--bad-option", "--out", out.toString());

        assertEquals(1, result.exitCode());
        assertFalse(Files.exists(out));
        assertTrue(result.err().contains("opción desconocida"));
    }

    @Test
    void motorPendienteFallaSinDejarArchivoParcial() {
        Path out = tmp.resolve("salida.txt");
        Result result = run("--steps", "1", "--out", out.toString());

        assertEquals(2, result.exitCode());
        assertFalse(Files.exists(out));
        assertTrue(result.err().contains("motor aún no implementado"));
    }

    @Test
    void reglaInvalidaFallaConErrorDeUsoSinCrearSalida() {
        Path out = tmp.resolve("salida.txt");
        Result result = run("--rule", "INVALIDA", "--out", out.toString());

        assertEquals(1, result.exitCode());
        assertFalse(Files.exists(out));
        assertTrue(result.err().contains("regla inválida"));
    }

    private Result run(String... args) {
        ByteArrayOutputStream stdout = new ByteArrayOutputStream();
        ByteArrayOutputStream stderr = new ByteArrayOutputStream();
        int exitCode = Main.run(
                args,
                new PrintStream(stdout),
                new PrintStream(stderr)
        );
        return new Result(exitCode, stdout.toString(), stderr.toString());
    }

    private record Result(int exitCode, String out, String err) { }
}
