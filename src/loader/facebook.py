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

from src.db.model import Base, Source, Entity, Person, EntityIdentifier, Authority, Location
from src.util.kino_geocode import KinoGeocode


# Initialize two Geocode instances
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

    with open(file_path, 'r') as file:
        csv_reader = csv.reader(file, delimiter=':')
        for row in csv_reader:
            # Ensure we have at least the minimum required fields
            if len(row) < 5:
                print(f"Skipping row with insufficient data: {row}")
                continue

            phone, facebook_id, first_name, last_name, sex, *other_fields = row
            current_location = other_fields[0] if len(other_fields) > 0 else None
            origin_location = other_fields[1] if len(other_fields) > 1 else None
            relationship_status = other_fields[2] if len(other_fields) > 2 else None
            workplace = other_fields[3] if len(other_fields) > 3 else None

            # Geocode current_location and origin_location
            current_location_id = None
            origin_location_id = None

            if current_location:
                current_location_id = get_or_create_location(session, gc, location_cache, current_location)
            if origin_location:
                origin_location_id = get_or_create_location(session, gc, location_cache, origin_location)

            # Create metadata dictionary
            meta_data = {
                'phone': phone,
                'facebook_id': facebook_id,
                'first_name': first_name,
                'last_name': last_name,
                'sex': sex,
                'current_location': current_location,
                'origin_location': origin_location,
                'relationship_status': relationship_status,
                'workplace': workplace
            }

            # Create or get the entity
            entity = Entity(type='person', name=f"{first_name} {last_name}", meta_data=json.dumps(meta_data))
            session.add(entity)
            session.flush()  # This will assign an ID to the entity

            # Create the person
            person = Person(
                entity_id=entity.id,
                first_name=first_name,
                last_name=last_name,
                sex=sex.lower() if sex and sex.lower() in ['male', 'female', 'other'] else None,
                relationship_status=relationship_status if relationship_status in ['Single', 'Married', 'In a relationship', 'Engaged', 'Divorced', 'Separated', 'It\'s complicated', 'Widowed', 'In a domestic partnership', 'In an open relationship', 'In a civil union'] else None,
                current_location_id=current_location_id,
                origin_location_id=origin_location_id
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

def get_or_create_location(session, geocode, location_cache, location_name):
    # Try to geocode the location with city-only instance first
    geocoded_results = geocode.decode(location_name)

    if geocoded_results:
        # If we have results from either geocoding attempt, select the best one
        priority_order = ['city', 'place', 'admin3', 'admin2', 'admin1', 'country']
        selected_result = None
        
        for priority in priority_order:
            for result in geocoded_results:
                if result['location_type'] == priority:
                    selected_result = result
                    break
            if selected_result:
                break
        
        # If no match found in priority list, use the first result
        if not selected_result:
            selected_result = geocoded_results[0]

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

        # Todo: hack, fix with something more reliable
        corrected_name = selected_result['name']
        corrected_name = corrected_name if corrected_name[0].isupper() else corrected_name.title()

        # Create a new location
        location = Location(
            entity_id=location_entity.id,
            name=corrected_name,
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
