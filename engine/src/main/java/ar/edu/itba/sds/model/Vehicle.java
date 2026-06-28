package ar.edu.itba.sds.model;

/**
 * Estado puro de un vehículo en el lattice. Posición = celda de la <b>cola</b>; el cuerpo ocupa
 * {@code [position, position + ℓ - 1]} (módulo L). Velocidad en celdas/paso, acotada por {@code vMax}.
 */
public final class Vehicle {

    private final int id;
    private final int vMax;   // velocidad máxima propia (heterogénea) [celdas/paso]
    private int position;     // celda de cola [0, L)
    private int velocity;     // [celdas/paso]

    public Vehicle(int id, int position, int velocity, int vMax) {
        this.id = id;
        this.position = position;
        this.velocity = velocity;
        this.vMax = vMax;
    }

    public int id() { return id; }
    public int vMax() { return vMax; }
    public int position() { return position; }
    public int velocity() { return velocity; }

    public void setPosition(int position) { this.position = position; }
    public void setVelocity(int velocity) { this.velocity = velocity; }

    @Override
    public String toString() {
        return "Vehicle[id=" + id + ", pos=" + position + ", v=" + velocity + ", vMax=" + vMax + "]";
    }
}
