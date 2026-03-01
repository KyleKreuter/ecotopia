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

import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;

@Component
public class GameInitializer {

    private static final String START_MAP = "maps/start.map";

    public Game createNewGame() {
        TileType[][] map = loadMap(START_MAP);

        Game game = Game.builder()
                .currentRound(1)
                .status(GameStatus.RUNNING)
                .resources(GameResources.builder()
                        .ecology(45)
                        .economy(65)
                        .research(5)
                        .build())
                .build();

        for (int y = 0; y < map.length; y++) {
            for (int x = 0; x < map[y].length; x++) {
                game.addTile(Tile.builder()
                        .x(x)
                        .y(y)
                        .tileType(map[y][x])
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

    private TileType[][] loadMap(String resourcePath) {
        try (InputStream is = getClass().getClassLoader().getResourceAsStream(resourcePath)) {
            if (is == null) {
                throw new IllegalStateException("Map not found: " + resourcePath);
            }

            String content = new String(is.readAllBytes(), StandardCharsets.UTF_8);
            String[] lines = content.lines()
                    .filter(line -> !line.isBlank() && !line.startsWith("#"))
                    .toArray(String[]::new);

            TileType[] types = TileType.values();
            TileType[][] map = new TileType[lines.length][];

            for (int y = 0; y < lines.length; y++) {
                String line = lines[y].trim();
                map[y] = new TileType[line.length()];
                for (int x = 0; x < line.length(); x++) {
                    int index = Character.digit(line.charAt(x), 16);
                    if (index < 0 || index >= types.length) {
                        throw new IllegalStateException(
                                "Invalid tile '%c' at (%d,%d) in %s".formatted(line.charAt(x), x, y, resourcePath));
                    }
                    map[y][x] = types[index];
                }
            }

            return map;
        } catch (IOException e) {
            throw new IllegalStateException("Failed to load map: " + resourcePath, e);
        }
    }
}
