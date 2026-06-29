package ar.edu.itba.sds.sim;

import ar.edu.itba.sds.config.Config;
import ar.edu.itba.sds.config.RunProtocol;
import ar.edu.itba.sds.model.PeriodicTrack;
import ar.edu.itba.sds.model.Vehicle;
import ar.edu.itba.sds.sim.collision.ClasicaSalvoCero;
import ar.edu.itba.sds.sim.collision.CollisionContext;
import ar.edu.itba.sds.sim.collision.CollisionRule;
import ar.edu.itba.sds.sim.collision.ContactoPuro;
import ar.edu.itba.sds.sim.collision.Movimiento;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Random;

/**
 * Motor de Nagel-Schreckenberg con la Regla 2 modificada. Actualización síncrona por paso de
 * tiempo. Es 100 % determinista dado el identificador reproducible de la realización (condiciones
 * iniciales + secuencia del PRNG): toda la aleatoriedad sale de un único {@link Random} sembrado con
 * {@link Config#seed()}.
 *
 * <h2>Orden de las reglas y garantía de no-solapamiento</h2>
 * El esquema lógico es R1 → R2 → R3 → R4, pero por el requisito de la cátedra de
 * <b>colisiones reproducibles y sin solapamiento jamás</b> el motor aplica:
 * <ol>
 *   <li><b>R1</b> aceleración sobre la velocidad heredada: {@code deseada = min(v_heredada + 1, vMax)};</li>
 *   <li><b>R3</b> frenado aleatorio sobre la velocidad deseada: con prob {@code p},
 *       {@code deseada = max(0, deseada - 1)};</li>
 *   <li><b>R2</b> proyección de contactos: la {@link CollisionRule} toma los huecos y las velocidades
 *       deseadas (ya frenadas) y devuelve, por vehículo, el desplazamiento real (acotado para no
 *       solaparse, resolviendo agrupamientos de adelante hacia atrás) y la velocidad heredada del
 *       paso siguiente;</li>
 *   <li><b>R4</b> movimiento: {@code x ← (x + desplazamiento) mod L}.</li>
 * </ol>
 * Se aplica <b>R3 antes</b> de la proyección de contactos a propósito: el frenado solo puede
 * <i>reducir</i> el avance, así que proyectar después garantiza que nunca aparezca un solapamiento
 * que el frenado no podía prever. Con {@code p = 0} este orden es idéntico al NaSch canónico
 * (R3 nunca se aplica), por lo que la validación analítica no se ve afectada.
 *
 * <h2>Velocidad registrada vs. velocidad heredada</h2>
 * El motor guarda en {@link Vehicle#velocity()} el <b>desplazamiento</b> efectivo del paso (la
 * velocidad observable del cuadro, {@code desplazamiento·Δv}, lo que mediría la cámara por diferencia
 * de posiciones). La velocidad <b>heredada</b> que alimenta R1 del paso siguiente se guarda aparte
 * (indexada por id de vehículo). En la variante clásica ambas coinciden; en contacto puro difieren
 * solo en el cuadro en que un vehículo queda a contacto (avanza hasta el líder pero hereda su
 * velocidad).
 */
public final class NaSchEngine {

    private static final double SEGUNDOS_POR_LOTE_INCREMENTAL = 180.0;
    private static final int VEHICULOS_POR_LOTE_INCREMENTAL = 5;

    private final Config config;
    private final Random rng;
    private final CollisionRule collisionRule;
    private final RandomBrake brake;

    private PeriodicTrack track;
    /** Velocidad heredada por vehículo (entrada de R1 del próximo paso), indexada por id. */
    private int[] carriedVelocity;

    // --- Estado del protocolo incremental ---
    private List<EspecieVehiculo> pendientes; // vehículos aún no insertados (en orden de inserción)
    private int proximoPaso;                   // contador de pasos ya ejecutados
    private int pasosPorLote;                  // 180 s / dt

    public NaSchEngine(Config config) {
        this.config = config;
        this.rng = new Random(config.seed());
        this.collisionRule = ruleFor(config);
        this.brake = new RandomBrake(rng);
    }

    private static CollisionRule ruleFor(Config config) {
        return switch (config.collisionRule()) {
            case CONTACTO_PURO -> new ContactoPuro();
            case CLASICA_SALVO_CERO -> new ClasicaSalvoCero();
        };
    }

    /** Estado actual de la ruta (null antes de {@link #initialize()}). */
    public PeriodicTrack track() {
        return track;
    }

    public Config config() {
        return config;
    }

