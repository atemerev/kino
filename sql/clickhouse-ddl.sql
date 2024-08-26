CREATE TABLE IF NOT EXISTS records
(
    uuid UUID,
    origin String,
    dataset String,
    ingested_at DateTime,
    type String,
    raw String INDEX raw_lowercase(lower(raw)) TYPE full_text,
    
    -- Arbitrary attributes (can be extended later)
    name String INDEX name_lowercase(lower(name)) TYPE full_text,
    first_name String INDEX first_name_lowercase(lower(first_name)) TYPE full_text,
    last_name String INDEX last_name_lowercase(lower(last_name)) TYPE full_text,
    phone String,
    email String,
    internal_id String,
    current_location String,
    origin_location String,
    date_of_birth Date,
    relationship_status String,
    
    -- Additional columns can be added here in the future
)
ENGINE = MergeTree()
PRIMARY KEY (uuid)
ORDER BY (dataset, phone, uuid);
