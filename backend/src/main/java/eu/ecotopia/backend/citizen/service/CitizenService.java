package eu.ecotopia.backend.citizen.service;

import eu.ecotopia.backend.citizen.model.Citizen;
import eu.ecotopia.backend.citizen.model.CitizenType;
import eu.ecotopia.backend.game.model.Game;
import eu.ecotopia.backend.tile.model.TileActionType;
import eu.ecotopia.backend.tile.model.TileType;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

/**
 * Manages dynamic citizen spawning, lifecycle, and approval mechanics.
 * Citizens are spawned based on tile actions and have limited lifetimes.
 * Solidarity effects adjust core citizen approvals when dynamic citizens spawn.
 */
@Service
@Slf4j
public class CitizenService {

    private static final int MAX_CITIZENS = 5;
    private static final int MIN_APPROVAL = 0;
    private static final int MAX_APPROVAL = 100;

    /**
     * Determines which citizens to spawn based on the previous tile type and the action taken,
     * creates them, adds them to the game, applies solidarity effects, and returns the list of spawned citizens.
     *
     * @param game             the current game state
     * @param previousTileType the tile type BEFORE the action was performed
     * @param action           the action that was performed on the tile
     * @return list of newly spawned citizens (may be empty if at capacity)
     */
    public List<Citizen> spawnCitizens(Game game, TileType previousTileType, TileActionType action) {
        List<Citizen> spawned = new ArrayList<>();

        // REPLACE_WITH_SOLAR triggers BOTH the destruction spawn (based on old tile) AND Lena
        if (action == TileActionType.REPLACE_WITH_SOLAR) {
            // First, spawn the destruction citizen based on the old tile type
            buildDestructionCitizen(previousTileType).ifPresent(citizen -> {
                if (canAddDynamicCitizen(game)) {
                    game.addCitizen(citizen);
                    spawned.add(citizen);
                    applySolidarityEffects(game, citizen);
                    log.info("Spawned destruction citizen '{}' for REPLACE_WITH_SOLAR on {}", citizen.getName(), previousTileType);
                } else {
                    log.info("Skipping destruction citizen '{}' spawn: max citizens reached", citizen.getName());
                }
            });

            // Then, spawn Lena (solar technician)
            Citizen lena = buildLena();
            if (canAddDynamicCitizen(game)) {
                game.addCitizen(lena);
                spawned.add(lena);
                applySolidarityEffects(game, lena);
                log.info("Spawned Lena for REPLACE_WITH_SOLAR");
            } else {
                log.info("Skipping Lena spawn: max citizens reached");
            }

            return spawned;
        }

        // Standard spawn logic for other actions
        Optional<Citizen> citizen = buildCitizenForAction(previousTileType, action);
        citizen.ifPresent(c -> {
            if (canAddDynamicCitizen(game)) {
                game.addCitizen(c);
                spawned.add(c);
                applySolidarityEffects(game, c);
                log.info("Spawned citizen '{}' for action {} on {}", c.getName(), action, previousTileType);
            } else {
                log.info("Skipping citizen '{}' spawn: max citizens reached", c.getName());
            }
        });

        return spawned;
    }

    /**
     * Adjusts core citizen approvals based on the type of dynamic citizen that was spawned.
     * <p>
     * Solidarity rules:
     * <ul>
     *   <li>Worker spawned (Oleg, Kerstin, Henning): Karl -5, Sarah +3</li>
     *   <li>Environmental spawn (Bernd): Mia -3</li>
     *   <li>Positive spawn (Lena, Dr. Yuki, Pavel): Mia +3, Karl +2</li>
     * </ul>
     *
     * @param game    the current game state
     * @param spawned the citizen that was just spawned
     */
    public void applySolidarityEffects(Game game, Citizen spawned) {
        String name = spawned.getName();

        switch (name) {
            case "Oleg", "Kerstin", "Henning" -> {
                // Worker spawned
                findCitizenByName(game, "Karl").ifPresent(karl -> {
                    karl.setApproval(clampApproval(karl.getApproval() - 5));
                    log.debug("Karl approval adjusted to {} (worker solidarity)", karl.getApproval());
                });
                findCitizenByName(game, "Sarah").ifPresent(sarah -> {
                    sarah.setApproval(clampApproval(sarah.getApproval() + 3));
                    log.debug("Sarah approval adjusted to {} (worker solidarity)", sarah.getApproval());
                });
            }
            case "Bernd" -> {
                // Environmental spawn
                findCitizenByName(game, "Mia").ifPresent(mia -> {
                    mia.setApproval(clampApproval(mia.getApproval() - 3));
                    log.debug("Mia approval adjusted to {} (environmental solidarity)", mia.getApproval());
                });
            }
            case "Lena", "Dr. Yuki", "Pavel" -> {
                // Positive spawn
                findCitizenByName(game, "Mia").ifPresent(mia -> {
                    mia.setApproval(clampApproval(mia.getApproval() + 3));
                    log.debug("Mia approval adjusted to {} (positive solidarity)", mia.getApproval());
                });
                findCitizenByName(game, "Karl").ifPresent(karl -> {
                    karl.setApproval(clampApproval(karl.getApproval() + 2));
                    log.debug("Karl approval adjusted to {} (positive solidarity)", karl.getApproval());
                });
            }
            default -> log.debug("No solidarity effects for citizen '{}'", name);
        }
    }

