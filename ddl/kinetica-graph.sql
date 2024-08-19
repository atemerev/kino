CREATE GRAPH IntelligenceGraph (
    -- Node types
    Entities (
        id BIGINT PRIMARY KEY REFERENCES Entities(entity_id),
    ),
    Artifacts (
        id BIGINT PRIMARY KEY REFERENCES Artifacts(artifact_id),
    ),

    -- Edge types
    RELATES (
        FROM Entities.id TO Entities.id,
        relationship_id BIGINT,
        type VARCHAR(50),
        strength FLOAT,
        evidence JSON
    )
)
WITH SCHEMA_CHANGE_TRACKING = TRACK;
