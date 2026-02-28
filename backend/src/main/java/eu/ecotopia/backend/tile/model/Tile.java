package eu.ecotopia.backend.tile.model;

import eu.ecotopia.backend.game.model.Game;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.ToString;

@Entity
@Table(name = "tiles", uniqueConstraints = @UniqueConstraint(columnNames = {"game_id", "x", "y"}))
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
@EqualsAndHashCode(onlyExplicitlyIncluded = true)
@ToString(exclude = "game")
public class Tile {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @EqualsAndHashCode.Include
    private Long id;

    private int x;
    private int y;

    @Enumerated(EnumType.STRING)
    private TileType tileType;

    @Builder.Default
    private int roundsInCurrentState = 0;

    @ManyToOne(fetch = FetchType.LAZY)
    private Game game;
}
