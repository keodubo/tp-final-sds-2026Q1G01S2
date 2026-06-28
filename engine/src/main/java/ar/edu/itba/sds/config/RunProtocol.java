package ar.edu.itba.sds.config;

/** Protocolo experimental a representar con la corrida. */
public enum RunProtocol {
    /** Corridas independientes con N fijo; útil para validar el motor y barrer parámetros. */
    FIXED_N,
    /** Réplica del artículo: agregar 5 VDV cada 180 s hasta N=30. */
    INCREMENTAL_180S
}
