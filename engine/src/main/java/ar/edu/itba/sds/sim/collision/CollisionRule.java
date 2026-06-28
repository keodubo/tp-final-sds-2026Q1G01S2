package ar.edu.itba.sds.sim.collision;

import java.util.List;

/**
 * Regla 2 (resolución de colisión). Recibe un snapshot inmutable ({@link CollisionContext}) y devuelve,
 * por vehículo, las <b>celdas efectivas a avanzar en este paso</b> (lo que aplica R4). No muta la ruta.
 * Operar sobre un snapshot evita que la actualización síncrona dependa del orden de iteración.
 *
 * <p><b>Contrato PROVISORIO (esqueleto, sin implementaciones ni llamadores todavía).</b> Dos
 * decisiones abiertas con el profe pueden cambiar esta firma (ver diseño §11):
 * <ul>
 *   <li>la interacción R2/R3 (si R3 va después de R2, antes de la proyección de contactos, o por
 *       agrupamiento);</li>
 *   <li>la variante de <i>contacto puro</i>: cerrar a contacto exige, además del desplazamiento,
 *       la velocidad que el seguidor <i>hereda</i> del líder para el paso siguiente — un único
 *       {@code List<Integer>} puede no alcanzar. Cuando se confirme la semántica, esto migrará a un
 *       tipo nombrado (p. ej. un record con desplazamiento + velocidad heredada). Cambiarlo ahora es
 *       barato porque {@code step()} aún no lo invoca.</li>
 * </ul>
 */
public interface CollisionRule {
    List<Integer> resolve(CollisionContext context);
}
