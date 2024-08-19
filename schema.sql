-- Create enum types
CREATE TYPE artifact_type AS ENUM ('document', 'social_media_post', 'account_dump', 'web_page', 'other');
CREATE TYPE entity_type AS ENUM ('person', 'organization', 'location', 'other');

-- Artifacts table
CREATE TABLE artifacts (
    id SERIAL PRIMARY KEY,
    type artifact_type NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Entities table
CREATE TABLE entities (
    id SERIAL PRIMARY KEY,
    type entity_type NOT NULL,
    name TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Entity mentions table (for named entity recognition results)
CREATE TABLE entity_mentions (
    id SERIAL PRIMARY KEY,
    artifact_id INTEGER REFERENCES artifacts(id),
    entity_id INTEGER REFERENCES entities(id),
    mention_text TEXT NOT NULL,
    start_position INTEGER,
    end_position INTEGER,
    confidence FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Entity relationships table (for cross-referencing)
CREATE TABLE entity_relationships (
    id SERIAL PRIMARY KEY,
    entity1_id INTEGER REFERENCES entities(id),
    entity2_id INTEGER REFERENCES entities(id),
    relationship_type TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_artifacts_type ON artifacts(type);
CREATE INDEX idx_entities_type ON entities(type);
CREATE INDEX idx_entity_mentions_artifact_id ON entity_mentions(artifact_id);
CREATE INDEX idx_entity_mentions_entity_id ON entity_mentions(entity_id);
CREATE INDEX idx_entity_relationships_entity1_id ON entity_relationships(entity1_id);
CREATE INDEX idx_entity_relationships_entity2_id ON entity_relationships(entity2_id);

