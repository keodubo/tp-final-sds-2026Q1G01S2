package ar.edu.itba.sds.sim.collision;

import java.util.List;

/**
 * Variante A — «contacto puro» (primaria; es la que modela el mecanismo del experimento).
 *
 * <p>Sin anticipación: un vehículo mantiene su velocidad mientras no alcance al de adelante.
 * <ul>
 *   <li>si {@code v ≤ gapAhead} → avanza libre (no se toca la velocidad);</li>
 *   <li>si {@code v > gapAhead} → colisión: el cierre a contacto se resuelve por <b>desplazamientos
 *       finales</b> compatibles con el del líder (el seguidor avanza hasta quedar pegado) y el
 *       seguidor <b>hereda</b> la velocidad del líder para el paso siguiente. No alcanza con mutar
 *       parcialmente la velocidad del seguidor (la frase informal "toma v_lider" no garantiza el
 *       cierre a contacto tras R4).</li>
 * </ul>
 * Los vehículos en contacto forman agrupamientos que se mueven a la velocidad del que va al frente;
 * en una ruta totalmente llena, todos a la mínima. La resolución de agrupamientos (orden de recorrido de la
 * ruta, manejo del caso totalmente trabado y compatibilidad con R3) se fija con TDD después de
 * confirmar la semántica con el profesor.
 *
 * <p>TODO (Hito 4 — TDD): implementar. Tests de invariantes: sin solapamiento, N conservado y orden
 * periódico preservado. El efecto «la velocidad de saturación es menor que la del más lento» del
 * artículo requiere p>0 (stop-and-go): con p=0 el agrupamiento va exactamente a la del más lento, así
 * que va como fenómeno a observar/discutir, no como invariante duro por paso.
 */
public final class ContactoPuro implements CollisionRule {
    @Override
    public List<Movimiento> resolve(CollisionContext context) {
        throw new UnsupportedOperationException("TODO Hito 4: implementar Regla 2 de contacto puro con TDD");
    }
}
