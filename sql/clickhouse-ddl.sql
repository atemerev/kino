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

    INDEX raw_lowercase raw_lowercase TYPE full_text(lower(raw)),
    INDEX name_lowercase name_lowercase TYPE full_text(lower(name)),
    INDEX first_name_lowercase first_name_lowercase TYPE full_text(lower(first_name)),
    INDEX last_name_lowercase last_name_lowercase TYPE full_text(lower(last_name))
)
ENGINE = MergeTree()
PRIMARY KEY (uuid)
ORDER BY (dataset, phone, uuid);