    /**
     * Construye el estado inicial según el protocolo:
     * <ul>
     *   <li>{@code FIXED_N}: ubica los {@code N} vehículos sin solapar, con posiciones de cola
     *       sorteadas (composición aleatoria del espacio libre en {@code N} huecos) y velocidad
     *       inicial 0;</li>
     *   <li>{@code INCREMENTAL_180S}: ubica el primer lote (5, o {@code N} si {@code N < 5}) y deja
     *       el resto en cola para insertarlos en huecos libres cada 180 s (ver {@link #step()}).</li>
     * </ul>
     * En todos los casos la velocidad libre de cada vehículo se sortea en
     * {@code [freeSpeedMin, freeSpeedMax]} y se mapea a {@code vMax_i = round(vfree_i / Δv)}.
     */
    public void initialize() {
        this.proximoPaso = 0;
        this.pasosPorLote = (int) Math.round(SEGUNDOS_POR_LOTE_INCREMENTAL / config.timeStepS());
        this.carriedVelocity = new int[config.n()];

        List<EspecieVehiculo> todos = ordenarPorInsercion(generarEspecies(config.n()));

        int inicial = switch (config.protocol()) {
            case FIXED_N -> config.n();
            case INCREMENTAL_180S -> Math.min(VEHICULOS_POR_LOTE_INCREMENTAL, config.n());
        };

        List<EspecieVehiculo> lote = new ArrayList<>(todos.subList(0, inicial));
        this.pendientes = new ArrayList<>(todos.subList(inicial, todos.size()));
        this.track = ubicarPorComposicion(lote);
    }

    /**
     * Condición inicial <b>determinista y uniforme</b> (huecos lo más parejos posible, sin sorteo de
     * posiciones). Es la que se usa para la validación analítica {@code p = 0}: con huecos iguales y
     * vmax homogéneo el estado estacionario es exactamente {@code v̄ = min(vmax, hueco)}.
     */
    public void initializeEvenlySpread() {
        this.proximoPaso = 0;
        this.pasosPorLote = (int) Math.round(SEGUNDOS_POR_LOTE_INCREMENTAL / config.timeStepS());
        this.carriedVelocity = new int[config.n()];
        this.pendientes = new ArrayList<>();

        List<EspecieVehiculo> especies = generarEspecies(config.n());

        int n = config.n();
        int ell = config.vehicleLength();
        int libre = config.latticeLength() - n * ell;
        int base = libre / n;
        int resto = libre % n;

        List<Vehicle> vehiculos = new ArrayList<>(n);
        int pos = 0;
        for (int k = 0; k < n; k++) {
            EspecieVehiculo e = especies.get(k);
            vehiculos.add(new Vehicle(e.id(), Math.floorMod(pos, config.latticeLength()), 0, e.vMax()));
            int hueco = base + (k < resto ? 1 : 0);
            pos += ell + hueco;
        }
        this.track = new PeriodicTrack(config.latticeLength(), ell, vehiculos);
    }

    /**
     * Avanza un paso de tiempo (actualización síncrona R1 → R3 → R2 → R4; ver la documentación de la
     * clase). Lee la velocidad heredada de cada vehículo, acelera (R1), frena al azar (R3), proyecta
     * los desplazamientos contra los huecos para no solapar (R2 vía {@link CollisionRule}) y mueve
     * (R4). Guarda en cada vehículo el desplazamiento del cuadro y registra aparte la velocidad
     * heredada para el próximo paso.
     */
    public void step() {
        if (track == null) throw new IllegalStateException("hay que llamar initialize() antes de step()");

        // Protocolo incremental: insertar el próximo lote si toca este paso.
        insertarLoteSiCorresponde();

        int n = track.size();
        int L = config.latticeLength();
        double p = config.brakeProb();

        // R1 (acelerar) + R3 (frenar) → velocidad deseada de cada vehículo.
        List<Integer> deseadas = new ArrayList<>(n);
        for (int i = 0; i < n; i++) {
            Vehicle v = track.get(i);
            int deseada = Math.min(carriedVelocity[v.id()] + 1, v.vMax()); // R1
            if (brake.brakes(p)) {                                          // R3
                deseada = Math.max(0, deseada - 1);
            }
            deseadas.add(deseada);
        }

        // R2 (proyección de contactos sobre el snapshot, sin solapamiento).
        CollisionContext ctx = CollisionContext.from(track, deseadas);
        List<Movimiento> movimientos = collisionRule.resolve(ctx);

        // R4 (mover) + registrar velocidades.
        for (int i = 0; i < n; i++) {
            Vehicle v = track.get(i);
            Movimiento m = movimientos.get(i);
            v.setPosition(Math.floorMod(v.position() + m.desplazamiento(), L));
            v.setVelocity(m.desplazamiento());              // velocidad observable del cuadro
            carriedVelocity[v.id()] = m.velocidadSiguiente(); // base de R1 del próximo paso
        }

        proximoPaso++;
    }

