import json
from typing import List, Dict, Any
from src.db.database import get_db_connection
from src.models.artifact import Artifact
from src.models.source import Source

def load_facebook_dump(file_path: str, batch_size: int = 1000) -> None:
    """
    Load Facebook dump data from a file in batches.
    
    :param file_path: Path to the Facebook dump file
    :param batch_size: Number of records to process in each batch
    """
    with open(file_path, 'r') as file:
        batch: List[Dict[str, Any]] = []
        
        for line in file:
            data = json.loads(line)
            batch.append(data)
            
            if len(batch) >= batch_size:
                process_batch(batch)
                batch = []
        
        # Process any remaining records
        if batch:
            process_batch(batch)

def process_batch(batch: List[Dict[str, Any]]) -> None:
    """
    Process a batch of Facebook dump records.
    
    :param batch: List of dictionaries containing Facebook dump data
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Create a source for this batch if it doesn't exist
            source = Source(
                type='account_leak',
                name='Facebook Dump',
                metadata={'dump_type': 'facebook'}
            )
            source.save(cur)
            
            for record in batch:
                artifact = Artifact(
                    source_id=source.id,
                    type='account_dump',
                    content=json.dumps(record),
                    metadata={'platform': 'facebook'}
                )
                artifact.save(cur)
        
        conn.commit()

if __name__ == "__main__":
    # Example usage
    load_facebook_dump("path/to/facebook_dump.json")
