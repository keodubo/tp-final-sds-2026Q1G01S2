package ar.edu.itba.sds.config;

/**
 * Variantes de la Regla 2 (resolución de colisión) del modelo. Ver el documento de diseño.
 */
public enum CollisionRuleType {
    /** Contacto puro (primaria): sin anticipación; toma la velocidad del líder al alcanzarlo. */
    CONTACTO_PURO,
    /** Clásica salvo a distancia 0: v ← min(v, gap), pero si gap=0 toma la velocidad del líder. */
    CLASICA_SALVO_CERO
}
