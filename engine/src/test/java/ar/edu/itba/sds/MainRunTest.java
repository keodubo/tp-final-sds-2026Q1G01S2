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
    void corridaExitosaEscribeSalidaFisica() throws Exception {
        Path out = tmp.resolve("salida.txt");
        Result result = run("--n", "5", "--steps", "5", "--p", "0.1", "--out", out.toString());

        assertEquals(0, result.exitCode());
        assertTrue(Files.exists(out));
        String text = Files.readString(out);
        assertTrue(text.contains("# columnas: paso id x_mm v_mmps"));
        // 5 vehículos en el paso 0 (estado inicial, velocidad 0).
        long filasPaso0 = text.lines().filter(l -> l.startsWith("0 ")).count();
        assertEquals(5, filasPaso0);
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
