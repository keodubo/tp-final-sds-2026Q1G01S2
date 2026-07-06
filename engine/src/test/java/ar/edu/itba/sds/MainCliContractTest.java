package ar.edu.itba.sds;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.io.ByteArrayOutputStream;
import java.io.PrintStream;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Contrato observable de la CLI: cada rama de error debe fallar con código 1 y sin dejar salida a
 * medias; la ayuda debe documentar todas las opciones reales; y las banderas nuevas
 * ({@code --even-spread}) deben tener efecto observable. Todo blackbox por {@link Main#run}.
 */
class MainCliContractTest {

    @TempDir
    Path tmp;

    // --- Ramas de error del parser (COV-2) ---

    @Test
    void ordenInvalidoFallaSinCrearSalida() {
        Path out = tmp.resolve("s.txt");
        Result r = run("--order", "XX", "--out", out.toString());
        assertEquals(1, r.exitCode());
        assertFalse(Files.exists(out));
        assertTrue(r.err().contains("orden inválido"), r.err());
    }

    @Test
    void protocoloInvalidoFallaSinCrearSalida() {
        Path out = tmp.resolve("s.txt");
        Result r = run("--protocol", "XX", "--out", out.toString());
        assertEquals(1, r.exitCode());
        assertFalse(Files.exists(out));
        assertTrue(r.err().contains("protocolo inválido"), r.err());
    }

    @Test
    void faltaValorParaOpcionFallaSinCrearSalida() {
        Path out = tmp.resolve("s.txt");
        Result r = run("--out", out.toString(), "--n"); // --n sin valor al final
        assertEquals(1, r.exitCode());
        assertFalse(Files.exists(out));
        assertTrue(r.err().contains("falta valor para --n"), r.err());
    }

    @Test
    void valorNumericoInvalidoFallaSinCrearSalida() {
        Path out = tmp.resolve("s.txt");
        Result r = run("--n", "abc", "--out", out.toString());
        assertEquals(1, r.exitCode());
        assertFalse(Files.exists(out));
        assertTrue(r.err().contains("valor numérico inválido"), r.err());
    }

    @Test
    void cantidadDeVehiculosCeroFallaPorValidacionDeConfig() {
        Path out = tmp.resolve("s.txt");
        Result r = run("--n", "0", "--out", out.toString());
        assertEquals(1, r.exitCode());
        assertFalse(Files.exists(out));
        assertTrue(r.err().contains("N debe ser > 0"), r.err());
    }

    @Test
    void ayudaImprimeUsoYRetornaCero() {
        Result r = run("--help");
        assertEquals(0, r.exitCode());
        assertTrue(r.out().contains("Uso:"), r.out());
    }

    // --- Fail-fast en tokens sueltos (CLI-03): un typo sin guion no debe revertir a defaults en silencio ---

    @Test
    void tokenSueltoSinGuionFallaSinCrearSalida() {
        Path out = tmp.resolve("s.txt");
        Result r = run("basura", "--n", "5", "--steps", "2", "--out", out.toString());
        assertEquals(1, r.exitCode(), "un argumento suelto sin guion debe ser error, no ignorarse");
        assertFalse(Files.exists(out));
    }

    // --- Bandera de validación --even-spread (RM-03/G14): reparto uniforme determinista ---

    @Test
    void evenSpreadConProtocoloIncrementalFallaSinCrearSalida() {
        Path out = tmp.resolve("incremental-even.txt");
        Result r = run("--protocol", "INCREMENTAL_180S", "--even-spread", "--steps", "1",
                "--out", out.toString());

        assertEquals(1, r.exitCode(), "--even-spread no debe habilitar un incremental falso");
        assertFalse(Files.exists(out));
        assertTrue(r.err().contains("--even-spread"), r.err());
        assertTrue(r.err().contains("INCREMENTAL_180S"), r.err());
        assertTrue(r.err().contains("no puede combinarse"), r.err());
    }

    @Test
    void banderaEvenSpreadUbicaVehiculosConHuecosParejosDesdeCero() throws Exception {
        // N=5, L=5280, ℓ=176 ⇒ libre=4400, hueco=880, paso=1056 celdas = 264 mm. Sin offset aleatorio:
        // id k queda en x = k·264 mm, velocidad 0.
        Path out = tmp.resolve("even.txt");
        Result r = run("--n", "5", "--p", "0", "--steps", "1", "--even-spread", "--out", out.toString());
        assertEquals(0, r.exitCode(), r.err());
        assertTrue(Files.exists(out));
        String text = Files.readString(out);
        assertTrue(text.contains("0 0 0.0000 0.0000"), "id 0 debe arrancar en x=0 (reparto uniforme)");
        assertTrue(text.contains("0 4 1056.0000 0.0000"), "id 4 en x=4·264=1056 mm");
    }

    @Test
    void salidaIncrementalNoAdelantaElLoteEnLaFronteraEscritaAntesDelPaso() throws Exception {
        // dt=90 ⇒ lote cada 2 pasos. La CLI registra el estado antes de ejecutar step(): el paso 2
        // todavía representa el cierre del lote N=5; el lote N=10 aparece en la siguiente muestra.
        Path out = tmp.resolve("incremental-boundary.txt");
        Result r = run("--n", "10", "--L", "400", "--ell", "1", "--dx", "90", "--dt", "90",
                "--vfree-min", "3", "--vfree-max", "6", "--p", "0",
                "--protocol", "INCREMENTAL_180S", "--order", "ASCENDING", "--steps", "4",
                "--output-every", "1", "--seed", "7", "--out", out.toString());

        assertEquals(0, r.exitCode(), r.err());
        String text = Files.readString(out);
        assertEquals(5, filasDelPaso(text, 0));
        assertEquals(5, filasDelPaso(text, 1));
        assertEquals(5, filasDelPaso(text, 2), "la frontera escrita antes del paso conserva N=5");
        assertEquals(10, filasDelPaso(text, 3), "el lote insertado se observa en la muestra siguiente");
    }

    // --- La ayuda documenta toda la superficie real de la CLI (CLI-02) ---

    @Test
    void ayudaDocumentaTransientYEvenSpread() {
        Result r = run("--help");
        assertTrue(r.out().contains("--transient"), "la ayuda debe listar --transient");
        assertTrue(r.out().contains("--even-spread"), "la ayuda debe listar --even-spread");
    }

    private Result run(String... args) {
        ByteArrayOutputStream stdout = new ByteArrayOutputStream();
        ByteArrayOutputStream stderr = new ByteArrayOutputStream();
        int exitCode = Main.run(args, new PrintStream(stdout), new PrintStream(stderr));
        return new Result(exitCode, stdout.toString(), stderr.toString());
    }

    private static long filasDelPaso(String text, int step) {
        return text.lines().filter(line -> line.startsWith(step + " ")).count();
    }

    private record Result(int exitCode, String out, String err) { }
}
