package ar.edu.itba.sds;

import ar.edu.itba.sds.config.CollisionRuleType;
import ar.edu.itba.sds.config.Config;
import ar.edu.itba.sds.config.InsertionOrder;
import ar.edu.itba.sds.config.RunProtocol;
import ar.edu.itba.sds.io.OutputWriter;
import ar.edu.itba.sds.sim.NaSchEngine;

import java.io.IOException;
import java.io.PrintStream;
import java.io.UncheckedIOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

/**
 * Punto de entrada: corre UNA simulación (una realización) dada la configuración por línea de
 * comandos y escribe la salida física. El barrido de la matriz (N × p × variante × realizaciones)
 * lo orquesta el script de Python {@code analysis/run_matrix.py} invocando este jar.
 */
public final class Main {

    private static final Set<String> VALUE_OPTIONS = Set.of(
            "n", "p", "rule", "seed", "steps", "transient", "output-every", "out",
            "order", "protocol", "L", "ell", "dx", "dt", "vfree-min", "vfree-max"
    );
    private static final Set<String> FLAG_OPTIONS = Set.of("h", "help");
    private static final Set<String> ALL_OPTIONS = new HashSet<>();

    static {
        ALL_OPTIONS.addAll(VALUE_OPTIONS);
        ALL_OPTIONS.addAll(FLAG_OPTIONS);
    }

    public static void main(String[] args) {
        int exitCode = run(args, System.out, System.err);
        if (exitCode != 0) {
            System.exit(exitCode);
        }
    }

    static int run(String[] args, PrintStream stdout, PrintStream stderr) {
        Map<String, String> opts;
        try {
            opts = parse(args);
            if (opts.containsKey("help") || opts.containsKey("h")) {
                printUsage(stdout);
                return 0;
            }

            Config cfg = buildConfig(opts);
            Path out = Path.of(opts.getOrDefault("out", "../data/salida.txt"));
            runSimulation(cfg, out, stdout);
            return 0;
        } catch (UsageException e) {
            stderr.println(e.getMessage());
            stderr.println("Usá --help para ver las opciones válidas.");
            return 1;
        } catch (UncheckedIOException e) {
            stderr.println("error de E/S al escribir la salida: " + e.getMessage());
            return 3;
        } catch (UnsupportedOperationException e) {
            stderr.println("[esqueleto] motor aún no implementado: " + e.getMessage());
            stderr.println("Ver hitos en diseno-tp-final-vdv-nasch_v1.md");
            return 2;
        }
    }

    private static void runSimulation(Config cfg, Path out, PrintStream stdout) {
        stdout.printf("NaSch-VDV | N=%d p=%.3f regla=%s orden=%s protocolo=%s realización=%d pasos=%d%n",
                cfg.n(), cfg.brakeProb(), cfg.collisionRule(), cfg.insertionOrder(),
                cfg.protocol(), cfg.seed(), cfg.steps());
        stdout.printf("calibración | Δx=%.3f mm dt=%.4f s Δv=%.3f mm/s L=%.1f mm ρ=%.5f 1/mm%n",
                cfg.cellSizeMm(), cfg.timeStepS(), cfg.velocityQuantumMmS(),
                cfg.trackLengthMm(), cfg.densityPerMm());

        NaSchEngine engine = new NaSchEngine(cfg);
        engine.initialize();

        Path tmp = tempOutputPath(out);
        try {
            try (OutputWriter writer = new OutputWriter(tmp, cfg)) {
                for (int t = 0; t < cfg.steps(); t++) {
                    if (t % cfg.outputEvery() == 0) writer.writeStep(t, engine.track());
                    engine.step();
                }
            }
            if (out.getParent() != null) Files.createDirectories(out.getParent());
            Files.move(tmp, out, StandardCopyOption.REPLACE_EXISTING, StandardCopyOption.ATOMIC_MOVE);
            stdout.println("listo → " + out);
        } catch (IOException e) {
            deleteQuietly(tmp);
            throw new UncheckedIOException("no se pudo publicar la salida: " + out, e);
        } catch (RuntimeException e) {
            deleteQuietly(tmp);
            throw e;
        }
    }

    private static Config buildConfig(Map<String, String> o) {
        Config d = Config.defaults();
        try {
            return new Config(
                    intOpt(o, "L", d.latticeLength()),
                    intOpt(o, "ell", d.vehicleLength()),
                    doubleOpt(o, "dx", d.cellSizeMm()),
                    doubleOpt(o, "dt", d.timeStepS()),
                    intOpt(o, "n", d.n()),
                    doubleOpt(o, "p", d.brakeProb()),
                    doubleOpt(o, "vfree-min", d.freeSpeedMinMmS()),
                    doubleOpt(o, "vfree-max", d.freeSpeedMaxMmS()),
                    ruleOpt(o, d.collisionRule()),
                    orderOpt(o, d.insertionOrder()),
                    protocolOpt(o, d.protocol()),
                    longOpt(o, "seed", d.seed()),
                    intOpt(o, "steps", d.steps()),
                    intOpt(o, "transient", d.transientSteps()),
                    intOpt(o, "output-every", d.outputEvery())
            );
        } catch (NumberFormatException e) {
            throw new UsageException("valor numérico inválido: " + e.getMessage());
        } catch (IllegalArgumentException e) {
            throw new UsageException(e.getMessage());
        }
    }

