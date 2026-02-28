package eu.ecotopia.backend.citizen.model;

import eu.ecotopia.backend.game.model.Game;
import eu.ecotopia.backend.promise.model.Promise;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.OneToMany;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.ToString;

import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "citizens")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
@EqualsAndHashCode(onlyExplicitlyIncluded = true)
@ToString(exclude = {"game", "promises"})
public class Citizen {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @EqualsAndHashCode.Include
    private Long id;

    private String name;

    @Enumerated(EnumType.STRING)
    private CitizenType citizenType;

    private String profession;

    private Integer age;

    @Column(length = 1000)
    private String personality;

    private int approval;

    @Column(length = 2000)
    private String openingSpeech;

    private Integer remainingRounds;

    @ManyToOne(fetch = FetchType.LAZY)
    private Game game;

    @OneToMany(mappedBy = "citizen")
    @Builder.Default
    private List<Promise> promises = new ArrayList<>();
}
