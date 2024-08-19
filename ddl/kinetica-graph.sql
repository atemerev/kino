CREATE GRAPH IntelligenceGraph (
    NODES => INPUT_TABLE(
        SELECT entity_id AS id
        FROM Entities
        UNION ALL
        SELECT artifact_id AS id
        FROM Artifacts
    ),
    EDGES => INPUT_TABLE(
        SELECT 
            e1.entity_id AS from_id,
            e2.entity_id AS to_id,
            'RELATES' AS edge_type,
            em1.mention_id AS relationship_id,
            em1.context AS type,
            1.0 AS strength,
            NULL AS evidence
        FROM Entities e1
        JOIN EntityMentions em1 ON e1.entity_id = em1.entity_id
        JOIN Artifacts a ON em1.artifact_id = a.artifact_id
        JOIN EntityMentions em2 ON a.artifact_id = em2.artifact_id
        JOIN Entities e2 ON em2.entity_id = e2.entity_id
        WHERE e1.entity_id < e2.entity_id
    )
)
