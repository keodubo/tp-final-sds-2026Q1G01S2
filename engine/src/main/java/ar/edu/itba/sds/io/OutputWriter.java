package ar.edu.itba.sds.io;

import ar.edu.itba.sds.config.Config;
import ar.edu.itba.sds.model.PeriodicTrack;
import ar.edu.itba.sds.model.Vehicle;

import java.io.BufferedWriter;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Locale;

/**
 * Escribe el estado del motor en formato de texto, en <b>unidades físicas</b> (mm, mm/s) — la
 * cátedra exige que la salida tenga solo variables físicas del modelo (id, posición, velocidad);
 * sin color ni radio. El color para las animaciones se deriva después, en el análisis.
 *
 * <p>Formato (fácil de cargar con numpy): una cabecera con los parámetros (líneas con {@code #})
 * y luego filas {@code paso  id  x_mm  v_mmps}. La posición es la celda de cola del vehículo.
 */
public final class OutputWriter implements AutoCloseable {

    private final BufferedWriter out;
    private final double cellSizeMm;          // Δx
    private final double velocityQuantumMmS;  // Δv

    public OutputWriter(Path file, Config config) {
        try {
            if (file.getParent() != null) Files.createDirectories(file.getParent());
            this.out = Files.newBufferedWriter(file);
        } catch (IOException e) {
            throw new UncheckedIOException("no se pudo abrir la salida: " + file, e);
        }
        this.cellSizeMm = config.cellSizeMm();
        this.velocityQuantumMmS = config.velocityQuantumMmS();
        writeHeader(config);
    }

    private void writeHeader(Config c) {
        line("# modelo=Nagel-Schreckenberg-VDV regla2=" + c.collisionRule());
        line(String.format(Locale.US,
                "# L_celdas=%d ell_celdas=%d dx_mm=%.6f dt_s=%.6f dv_mmps=%.6f",
                c.latticeLength(), c.vehicleLength(), c.cellSizeMm(), c.timeStepS(), c.velocityQuantumMmS()));
        line(String.format(Locale.US,
                "# N=%d p=%.6f vfree_min_mmps=%.3f vfree_max_mmps=%.3f order=%s protocol=%s realizacion_id=%d steps=%d transient_steps=%d output_every=%d",
                c.n(), c.brakeProb(), c.freeSpeedMinMmS(), c.freeSpeedMaxMmS(), c.insertionOrder(),
                c.protocol(), c.seed(), c.steps(), c.transientSteps(), c.outputEvery()));
        line("# columnas: paso id x_mm v_mmps");
    }

    /** Escribe el estado de la ruta en el paso indicado. */
    public void writeStep(int step, PeriodicTrack track) {
        for (int i = 0; i < track.size(); i++) {
            Vehicle v = track.get(i);
            line(String.format(Locale.US, "%d %d %.4f %.4f",
                    step, v.id(), v.position() * cellSizeMm, v.velocity() * velocityQuantumMmS));
        }
    }

    private void line(String s) {
        try {
            out.write(s);
            out.newLine();
        } catch (IOException e) {
            throw new UncheckedIOException("error escribiendo la salida", e);
        }
    }

    @Override
    public void close() {
        try {
            out.close();
        } catch (IOException e) {
            throw new UncheckedIOException("error cerrando la salida", e);
        }
    }
}
