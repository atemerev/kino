CREATE TABLE IF NOT EXISTS records
(
    uuid UUID,
    origin String,
    dataset String,
    ingested_at DateTime,
    type String,
    raw String,
    
    -- Arbitrary attributes (can be extended later)
    phone String,
    email String,
    internal_id String,
    current_location String,
    origin_location String,
    date_of_birth Date,
    relationship_status String,
    
    -- Additional columns can be added here in the future
    
    -- Clickhouse-specific optimizations
    _version UInt64
)
ENGINE = ReplacingMergeTree(_version)
PRIMARY KEY (uuid)
ORDER BY (dataset, phone);