    /**
     * Decrements remainingRounds for all DYNAMIC citizens and removes those whose rounds have expired.
     *
     * @param game the current game state
     */
    public void tickCitizenLifecycle(Game game) {
        List<Citizen> toRemove = new ArrayList<>();

        for (Citizen citizen : game.getCitizens()) {
            if (citizen.getCitizenType() != CitizenType.DYNAMIC) {
                continue;
            }

            if (citizen.getRemainingRounds() != null) {
                citizen.setRemainingRounds(citizen.getRemainingRounds() - 1);

                if (citizen.getRemainingRounds() <= 0) {
                    toRemove.add(citizen);
                    log.info("Dynamic citizen '{}' expired (remainingRounds reached 0)", citizen.getName());
                }
            }
        }

        game.getCitizens().removeAll(toRemove);
    }

    // --- Private helper methods ---

    /**
     * Checks whether adding another dynamic citizen would exceed the max citizen limit.
     */
    private boolean canAddDynamicCitizen(Game game) {
        return game.getCitizens().size() < MAX_CITIZENS;
    }

    /**
     * Builds the appropriate destruction citizen based on the previous tile type.
     * Used when a tile is demolished or replaced.
     */
    private Optional<Citizen> buildDestructionCitizen(TileType previousTileType) {
        return switch (previousTileType) {
            case OIL_REFINERY -> Optional.of(buildOleg());
            case COAL_PLANT -> Optional.of(buildKerstin());
            case HEALTHY_FOREST -> Optional.of(buildBernd());
            default -> Optional.empty();
        };
    }

    /**
     * Builds the appropriate citizen for a given tile type and action combination.
     */
    private Optional<Citizen> buildCitizenForAction(TileType previousTileType, TileActionType action) {
        return switch (action) {
            case DEMOLISH -> switch (previousTileType) {
                case OIL_REFINERY -> Optional.of(buildOleg());
                case COAL_PLANT -> Optional.of(buildKerstin());
                case HEALTHY_FOREST -> Optional.of(buildBernd());
                default -> Optional.empty();
            };
            case CLEAR_FARMLAND -> previousTileType == TileType.FARMLAND
                    ? Optional.of(buildHenning())
                    : Optional.empty();
            case BUILD_SOLAR -> Optional.of(buildLena());
            case BUILD_RESEARCH_CENTER -> Optional.of(buildDrYuki());
            case BUILD_FUSION -> Optional.of(buildPavel());
            default -> Optional.empty();
        };
    }

    /**
     * Finds a citizen by name in the game's citizen list.
     */
    private Optional<Citizen> findCitizenByName(Game game, String name) {
        return game.getCitizens().stream()
                .filter(c -> name.equals(c.getName()))
                .findFirst();
    }

    /**
     * Clamps an approval value to the valid range [0, 100].
     */
    private int clampApproval(int approval) {
        return Math.max(MIN_APPROVAL, Math.min(MAX_APPROVAL, approval));
    }

    // --- Citizen builder methods ---

    private Citizen buildOleg() {
        return Citizen.builder()
                .name("Oleg")
                .profession("Drill Worker")
                .age(54)
                .approval(15)
                .personality("Angry, fearful, feels discarded after 20 years of service.")
                .remainingRounds(3)
                .citizenType(CitizenType.DYNAMIC)
                .build();
    }

    private Citizen buildKerstin() {
        return Citizen.builder()
                .name("Kerstin")
                .profession("Power Plant Worker")
                .age(38)
                .approval(20)
                .personality("Desperate single mother, needs an alternative immediately.")
                .remainingRounds(2)
                .citizenType(CitizenType.DYNAMIC)
                .build();
    }

    private Citizen buildBernd() {
        return Citizen.builder()
                .name("Bernd")
                .profession("Forester")
                .age(61)
                .approval(25)
                .personality("Sad, disappointed, lives from the forest.")
                .remainingRounds(2)
                .citizenType(CitizenType.DYNAMIC)
                .build();
    }

    private Citizen buildHenning() {
        return Citizen.builder()
                .name("Henning")
                .profession("Farmer")
                .age(55)
                .approval(20)
                .personality("Bitter, conservative, 3rd generation farmer.")
                .remainingRounds(2)
                .citizenType(CitizenType.DYNAMIC)
                .build();
    }

    private Citizen buildLena() {
        return Citizen.builder()
                .name("Lena")
                .profession("Solar Technician")
                .age(28)
                .approval(65)
                .personality("Optimistic, future-oriented, excited about renewables.")
                .remainingRounds(2)
                .citizenType(CitizenType.DYNAMIC)
                .build();
    }

    private Citizen buildDrYuki() {
        return Citizen.builder()
                .name("Dr. Yuki")
                .profession("PhD Student")
                .age(29)
                .approval(70)
                .personality("Enthusiastic, idealistic, researches fusion energy.")
                .remainingRounds(2)
                .citizenType(CitizenType.DYNAMIC)
                .build();
    }

    private Citizen buildPavel() {
        return Citizen.builder()
                .name("Pavel")
                .profession("Fusion Engineer")
                .age(45)
                .approval(60)
                .personality("Proud, rational progress-optimist.")
                .remainingRounds(3)
                .citizenType(CitizenType.DYNAMIC)
                .build();
    }
}
