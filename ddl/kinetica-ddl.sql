DROP TABLE IF EXISTS EntityMentions;
DROP TABLE IF EXISTS EntityEnrichments;
DROP TABLE IF EXISTS EnrichmentSources;
DROP TABLE IF EXISTS Entities;
DROP TABLE IF EXISTS Artifacts;

CREATE REPLICATED TABLE Artifacts (
    artifact_id BIGINT PRIMARY KEY,
    type VARCHAR(50),
    content TEXT,
    source VARCHAR(255),
    timestamp TIMESTAMP,
    metadata JSON
);

CREATE REPLICATED TABLE Entities (
    entity_id BIGINT PRIMARY KEY,
    type VARCHAR(50),
    name VARCHAR(255),
    metadata JSON
);

CREATE TABLE EntityMentions (
    mention_id BIGINT,
    entity_id BIGINT,
    artifact_id BIGINT,
    start_position INTEGER,
    end_position INTEGER,
    context TEXT,
    FOREIGN KEY (entity_id) REFERENCES Entities(entity_id),
    FOREIGN KEY (artifact_id) REFERENCES Artifacts(artifact_id)
);

CREATE REPLICATED TABLE EnrichmentSources (
    source_id BIGINT PRIMARY KEY,
    name VARCHAR(255),
    description TEXT,
    last_updated TIMESTAMP
);

CREATE TABLE EntityEnrichments (
    enrichment_id BIGINT PRIMARY KEY,
    entity_id BIGINT,
    source_id BIGINT,
    enrichment_data JSON,
    timestamp TIMESTAMP,
    FOREIGN KEY (entity_id) REFERENCES Entities(entity_id),
    FOREIGN KEY (source_id) REFERENCES EnrichmentSources(source_id)
);

