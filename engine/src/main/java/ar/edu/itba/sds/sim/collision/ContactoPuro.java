package ar.edu.itba.sds.sim.collision;

import java.util.ArrayList;
import java.util.List;

/**
 * Variante A — «contacto puro» (primaria; modela el mecanismo del experimento de VDV).
 *
 * <p>Sin anticipación: un vehículo avanza a su velocidad deseada mientras no choque con el de
 * adelante. Como la actualización es síncrona, el líder también se mueve en el mismo paso, así que el
 * tope real de avance del seguidor es {@code hueco_i + desplazamiento_lider}:
 * <ul>
 *   <li>si {@code deseada_i ≤ hueco_i + despl_lider}: avanza libre a su velocidad deseada (le queda
 *       hueco por delante);</li>
 *   <li>si {@code deseada_i > hueco_i + despl_lider}: <b>colisión</b>. Avanza solo hasta quedar a
 *       contacto ({@code despl_i = hueco_i + despl_lider}, hueco resultante 0) y <b>hereda</b> la
 *       velocidad del líder para el paso siguiente.</li>
 * </ul>
 *
 * <p><b>Resolución por agrupamientos.</b> Los desplazamientos se resuelven con la relajación
 * {@code despl_i = min(deseada_i, hueco_i + despl_lider)} hasta el punto fijo (mayor punto fijo ≤
 * deseada): cada vehículo avanza lo máximo posible sin atravesar a su líder. La velocidad heredada se
 * propaga de adelante hacia atrás dentro de cada agrupamiento: la cabeza (la que quedó con hueco
 * {@code > 0}) conserva su velocidad deseada y los de atrás, a contacto, heredan la del de adelante.
 * Una ruta totalmente llena (a contacto) avanza rígidamente a la velocidad del más lento.
 *
 * <p>Garantía de no-solapamiento: por construcción {@code despl_i ≤ hueco_i + despl_lider}, así que el
 * hueco resultante {@code = hueco_i + despl_lider − despl_i ≥ 0} y la suma de huecos se conserva.
 */
public final class ContactoPuro implements CollisionRule {

    @Override
    public List<Movimiento> resolve(CollisionContext context) {
        int n = context.size();
        List<Integer> gap = context.gapsAhead();
        List<Integer> desired = context.desiredVelocities();

        // Relajación de desplazamientos: arranca en la velocidad deseada y baja al mayor punto fijo.
        int[] disp = new int[n];
        for (int i = 0; i < n; i++) disp[i] = desired.get(i);
        for (int iter = 0; iter <= n; iter++) {
            boolean cambio = false;
            for (int i = 0; i < n; i++) {
                int lider = (i + 1) % n;
                int tope = gap.get(i) + disp[lider];
                int nuevo = Math.min(desired.get(i), tope);
                if (nuevo != disp[i]) {
                    disp[i] = nuevo;
                    cambio = true;
                }
            }
            if (!cambio) break;
        }

        // Hueco resultante de cada vehículo tras mover (>= 0). Hueco 0 ⇒ quedó a contacto.
        int[] huecoResultante = new int[n];
        for (int i = 0; i < n; i++) {
            int lider = (i + 1) % n;
            huecoResultante[i] = gap.get(i) + disp[lider] - disp[i];
        }

        // Velocidad heredada: la cabeza del agrupamiento mantiene su deseada; los de atrás heredan.
        int[] velSiguiente = new int[n];
        int cabeza = -1;
        for (int i = 0; i < n; i++) {
            if (huecoResultante[i] > 0) {
                cabeza = i;
                break;
            }
        }
        if (cabeza < 0) {
            // Ruta totalmente a contacto (ρ=1): todos llevan el desplazamiento común.
            for (int i = 0; i < n; i++) velSiguiente[i] = disp[i];
        } else {
            // De adelante hacia atrás a partir de una cabeza: el líder ya está resuelto.
            for (int s = 0; s < n; s++) {
                int i = Math.floorMod(cabeza - s, n);
                if (huecoResultante[i] > 0) {
                    velSiguiente[i] = desired.get(i);
                } else {
                    velSiguiente[i] = velSiguiente[(i + 1) % n];
                }
            }
        }

        List<Movimiento> resultado = new ArrayList<>(n);
        for (int i = 0; i < n; i++) {
            resultado.add(new Movimiento(disp[i], velSiguiente[i]));
        }
        return resultado;
    }
}
