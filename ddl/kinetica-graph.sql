CREATE GRAPH IntelligenceGraph (
    -- Node types
    Entities (
        id BIGINT PRIMARY KEY REFERENCES Entities(entity_id),
    ),
    Artifacts (
        id BIGINT PRIMARY KEY REFERENCES Artifacts(artifact_id),
    ),

    -- Edge types
    MENTIONS (
        FROM Artifacts.id TO Entities.id,
        mention_id BIGINT REFERENCES EntityMentions(mention_id)
    ),
    RELATES (
        FROM Entities.id TO Entities.id,
        relationship_id BIGINT REFERENCES Relationships(relationship_id)
    )
)
WITH SCHEMA_CHANGE_TRACKING = TRACK;