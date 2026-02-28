package eu.ecotopia.backend.promise.repository;

import eu.ecotopia.backend.promise.model.Promise;
import eu.ecotopia.backend.promise.model.PromiseStatus;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface PromiseRepository extends JpaRepository<Promise, Long> {

    List<Promise> findByGameIdAndStatus(Long gameId, PromiseStatus status);

    List<Promise> findByGameId(Long gameId);
}
