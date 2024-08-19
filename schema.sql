-- Create enum types
CREATE TYPE artifact_type AS ENUM ('document', 'social_media_post', 'account_dump', 'web_page', 'other');
CREATE TYPE entity_type AS ENUM ('person', 'organization', 'location', 'other');
CREATE TYPE source_type AS ENUM ('account_leak', 'social_media', 'website', 'other');

-- Sources table
CREATE TABLE sources (
    id SERIAL PRIMARY KEY,
    type source_type NOT NULL,
    name TEXT NOT NULL,
    url TEXT,
    medium TEXT,
    channel TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Artifacts table
CREATE TABLE artifacts (
    id SERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES sources(id),
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

-- Persons table
CREATE TABLE persons (
    id SERIAL PRIMARY KEY,
    entity_id INTEGER REFERENCES entities(id),
    first_name TEXT,
    last_name TEXT,
    date_of_birth DATE,
    nationality TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Organizations table
CREATE TABLE organizations (
    id SERIAL PRIMARY KEY,
    entity_id INTEGER REFERENCES entities(id),
    org_type TEXT,
    founded_date DATE,
    headquarters TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Locations table
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    entity_id INTEGER REFERENCES entities(id),
    location_type TEXT,
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    country TEXT,
    region TEXT,
    city TEXT,
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

-- Create index for sources
CREATE INDEX idx_sources_type ON sources(type);

-- Create index for artifacts.source_id
CREATE INDEX idx_artifacts_source_id ON artifacts(source_id);

-- Create indexes for new tables
CREATE INDEX idx_persons_entity_id ON persons(entity_id);
CREATE INDEX idx_organizations_entity_id ON organizations(entity_id);
CREATE INDEX idx_locations_entity_id ON locations(entity_id);

