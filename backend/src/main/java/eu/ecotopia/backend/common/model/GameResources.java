package eu.ecotopia.backend.common.model;

import jakarta.persistence.Embeddable;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Embeddable
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class GameResources {

    @Min(0) @Max(100)
    private int ecology;

    @Min(0) @Max(100)
    private int economy;

    @Min(0) @Max(100)
    private int research;
}
