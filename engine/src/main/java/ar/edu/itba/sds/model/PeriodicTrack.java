package ar.edu.itba.sds.model;

import java.util.Collections;
import java.util.List;

/**
 * Ruta unidimensional con <b>condiciones periódicas</b>: una línea de {@code latticeLength} celdas
 * donde lo que sale por un extremo reentra por el otro (no es un círculo físico; la curvatura no
 * entra en el modelo). Los vehículos son extendidos, de {@code vehicleLength} celdas, y se mantienen
 * <b>ordenados de forma periódica</b> por posición (índice {@code i+1} = líder de {@code i}; el
 * último tiene como líder al primero, por la envoltura).
 *
 * <p>Geometría pura (gaps, vecinos): es determinista y está implementada y testeada. La dinámica
 * (R1–R4) vive en el motor.
 */
public final class PeriodicTrack {

    private final int latticeLength;   // L
    private final int vehicleLength;   // ℓ
    private final List<Vehicle> vehicles; // ordenados periódicamente por posición

    public PeriodicTrack(int latticeLength, int vehicleLength, List<Vehicle> vehicles) {
        this.latticeLength = latticeLength;
        this.vehicleLength = vehicleLength;
        this.vehicles = vehicles;
    }

    public int latticeLength() { return latticeLength; }
    public int vehicleLength() { return vehicleLength; }
    public int size() { return vehicles.size(); }
    public Vehicle get(int i) { return vehicles.get(i); }
    public List<Vehicle> vehicles() { return Collections.unmodifiableList(vehicles); }

    /** Líder de {@code i} (el de adelante), con envoltura periódica. */
    public Vehicle leader(int i) {
        return vehicles.get(Math.floorMod(i + 1, vehicles.size()));
    }

    /** Seguidor de {@code i} (el de atrás), con envoltura periódica. */
    public Vehicle follower(int i) {
        return vehicles.get(Math.floorMod(i - 1, vehicles.size()));
    }

    /**
     * Celdas libres entre el frente de {@code i} y la cola de su líder (a contacto = 0). La resta
     * se toma módulo L para contemplar el par que cruza el extremo de la línea.
     */
    public int gapAhead(int i) {
        Vehicle v = vehicles.get(i);
        Vehicle lead = leader(i);
        return Math.floorMod(lead.position() - v.position() - vehicleLength, latticeLength);
    }

    /**
     * Gap al vecino más cercano (mínimo entre el de adelante y el de atrás). Se usa para la
     * densidad individual {@code ρ_i} (ver observables).
     */
    public int nearestGap(int i) {
        int ahead = gapAhead(i);
        int behind = gapAhead(Math.floorMod(i - 1, vehicles.size())); // gap delante del seguidor
        return Math.min(ahead, behind);
    }

    /**
     * Verifica los invariantes geométricos: cada gap ≥ 0 y la suma de huecos más los cuerpos cubre
     * exactamente la línea (no hay solapamiento ni inconsistencia). Lo usan los tests.
     */
    public boolean isConsistent() {
        long occupied = (long) vehicles.size() * vehicleLength;
        long gaps = 0;
        for (int i = 0; i < vehicles.size(); i++) {
            int g = gapAhead(i);
            if (g < 0) return false;
            gaps += g;
        }
        return occupied + gaps == latticeLength;
    }
}
