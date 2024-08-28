-- Fuzzy search by first name and last name
SELECT
    uuid,
    first_name,
    last_name,
    name,
    origin,
    dataset,
    ingested_at,
    type
FROM records
WHERE fuzzySearch(first_name_lowercase, lower({first_name:String})) = 1
   OR fuzzySearch(last_name_lowercase, lower({last_name:String})) = 1
ORDER BY ingested_at DESC
LIMIT 100;
