package ar.edu.itba.sds;

import ar.edu.itba.sds.config.CollisionRuleType;
import ar.edu.itba.sds.config.Config;
import ar.edu.itba.sds.io.OutputWriter;
import ar.edu.itba.sds.sim.NaSchEngine;

import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;

/**
 * Punto de entrada: corre UNA simulación (una realización) dada la configuración por línea de
 * comandos y escribe la salida física. El barrido de la matriz (N × p × variante × realizaciones)
 * lo orquesta el script de Python {@code analysis/run_matrix.py} invocando este jar.
 */
public final class Main {

    public static void main(String[] args) {
        Map<String, String> opts = parse(args);
        if (opts.containsKey("help") || opts.containsKey("h")) {
            printUsage();
            return;
        }

        Config cfg = buildConfig(opts);
        Path out = Path.of(opts.getOrDefault("out", "../data/salida.txt"));

        System.out.printf("NaSch-VDV | N=%d p=%.3f regla=%s semilla=%d pasos=%d%n",
                cfg.n(), cfg.brakeProb(), cfg.collisionRule(), cfg.seed(), cfg.steps());
        System.out.printf("calibración | Δx=%.3f mm dt=%.4f s Δv=%.3f mm/s L=%.1f mm ρ=%.5f 1/mm%n",
                cfg.cellSizeMm(), cfg.timeStepS(), cfg.velocityQuantumMmS(),
                cfg.trackLengthMm(), cfg.densityPerMm());

        NaSchEngine engine = new NaSchEngine(cfg);
        try (OutputWriter writer = new OutputWriter(out, cfg)) {
            engine.initialize();
            for (int t = 0; t < cfg.steps(); t++) {
                if (t % cfg.outputEvery() == 0) writer.writeStep(t, engine.track());
                engine.step();
            }
            System.out.println("listo → " + out);
        } catch (UnsupportedOperationException e) {
            System.err.println("[scaffold] motor aún no implementado: " + e.getMessage());
            System.err.println("Ver hitos en diseno-tp-final-vdv-nasch_v1.md");
            System.exit(2);
        }
    }

    private static Config buildConfig(Map<String, String> o) {
        Config d = Config.defaults();
        return new Config(
                intOpt(o, "L", d.latticeLength()),
                intOpt(o, "ell", d.vehicleLength()),
                doubleOpt(o, "dx", d.cellSizeMm()),
                doubleOpt(o, "dt", d.timeStepS()),
                intOpt(o, "n", d.n()),
                doubleOpt(o, "p", d.brakeProb()),
                doubleOpt(o, "vfree-min", d.freeSpeedMinMmS()),
                doubleOpt(o, "vfree-max", d.freeSpeedMaxMmS()),
                o.containsKey("rule") ? CollisionRuleType.valueOf(o.get("rule")) : d.collisionRule(),
                longOpt(o, "seed", d.seed()),
                intOpt(o, "steps", d.steps()),
                intOpt(o, "transient", d.transientSteps()),
                intOpt(o, "output-every", d.outputEvery())
        );
    }

    // --- parser mínimo de --clave valor (y --flag) ---

    private static Map<String, String> parse(String[] args) {
        Map<String, String> m = new HashMap<>();
        for (int i = 0; i < args.length; i++) {
            String a = args[i];
            if (a.startsWith("--")) a = a.substring(2);
            else if (a.startsWith("-")) a = a.substring(1);
            else continue;
            if (i + 1 < args.length && !args[i + 1].startsWith("-")) m.put(a, args[++i]);
            else m.put(a, "true");
        }
        return m;
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

    private static void printUsage() {
        System.out.println("""
            NaSch-VDV — motor de Nagel-Schreckenberg (R2 de contacto) para vibration-driven vehicles

            Uso:
              java -jar nasch-vdv.jar [opciones]

            Opciones (con sus valores por defecto, ver Config.defaults()):
              --n <int>            cantidad de vehículos N            (10)
              --p <double>         prob. de frenado aleatorio         (0.1)
              --rule <tipo>        CONTACTO_PURO | CLASICA_SALVO_CERO  (CONTACTO_PURO)
              --seed <long>        semilla (una realización)          (1)
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

    private Main() { }
}
