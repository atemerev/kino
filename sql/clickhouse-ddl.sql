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
    birthday Date,
    raw String,
    metadata String,
    INDEX idx_fulltext_raw raw TYPE fulltext,
    INDEX idx_fulltext_first_name first_name TYPE fulltext,
    INDEX idx_fulltext_last_name last_name TYPE fulltext
) ENGINE = MergeTree()
ORDER BY (phone, facebook_id);
