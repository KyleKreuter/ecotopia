package eu.ecotopia.backend.round.repository;

import eu.ecotopia.backend.round.model.GameRound;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface GameRoundRepository extends JpaRepository<GameRound, Long> {

    Optional<GameRound> findByGameIdAndRoundNumber(Long gameId, int roundNumber);

    List<GameRound> findByGameIdOrderByRoundNumberAsc(Long gameId);
}
