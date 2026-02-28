package eu.ecotopia.backend.citizen.repository;

import eu.ecotopia.backend.citizen.model.Citizen;
import eu.ecotopia.backend.citizen.model.CitizenType;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface CitizenRepository extends JpaRepository<Citizen, Long> {

    List<Citizen> findByGameId(Long gameId);

    List<Citizen> findByGameIdAndCitizenType(Long gameId, CitizenType citizenType);

    long countByGameIdAndCitizenType(Long gameId, CitizenType citizenType);
}
