-- Enable pg_trgm extension for fuzzy search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Drop and recreate enum types
DROP TYPE IF EXISTS artifact_type CASCADE;
DROP TYPE IF EXISTS entity_type CASCADE;
DROP TYPE IF EXISTS source_type CASCADE;
DROP TYPE IF EXISTS identifier_type CASCADE;
DROP TYPE IF EXISTS relationship_status CASCADE;
DROP TYPE IF EXISTS sex CASCADE;
DROP TYPE IF EXISTS location_type CASCADE;

CREATE TYPE artifact_type AS ENUM ('document', 'social_media_post', 'account_dump', 'web_page', 'other');
CREATE TYPE entity_type AS ENUM ('person', 'organization', 'location', 'other');
CREATE TYPE source_type AS ENUM ('account_leak', 'social_media', 'website', 'other');
CREATE TYPE identifier_type AS ENUM ('phone', 'email', 'username', 'user_id', 'tax_number', 'passport', 'national_id', 'other');
CREATE TYPE relationship_status AS ENUM ('single', 'married', 'divorced', 'widowed', 'separated', 'in_relationship', 'other');
CREATE TYPE sex AS ENUM ('male', 'female', 'other');
CREATE TYPE location_type AS ENUM ('city', 'place', 'country', 'continent', 'region', 'other');

-- Sources table
DROP TABLE IF EXISTS sources CASCADE;
CREATE TABLE IF NOT EXISTS sources (
    id SERIAL PRIMARY KEY,
    type source_type NOT NULL,
    name TEXT NOT NULL,
    url TEXT,
    medium TEXT,
    channel TEXT,
    meta_data JSONB,
    source_timestamp TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Artifacts table
DROP TABLE IF EXISTS artifacts CASCADE;
CREATE TABLE IF NOT EXISTS artifacts (
    id SERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES sources(id),
    type artifact_type NOT NULL,
    content TEXT NOT NULL,
    meta_data JSONB,
    source_timestamp TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Entities table
DROP TABLE IF EXISTS entities CASCADE;
CREATE TABLE IF NOT EXISTS entities (
    id SERIAL PRIMARY KEY,
    type entity_type NOT NULL,
    name TEXT NOT NULL,
    meta_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Persons table
DROP TABLE IF EXISTS persons CASCADE;
CREATE TABLE IF NOT EXISTS persons (
    id SERIAL PRIMARY KEY,
    entity_id INTEGER REFERENCES entities(id),
    first_name TEXT,
    last_name TEXT,
    date_of_birth DATE,
    nationality TEXT,
    sex sex,
    relationship_status relationship_status,
    current_location_id INTEGER REFERENCES locations(id),
    origin_location_id INTEGER REFERENCES locations(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Organizations table
DROP TABLE IF EXISTS organizations CASCADE;
CREATE TABLE IF NOT EXISTS organizations (
    id SERIAL PRIMARY KEY,
    entity_id INTEGER REFERENCES entities(id),
    org_type TEXT,
    founded_date DATE,
    headquarters TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Locations table
DROP TABLE IF EXISTS locations CASCADE;
CREATE TABLE IF NOT EXISTS locations (
    id SERIAL PRIMARY KEY,
    entity_id INTEGER REFERENCES entities(id),
    name TEXT NOT NULL,
    official_name TEXT,
    country_code CHAR(2),
    longitude DECIMAL(9,6),
    latitude DECIMAL(8,6),
    geoname_id INTEGER,
    location_type location_type,
    population INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_locations_geoname_id ON locations(geoname_id);
CREATE INDEX IF NOT EXISTS idx_locations_name ON locations(name);
CREATE INDEX IF NOT EXISTS idx_locations_country_code ON locations(country_code);

-- Entity mentions table (for named entity recognition results)
DROP TABLE IF EXISTS entity_mentions CASCADE;
CREATE TABLE IF NOT EXISTS entity_mentions (
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
DROP TABLE IF EXISTS entity_relationships CASCADE;
CREATE TABLE IF NOT EXISTS entity_relationships (
    id SERIAL PRIMARY KEY,
    source_entity INTEGER REFERENCES entities(id),
    target_entity INTEGER REFERENCES entities(id),
    relationship_type TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_artifacts_type ON artifacts(type);
CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(type);
CREATE INDEX IF NOT EXISTS idx_entity_mentions_artifact_id ON entity_mentions(artifact_id);
CREATE INDEX IF NOT EXISTS idx_entity_mentions_entity_id ON entity_mentions(entity_id);
CREATE INDEX IF NOT EXISTS idx_entity_relationships_source_entity ON entity_relationships(source_entity);
CREATE INDEX IF NOT EXISTS idx_entity_relationships_target_entity ON entity_relationships(target_entity);

-- Create index for sources
CREATE INDEX IF NOT EXISTS idx_sources_type ON sources(type);

-- Create index for artifacts.source_id
CREATE INDEX IF NOT EXISTS idx_artifacts_source_id ON artifacts(source_id);

-- Create indexes for new tables
CREATE INDEX IF NOT EXISTS idx_persons_entity_id ON persons(entity_id);
CREATE INDEX IF NOT EXISTS idx_organizations_entity_id ON organizations(entity_id);
CREATE INDEX IF NOT EXISTS idx_locations_entity_id ON locations(entity_id);

-- Create GIN indexes for fuzzy search
CREATE INDEX IF NOT EXISTS idx_entities_name_trgm ON entities USING gin (name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_persons_first_name_trgm ON persons USING gin (first_name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_persons_last_name_trgm ON persons USING gin (last_name gin_trgm_ops);

-- Authorities table
DROP TABLE IF EXISTS authorities CASCADE;
CREATE TABLE IF NOT EXISTS authorities (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Entity identifiers table
DROP TABLE IF EXISTS entity_identifiers CASCADE;
CREATE TABLE IF NOT EXISTS entity_identifiers (
    id SERIAL PRIMARY KEY,
    entity_id INTEGER REFERENCES entities(id),
    authority_id INTEGER REFERENCES authorities(id),
    identifier_type identifier_type NOT NULL,
    identifier_value TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for entity_identifiers
CREATE INDEX IF NOT EXISTS idx_entity_identifiers_entity_id ON entity_identifiers(entity_id);
CREATE INDEX IF NOT EXISTS idx_entity_identifiers_authority_id ON entity_identifiers(authority_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_entity_identifiers_authority_type_value ON entity_identifiers(authority_id, identifier_type, identifier_value);

-- Insert some example authorities
INSERT INTO authorities (name, description) VALUES
('Facebook', 'Facebook identifiers'),
('Twitter', 'Twitter identifiers');
