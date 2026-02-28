package eu.ecotopia.backend.tile.repository;

import eu.ecotopia.backend.tile.model.Tile;
import eu.ecotopia.backend.tile.model.TileType;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface TileRepository extends JpaRepository<Tile, Long> {

    Optional<Tile> findByGameIdAndXAndY(Long gameId, int x, int y);

    List<Tile> findByGameIdAndTileType(Long gameId, TileType tileType);

    List<Tile> findByGameIdOrderByYAscXAsc(Long gameId);
}
