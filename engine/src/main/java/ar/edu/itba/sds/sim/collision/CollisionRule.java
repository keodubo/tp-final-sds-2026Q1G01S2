package ar.edu.itba.sds.sim.collision;

import java.util.List;

/**
 * Regla 2 (resolución de colisión). Recibe un snapshot inmutable ({@link CollisionContext}) con los
 * huecos y la <b>velocidad deseada</b> de cada vehículo (la que querría avanzar este paso, ya pasada
 * por R1 y R3) y devuelve, por vehículo, un {@link Movimiento}: cuánto avanza efectivamente este paso
 * y con qué velocidad entra al siguiente. No muta la ruta.
 *
 * <p>Operar sobre un snapshot evita que la actualización síncrona dependa del orden de iteración: el
 * resultado es función pura de {@code (huecos, velocidades deseadas)}. La regla es responsable de
 * garantizar que los desplazamientos <b>no produzcan solapamiento</b>
 * ({@code desplazamiento_i ≤ hueco_i + desplazamiento_lider_i}) resolviendo los agrupamientos de
 * adelante hacia atrás.
 *
 * <p>El contrato devuelve {@code Movimiento} (y no un único entero) porque la variante de contacto
 * puro necesita distinguir el desplazamiento de la velocidad heredada del líder (ver
 * {@link Movimiento} y {@link ContactoPuro}).
 */
public interface CollisionRule {

    /**
     * Resuelve la Regla 2 para todos los vehículos.
     *
     * @return lista de tamaño {@code N} alineada por índice con los vehículos del contexto.
     */
    List<Movimiento> resolve(CollisionContext context);
}
