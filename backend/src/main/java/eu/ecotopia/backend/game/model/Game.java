package eu.ecotopia.backend.game.model;

import eu.ecotopia.backend.citizen.model.Citizen;
import eu.ecotopia.backend.common.model.GameResources;
import eu.ecotopia.backend.promise.model.Promise;
import eu.ecotopia.backend.round.model.GameRound;
import eu.ecotopia.backend.tile.model.Tile;
import jakarta.persistence.CascadeType;
import jakarta.persistence.Embedded;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.OneToMany;
import jakarta.persistence.PrePersist;
import jakarta.persistence.PreUpdate;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.ToString;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "games")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
@EqualsAndHashCode(onlyExplicitlyIncluded = true)
@ToString(exclude = {"tiles", "citizens", "promises", "rounds"})
public class Game {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @EqualsAndHashCode.Include
    private Long id;

    private int currentRound;

    @Enumerated(EnumType.STRING)
    private GameStatus status;

    @Enumerated(EnumType.STRING)
    private GameRank resultRank;

    @Enumerated(EnumType.STRING)
    private DefeatReason defeatReason;

    @Embedded
    private GameResources resources;

    private Instant createdAt;
    private Instant updatedAt;

    @OneToMany(mappedBy = "game", cascade = CascadeType.ALL, orphanRemoval = true)
    @Builder.Default
    private List<Tile> tiles = new ArrayList<>();

    @OneToMany(mappedBy = "game", cascade = CascadeType.ALL, orphanRemoval = true)
    @Builder.Default
    private List<Citizen> citizens = new ArrayList<>();

    @OneToMany(mappedBy = "game", cascade = CascadeType.ALL, orphanRemoval = true)
    @Builder.Default
    private List<Promise> promises = new ArrayList<>();

    @OneToMany(mappedBy = "game", cascade = CascadeType.ALL, orphanRemoval = true)
    @Builder.Default
    private List<GameRound> rounds = new ArrayList<>();

    @PrePersist
    void prePersist() {
        createdAt = Instant.now();
        updatedAt = Instant.now();
    }

    @PreUpdate
    void preUpdate() {
        updatedAt = Instant.now();
    }

    public void addTile(Tile tile) {
        tiles.add(tile);
        tile.setGame(this);
    }

    public void addCitizen(Citizen citizen) {
        citizens.add(citizen);
        citizen.setGame(this);
    }

    public void addPromise(Promise promise) {
        promises.add(promise);
        promise.setGame(this);
    }

    public void addRound(GameRound round) {
        rounds.add(round);
        round.setGame(this);
    }
}
