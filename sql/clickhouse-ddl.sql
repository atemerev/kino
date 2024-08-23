CREATE TABLE Records
(
    phone String,
    facebook_id String,
    first_name String,
    last_name String,
    gender String,
    city String,
    hometown String,
    relationship_status String,
    workplace String,
    timestamp DateTime,
    email String,
    birthday String,
    raw String,
    metadata String
) ENGINE = MergeTree()
ORDER BY (phone, facebook_id);
