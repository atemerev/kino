from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import csv
from typing import List, Dict
import sys
import os
import json

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from src.db.model import Base, Source, Entity, Person, EntityIdentifier, Authority

def load_facebook_data(file_path: str, db_url: str):
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create or get the Facebook source
    facebook_source = session.query(Source).filter_by(name='Facebook').first()
    if not facebook_source:
        facebook_source = Source(type='social_media', name='Facebook')
        session.add(facebook_source)
        session.commit()

    # Create or get the Facebook authority
    facebook_authority = session.query(Authority).filter_by(name='Facebook').first()
    if not facebook_authority:
        facebook_authority = Authority(name='Facebook', description='Facebook usernames')
        session.add(facebook_authority)
        session.commit()

    with open(file_path, 'r') as file:
        csv_reader = csv.reader(file, delimiter=':')
        for row in csv_reader:
            # Ensure we have at least the minimum required fields
            if len(row) < 5:
                print(f"Skipping row with insufficient data: {row}")
                continue

            phone, facebook_id, first_name, last_name, sex, *other_fields = row
            current_city = other_fields[0] if len(other_fields) > 0 else None
            hometown = other_fields[1] if len(other_fields) > 1 else None
            relationship_status = other_fields[2] if len(other_fields) > 2 else None
            workplace = other_fields[3] if len(other_fields) > 3 else None
            # Create metadata dictionary
            metadata = {
                'phone': phone,
                'facebook_id': facebook_id,
                'first_name': first_name,
                'last_name': last_name,
                'sex': sex,
                'current_city': current_city,
                'hometown': hometown,
                'relationship_status': relationship_status,
                'workplace': workplace
            }

            # Create or get the entity
            entity = Entity(type='person', name=f"{first_name} {last_name}", metadata=json.dumps(metadata))
            session.add(entity)
            session.flush()  # This will assign an ID to the entity

            # Create the person
            person = Person(
                entity_id=entity.id,
                first_name=first_name,
                last_name=last_name,
                sex=sex.lower() if sex else None,
                relationship_status=relationship_status.lower().replace(' ', '_') if relationship_status and relationship_status.lower().replace(' ', '_') in ['single', 'married', 'divorced', 'widowed', 'separated', 'in_relationship'] else None
            )
            session.add(person)

            # Create entity identifiers
            identifiers = [
                ('phone', phone, None),
                ('user_id', facebook_id, facebook_authority.id)
            ]

            for id_type, id_value, authority_id in identifiers:
                if id_value:
                    identifier = EntityIdentifier(
                        entity_id=entity.id,
                        authority_id=authority_id,
                        identifier_type=id_type,
                        identifier_value=id_value
                    )
                    session.add(identifier)

    session.commit()
    session.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python src/loader/facebook.py <file_path> <db_url>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    db_url = sys.argv[2]
    load_facebook_data(file_path, db_url)
