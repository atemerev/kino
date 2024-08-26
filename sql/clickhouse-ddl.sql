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
)
ENGINE = MergeTree()
PRIMARY KEY (uuid)
ORDER BY (dataset, phone, uuid);