    /** Inserta el próximo lote del protocolo incremental, si este paso es múltiplo del intervalo. */
    private void insertarLoteSiCorresponde() {
        if (config.protocol() != RunProtocol.INCREMENTAL_180S) return;
        if (pendientes.isEmpty()) return;
        if (proximoPaso == 0 || proximoPaso % pasosPorLote != 0) return;

        int aInsertar = Math.min(VEHICULOS_POR_LOTE_INCREMENTAL, pendientes.size());
        for (int k = 0; k < aInsertar; k++) {
            EspecieVehiculo e = pendientes.get(0);
            if (!insertarEnHueco(e)) break; // no hay hueco para más; se reintenta en el próximo lote
            pendientes.remove(0);
        }
    }

    /**
     * Inserta un vehículo nuevo (velocidad 0) en un hueco libre de tamaño {@code ≥ ℓ}, elegido al
     * azar, dejándolo en la posición cíclica correcta. Devuelve {@code false} si no hay ningún hueco
     * que lo aloje (ruta demasiado llena/fragmentada): limitación honesta del protocolo incremental
     * cerca de la saturación.
     */
    private boolean insertarEnHueco(EspecieVehiculo e) {
        int L = config.latticeLength();
        int ell = config.vehicleLength();
        int n = track.size();

        List<Integer> candidatos = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            if (track.gapAhead(i) >= ell) candidatos.add(i);
        }
        if (candidatos.isEmpty()) return false;

        int i = candidatos.get(rng.nextInt(candidatos.size()));
        int hueco = track.gapAhead(i);
        int offset = rng.nextInt(hueco - ell + 1);
        int nuevaPos = Math.floorMod(track.get(i).position() + ell + offset, L);

        List<Vehicle> vehiculos = new ArrayList<>(n + 1);
        for (int k = 0; k < n; k++) {
            vehiculos.add(track.get(k));
            if (k == i) vehiculos.add(new Vehicle(e.id(), nuevaPos, 0, e.vMax()));
        }
        this.track = new PeriodicTrack(L, ell, vehiculos);
        this.carriedVelocity[e.id()] = 0;
        return true;
    }

    // ------------------------------------------------------------------
    // Generación y ubicación de vehículos (condiciones iniciales)
    // ------------------------------------------------------------------

    /** Especificación inmutable de un vehículo a crear (id + velocidad máxima derivada de su vfree). */
    private record EspecieVehiculo(int id, double vFree, int vMax) { }

    /** Genera {@code count} vehículos con ids 0..count-1, sorteando vfree en orden de id. */
    private List<EspecieVehiculo> generarEspecies(int count) {
        double min = config.freeSpeedMinMmS();
        double max = config.freeSpeedMaxMmS();
        double dv = config.velocityQuantumMmS();
        List<EspecieVehiculo> especies = new ArrayList<>(count);
        for (int id = 0; id < count; id++) {
            double vFree = min + rng.nextDouble() * (max - min);
            int vMax = (int) Math.round(vFree / dv);
            especies.add(new EspecieVehiculo(id, vFree, vMax));
        }
        return especies;
    }

    /** Reordena los vehículos según el orden de inserción (por velocidad libre). */
    private List<EspecieVehiculo> ordenarPorInsercion(List<EspecieVehiculo> especies) {
        List<EspecieVehiculo> ordenadas = new ArrayList<>(especies);
        switch (config.insertionOrder()) {
            case ASCENDING -> ordenadas.sort(Comparator.comparingDouble(EspecieVehiculo::vFree));
            case DESCENDING -> ordenadas.sort(Comparator.comparingDouble(EspecieVehiculo::vFree).reversed());
            case RANDOM -> mezclar(ordenadas);
        }
        return ordenadas;
    }

    /** Mezcla determinista (Fisher-Yates) usando el PRNG de la realización. */
    private void mezclar(List<EspecieVehiculo> lista) {
        for (int i = lista.size() - 1; i > 0; i--) {
            int j = rng.nextInt(i + 1);
            EspecieVehiculo tmp = lista.get(i);
            lista.set(i, lista.get(j));
            lista.set(j, tmp);
        }
    }

    /**
     * Ubica un lote de vehículos en una ruta vacía repartiendo el espacio libre en huecos al azar
     * (composición multinomial) y con una rotación global aleatoria, sin solapar. Los vehículos
     * quedan en el orden recibido, que es el orden cíclico a lo largo de la ruta.
     */
    private PeriodicTrack ubicarPorComposicion(List<EspecieVehiculo> lote) {
        int count = lote.size();
        int L = config.latticeLength();
        int ell = config.vehicleLength();
        int libre = L - count * ell;

        int[] huecos = new int[count];
        for (int u = 0; u < libre; u++) {
            huecos[rng.nextInt(count)]++;
        }
        int offset = rng.nextInt(L);

        List<Vehicle> vehiculos = new ArrayList<>(count);
        int pos = offset;
        for (int k = 0; k < count; k++) {
            EspecieVehiculo e = lote.get(k);
            vehiculos.add(new Vehicle(e.id(), Math.floorMod(pos, L), 0, e.vMax()));
            pos += ell + huecos[k];
        }
        return new PeriodicTrack(L, ell, vehiculos);
    }
}
