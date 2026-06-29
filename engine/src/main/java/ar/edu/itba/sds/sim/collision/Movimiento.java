package ar.edu.itba.sds.sim.collision;

/**
 * Resultado de la Regla 2 para <b>un</b> vehículo en un paso. Un único entero no alcanza para la
 * variante de contacto puro: hace falta separar lo que el vehículo <b>avanza este paso</b> de la
 * <b>velocidad que hereda para el paso siguiente</b>.
 *
 * <ul>
 *   <li>{@code desplazamiento}: celdas que el vehículo efectivamente avanza este paso (lo que aplica
 *       R4, ya garantizado sin solapamiento). Es la velocidad observable del cuadro
 *       ({@code desplazamiento·Δv}).</li>
 *   <li>{@code velocidadSiguiente}: velocidad (celdas/paso) con la que el vehículo entra al próximo
 *       paso, es decir la base de R1 (acelerar) del paso que viene. En la variante de contacto puro,
 *       cuando un vehículo queda a contacto, hereda la velocidad del líder; en la variante clásica
 *       coincide siempre con {@code desplazamiento}.</li>
 * </ul>
 *
 * <p>Esta separación es lo que permite que un agrupamiento avance a la velocidad del que va al frente
 * sin que los de atrás lo atraviesen ni se solapen.
 */
public record Movimiento(int desplazamiento, int velocidadSiguiente) {

    public Movimiento {
        if (desplazamiento < 0) throw new IllegalArgumentException("desplazamiento debe ser >= 0");
        if (velocidadSiguiente < 0) throw new IllegalArgumentException("velocidadSiguiente debe ser >= 0");
    }
}
