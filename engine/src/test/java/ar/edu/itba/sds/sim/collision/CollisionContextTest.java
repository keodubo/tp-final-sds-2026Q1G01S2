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
        List<Integer> velocitiesAfterR1 = new ArrayList<>(List.of(2, 5));
        List<Integer> leaderVelocities = new ArrayList<>(List.of(4, 1));

        CollisionContext context = CollisionContext.from(track, velocitiesAfterR1, leaderVelocities);
        velocitiesAfterR1.set(0, 99);
        leaderVelocities.set(0, 99);
        follower.setVelocity(99);

        assertEquals(List.of(4, 8), context.gapsAhead());
        assertEquals(List.of(2, 5), context.velocitiesAfterR1());
        assertEquals(List.of(4, 1), context.leaderVelocitiesForR2());
        assertThrows(UnsupportedOperationException.class, () -> context.velocitiesAfterR1().set(0, 3));
    }
}
