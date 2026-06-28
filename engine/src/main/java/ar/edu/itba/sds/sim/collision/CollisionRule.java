package ar.edu.itba.sds.sim.collision;

import java.util.List;

/**
 * Regla 2 (resolución de colisión). Recibe un snapshot de gaps y velocidades, y devuelve las
 * velocidades/desplazamientos propuestos por R2 para todos los vehículos. No muta la ruta.
 *
 * <p>Esta forma evita que la actualización síncrona dependa del orden de iteración. La interacción
 * fina entre R2 de contacto puro y R3 sigue marcada como decisión abierta en el diseño: antes de
 * implementar hay que confirmar si R3 se aplica después de R2, antes de la proyección de contactos,
 * o de forma común por agrupamiento.
 */
public interface CollisionRule {
    List<Integer> resolve(CollisionContext context);
}
