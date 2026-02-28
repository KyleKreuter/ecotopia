package eu.ecotopia.backend.game.repository;

import eu.ecotopia.backend.game.model.Game;
import eu.ecotopia.backend.game.model.GameStatus;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface GameRepository extends JpaRepository<Game, Long> {

    List<Game> findByStatus(GameStatus status);

    Optional<Game> findTopByOrderByCreatedAtDesc();
}
