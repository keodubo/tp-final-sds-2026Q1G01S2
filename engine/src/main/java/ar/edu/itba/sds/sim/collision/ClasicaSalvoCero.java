package ar.edu.itba.sds.sim.collision;

import java.util.ArrayList;
import java.util.List;

/**
 * Variante B — «clásica salvo a distancia 0».
 *
 * <p>Es la Regla 2 clásica anticipatoria de NaSch, con una sola excepción: un vehículo que ya está a
 * contacto no queda clavado en 0, sino que avanza con su líder.
 * <ul>
 *   <li>si {@code hueco > 0}: {@code desplazamiento = min(deseada, hueco)} (clásica, nunca alcanza al
 *       líder, así que no hace falta acoplar con su avance);</li>
 *   <li>si {@code hueco == 0} (a contacto): {@code desplazamiento = min(deseada, despl_lider)} — toma
 *       la velocidad del líder, acotada por su propia velocidad deseada, para moverse pegado sin
 *       solaparse.</li>
 * </ul>
 * En esta variante la velocidad heredada coincide siempre con el desplazamiento (no hay distinción
 * como en contacto puro). El caso a contacto se resuelve de adelante hacia atrás (los huecos cero
 * forman cadenas cuyo cabeza tiene hueco {@code > 0}); una ruta totalmente llena (todos los huecos en
 * cero) queda detenida, como en el NaSch clásico.
 *
 * <p>Con {@code p = 0} y configuración homogénea reproduce el diagrama fundamental analítico
 * {@code Q(ρ) = min(ρ·vmax, 1−ρ)} (Hito 3).
 */
public final class ClasicaSalvoCero implements CollisionRule {

    @Override
    public List<Movimiento> resolve(CollisionContext context) {
        int n = context.size();
        List<Integer> gap = context.gapsAhead();
        List<Integer> desired = context.desiredVelocities();

        // Caso base clásico: nunca se pasa del hueco (a contacto queda en 0 hasta relajar).
        int[] disp = new int[n];
        for (int i = 0; i < n; i++) {
            disp[i] = Math.min(desired.get(i), gap.get(i));
        }

        // Relajación de los vehículos a contacto: avanzan con su líder (de adelante hacia atrás).
        // Basta con n pasadas para propagar la información a lo largo de cualquier cadena.
        for (int iter = 0; iter < n; iter++) {
            boolean cambio = false;
            for (int i = 0; i < n; i++) {
                if (gap.get(i) == 0) {
                    int lider = (i + 1) % n;
                    int nuevo = Math.min(desired.get(i), disp[lider]);
                    if (nuevo != disp[i]) {
                        disp[i] = nuevo;
                        cambio = true;
                    }
                }
            }
            if (!cambio) break;
        }

        List<Movimiento> resultado = new ArrayList<>(n);
        for (int i = 0; i < n; i++) {
            resultado.add(new Movimiento(disp[i], disp[i]));
        }
        return resultado;
    }
}
