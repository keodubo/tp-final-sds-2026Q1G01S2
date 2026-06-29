package ar.edu.itba.sds.sim.collision;

import ar.edu.itba.sds.model.PeriodicTrack;
import ar.edu.itba.sds.model.Vehicle;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

class CollisionContextTest {

    @Test
    void capturaSnapshotsInmutablesParaResolverR2SinDependerDelOrdenDeIteracion() {
        Vehicle follower = new Vehicle(0, 0, 1, 5);
        Vehicle leader = new Vehicle(1, 8, 4, 5);
        PeriodicTrack track = new PeriodicTrack(20, 4, List.of(follower, leader));
        List<Integer> desired = new ArrayList<>(List.of(2, 5));

        CollisionContext context = CollisionContext.from(track, desired);

        // Mutar las fuentes después de construir no debe afectar el snapshot.
        desired.set(0, 99);
        follower.setVelocity(99);
        follower.setPosition(15);

        assertEquals(List.of(4, 8), context.gapsAhead());
        assertEquals(List.of(2, 5), context.desiredVelocities());
        assertThrows(UnsupportedOperationException.class, () -> context.desiredVelocities().set(0, 3));
        assertThrows(UnsupportedOperationException.class, () -> context.gapsAhead().set(0, 3));
    }

    @Test
    void rechazaSnapshotsDeTamanioInconsistente() {
        assertThrows(IllegalArgumentException.class,
                () -> new CollisionContext(20, 4, List.of(4, 8), List.of(2)));
    }
}