    // --- parser mínimo de --clave valor (y --flag) ---

    private static Map<String, String> parse(String[] args) {
        Map<String, String> m = new HashMap<>();
        for (int i = 0; i < args.length; i++) {
            String a = args[i];
            if (a.startsWith("--")) a = a.substring(2);
            else if (a.startsWith("-")) a = a.substring(1);
            else continue;
            if (!ALL_OPTIONS.contains(a)) throw new UsageException("opción desconocida: --" + a);
            if (FLAG_OPTIONS.contains(a)) {
                m.put(a, "true");
            } else {
                if (i + 1 >= args.length) throw new UsageException("falta valor para --" + a);
                m.put(a, args[++i]);
            }
        }
        return m;
    }

    private static CollisionRuleType ruleOpt(Map<String, String> o, CollisionRuleType def) {
        if (!o.containsKey("rule")) return def;
        try {
            return CollisionRuleType.valueOf(o.get("rule"));
        } catch (IllegalArgumentException e) {
            throw new UsageException("regla inválida: " + o.get("rule"));
        }
    }

    private static InsertionOrder orderOpt(Map<String, String> o, InsertionOrder def) {
        if (!o.containsKey("order")) return def;
        try {
            return InsertionOrder.valueOf(o.get("order"));
        } catch (IllegalArgumentException e) {
            throw new UsageException("orden inválido: " + o.get("order"));
        }
    }

    private static RunProtocol protocolOpt(Map<String, String> o, RunProtocol def) {
        if (!o.containsKey("protocol")) return def;
        try {
            return RunProtocol.valueOf(o.get("protocol"));
        } catch (IllegalArgumentException e) {
            throw new UsageException("protocolo inválido: " + o.get("protocol"));
        }
    }

    private static int intOpt(Map<String, String> o, String k, int def) {
        return o.containsKey(k) ? Integer.parseInt(o.get(k)) : def;
    }

    private static long longOpt(Map<String, String> o, String k, long def) {
        return o.containsKey(k) ? Long.parseLong(o.get(k)) : def;
    }

    private static double doubleOpt(Map<String, String> o, String k, double def) {
        return o.containsKey(k) ? Double.parseDouble(o.get(k)) : def;
    }

    private static Path tempOutputPath(Path out) {
        Path name = out.getFileName();
        String tmpName = "." + (name == null ? "salida" : name) + ".tmp";
        return out.resolveSibling(tmpName);
    }

    private static void deleteQuietly(Path p) {
        try {
            Files.deleteIfExists(p);
        } catch (IOException ignored) {
            // Si falla la limpieza del temporal, el error original sigue siendo el relevante.
        }
    }

    private static void printUsage(PrintStream out) {
        out.println("""
            NaSch-VDV — motor de Nagel-Schreckenberg (R2 de contacto) para vibration-driven vehicles

            Uso:
              java -jar nasch-vdv.jar [opciones]

            Opciones (con sus valores por defecto, ver Config.defaults()):
              --n <int>            cantidad de vehículos N            (10)
              --p <double>         prob. de frenado aleatorio         (0.1)
              --rule <tipo>        CONTACTO_PURO | CLASICA_SALVO_CERO  (CLASICA_SALVO_CERO)
              --order <tipo>       ASCENDING | DESCENDING | RANDOM    (RANDOM)
              --protocol <tipo>    FIXED_N | INCREMENTAL_180S         (FIXED_N)
              --seed <long>        identificador reproducible de realización (1)
              --steps <int>        pasos de simulación                (10000)
              --output-every <int> escribir cada k pasos              (1)
              --out <path>         archivo de salida                  (../data/salida.txt)

              Calibración (normalmente no se tocan):
              --L <int>            celdas de la ruta periódica        (5280)
              --ell <int>          largo del vehículo en celdas       (176)
              --dx <double>        Δx [mm]                            (0.25)
              --dt <double>        dt [s]                             (0.041666...)
              --vfree-min <double> velocidad libre mínima [mm/s]      (90)
              --vfree-max <double> velocidad libre máxima [mm/s]      (120)

              -h, --help           esta ayuda
            """);
    }

    private static final class UsageException extends RuntimeException {
        private UsageException(String message) {
            super(message);
        }
    }

    private Main() { }
}
