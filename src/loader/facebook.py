from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
import sys
import os
import json
from tqdm import tqdm

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from src.db.model import Base, Source, Entity, Person, EntityIdentifier, Authority, Location
from src.util.kino_geocode import KinoGeocode

# Initialize Geocode instance
gc = KinoGeocode(large_city_population_cutoff=5000)
gc.load()

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

    # Initialize location cache
    location_cache = {}

    # Read CSV file
    df = pd.read_csv(file_path)

    # Process each row
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Processing Facebook data"):
        # Geocode current_location and origin_location
        current_location_id = get_or_create_location(session, gc, location_cache, row['current_location']) if pd.notna(row['current_location']) else None
        origin_location_id = get_or_create_location(session, gc, location_cache, row['origin_location']) if pd.notna(row['origin_location']) else None

        # Create metadata dictionary
        meta_data = row.to_dict()

        # Create or get the entity
        entity = Entity(type='person', name=f"{row['first_name']} {row['last_name']}", meta_data=json.dumps(meta_data))
        session.add(entity)
        session.flush()  # This will assign an ID to the entity

        # Create the person
        person_data = {
            'entity_id': entity.id,
            'current_location_id': current_location_id,
            'origin_location_id': origin_location_id
        }
        for field in Person.__table__.columns:
            if field.name in row and pd.notna(row[field.name]):
                person_data[field.name] = row[field.name]

        person = Person(**person_data)
        session.add(person)

        # Create entity identifiers
        identifiers = [
            ('phone', row['phone'], None),
            ('user_id', row['facebook_id'], facebook_authority.id)
        ]

        for id_type, id_value, authority_id in identifiers:
            if pd.notna(id_value):
                identifier = EntityIdentifier(
                    entity_id=entity.id,
                    authority_id=authority_id,
                    identifier_type=id_type,
                    identifier_value=str(id_value)
                )
                session.add(identifier)

        # Commit every 500 rows to avoid large transactions
        if _ % 500 == 0:
            session.commit()

    session.commit()
    session.close()

def get_or_create_location(session, geocode, location_cache, location_name):
    # Try to geocode the location
    geocoded_results = geocode.decode(location_name)

    if geocoded_results:
        # If we have results, select the best one
        priority_order = ['city', 'place', 'admin3', 'admin2', 'admin1', 'country']
        selected_result = next((result for priority in priority_order for result in geocoded_results if result['location_type'] == priority), geocoded_results[0])

        geoname_id = selected_result['geoname_id']
        
        # Check if the location is already in the cache
        if geoname_id in location_cache:
            return location_cache[geoname_id]
        
        # Check if the location with this geoname_id already exists in the database
        existing_location = session.query(Location).filter_by(geoname_id=geoname_id).first()
        if existing_location:
            location_cache[geoname_id] = existing_location.id
            return existing_location.id

        # Create a new entity for the location
        location_entity = Entity(type='location', name=selected_result['name'], meta_data=json.dumps(selected_result))
        session.add(location_entity)
        session.flush()  # This will assign an ID to the entity

        # Create a new location
        location = Location(
            entity_id=location_entity.id,
            name=selected_result['name'].title(),
            official_name=selected_result['official_name'],
            country_code=selected_result['country_code'],
            longitude=selected_result['longitude'],
            latitude=selected_result['latitude'],
            geoname_id=geoname_id,
            location_type=selected_result['location_type'],
            population=selected_result['population']
        )
        session.add(location)
        session.flush()  # This will assign an ID to the location
        location_cache[geoname_id] = location.id
        return location.id
    else:
        print(f"Could not geocode location: {location_name}")
        return None

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python src/loader/facebook.py <file_path> <db_url>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    db_url = sys.argv[2]
    load_facebook_data(file_path, db_url)
