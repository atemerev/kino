CREATE TABLE IF NOT EXISTS records
(
    uuid UUID,
    origin String,
    dataset String,
    ingested_at DateTime,
    type String,
    raw String,
    
    -- Arbitrary attributes (can be extended later)
    name String,
    first_name String,
    last_name String,
    phone String,
    email String,
    internal_id String,
    current_location String,
    origin_location String,
    date_of_birth Date,
    relationship_status String,
    
    -- Additional columns can be added here in the future

    INDEX raw_lowercase(lower(raw)) TYPE full_text,
    INDEX name_lowercase(lower(name)) TYPE full_text,
    INDEX first_name_lowercase(lower(first_name)) TYPE full_text,
    INDEX last_name_lowercase(lower(last_name)) TYPE full_text
)
ENGINE = MergeTree()
PRIMARY KEY (uuid);
