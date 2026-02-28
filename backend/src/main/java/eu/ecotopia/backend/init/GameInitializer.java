package eu.ecotopia.backend.init;

import eu.ecotopia.backend.citizen.model.Citizen;
import eu.ecotopia.backend.citizen.model.CitizenType;
import eu.ecotopia.backend.common.model.GameResources;
import eu.ecotopia.backend.game.model.Game;
import eu.ecotopia.backend.game.model.GameStatus;
import eu.ecotopia.backend.round.model.GameRound;
import eu.ecotopia.backend.tile.model.Tile;
import eu.ecotopia.backend.tile.model.TileType;
import org.springframework.stereotype.Component;

import static eu.ecotopia.backend.tile.model.TileType.*;

@Component
public class GameInitializer {

    private static final TileType[][] START_MAP = {
        {HEALTHY_FOREST, HEALTHY_FOREST, HEALTHY_FOREST, HEALTHY_FOREST, HEALTHY_FOREST, CLEAN_RIVER, CLEAN_RIVER, FACTORY, FACTORY, OIL_REFINERY},
        {HEALTHY_FOREST, HEALTHY_FOREST, HEALTHY_FOREST, HEALTHY_FOREST, HEALTHY_FOREST, CLEAN_RIVER, CLEAN_RIVER, FACTORY, COAL_PLANT, WASTELAND},
        {HEALTHY_FOREST, HEALTHY_FOREST, HEALTHY_FOREST, HEALTHY_FOREST, CLEAN_RIVER, CLEAN_RIVER, CLEAN_RIVER, WASTELAND, WASTELAND, WASTELAND},
        {HEALTHY_FOREST, HEALTHY_FOREST, HEALTHY_FOREST, CLEAN_RIVER, CLEAN_RIVER, CLEAN_RIVER, WASTELAND, WASTELAND, RESIDENTIAL, RESIDENTIAL},
        {CLEAN_RIVER, CLEAN_RIVER, CLEAN_RIVER, CLEAN_RIVER, CLEAN_RIVER, CLEAN_RIVER, FARMLAND, FARMLAND, RESIDENTIAL, RESIDENTIAL},
        {CLEAN_RIVER, CLEAN_RIVER, CLEAN_RIVER, CLEAN_RIVER, CLEAN_RIVER, FARMLAND, FARMLAND, FARMLAND, CITY_CENTER, RESIDENTIAL},
        {WASTELAND, FARMLAND, FARMLAND, FARMLAND, FARMLAND, FARMLAND, FARMLAND, RESIDENTIAL, RESIDENTIAL, RESIDENTIAL},
        {WASTELAND, FARMLAND, FARMLAND, FARMLAND, FARMLAND, FARMLAND, RESIDENTIAL, RESIDENTIAL, CITY_CENTER, WASTELAND},
        {WASTELAND, WASTELAND, FARMLAND, FARMLAND, FARMLAND, WASTELAND, RESIDENTIAL, WASTELAND, WASTELAND, WASTELAND},
        {WASTELAND, WASTELAND, WASTELAND, WASTELAND, WASTELAND, WASTELAND, WASTELAND, WASTELAND, WASTELAND, WASTELAND},
    };

    public Game createNewGame() {
        Game game = Game.builder()
                .currentRound(1)
                .status(GameStatus.RUNNING)
                .resources(GameResources.builder()
                        .ecology(45)
                        .economy(65)
                        .research(5)
                        .build())
                .build();

        for (int y = 0; y < 10; y++) {
            for (int x = 0; x < 10; x++) {
                game.addTile(Tile.builder()
                        .x(x)
                        .y(y)
                        .tileType(START_MAP[y][x])
                        .build());
            }
        }

        game.addCitizen(Citizen.builder()
                .name("Karl")
                .citizenType(CitizenType.CORE)
                .profession("Factory Worker")
                .age(48)
                .personality("Conservative, family-oriented, skeptical of change. Values: jobs, stability, providing for his family.")
                .approval(60)
                .build());

        game.addCitizen(Citizen.builder()
                .name("Mia")
                .citizenType(CitizenType.CORE)
                .profession("Climate Activist")
                .age(24)
                .personality("Idealistic, impatient, passionate. Values: immediate climate action, biodiversity, generational justice.")
                .approval(35)
                .build());

        game.addCitizen(Citizen.builder()
                .name("Sarah")
                .citizenType(CitizenType.CORE)
                .profession("Opposition Politician")
                .age(42)
                .personality("Strategic, opportunistic, sharp-tongued. Exploits the mayor's weaknesses, quotes verbatim, instrumentalizes suffering.")
                .approval(25)
                .build());

        game.addRound(GameRound.builder()
                .roundNumber(1)
                .remainingActions(2)
                .build());

        return game;
    }
}
