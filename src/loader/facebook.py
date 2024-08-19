from sqlalchemy import create_engine, Column, Integer, String, Date, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import csv
from typing import List, Dict

Base = declarative_base()

class Source(Base):
    __tablename__ = 'sources'
    id = Column(Integer, primary_key=True)
    type = Column(Enum('account_leak', 'social_media', 'website', 'other', name='source_type'), nullable=False)
    name = Column(String, nullable=False)

class Entity(Base):
    __tablename__ = 'entities'
    id = Column(Integer, primary_key=True)
    type = Column(Enum('person', 'organization', 'location', 'other', name='entity_type'), nullable=False)
    name = Column(String, nullable=False)

class Person(Base):
    __tablename__ = 'persons'
    id = Column(Integer, primary_key=True)
    entity_id = Column(Integer, ForeignKey('entities.id'))
    first_name = Column(String)
    last_name = Column(String)
    sex = Column(Enum('male', 'female', 'other', name='sex'))
    relationship_status = Column(Enum('single', 'married', 'divorced', 'widowed', 'separated', 'in_relationship', 'other', name='relationship_status'))

class EntityIdentifier(Base):
    __tablename__ = 'entity_identifiers'
    id = Column(Integer, primary_key=True)
    entity_id = Column(Integer, ForeignKey('entities.id'))
    identifier_type = Column(Enum('phone', 'email', 'username', 'tax_number', 'passport', 'national_id', 'other', name='identifier_type'), nullable=False)
    identifier_value = Column(String, nullable=False)

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

    with open(file_path, 'r') as file:
        csv_reader = csv.reader(file, delimiter=':')
        for row in csv_reader:
            phone, facebook_id, first_name, last_name, sex, current_city, hometown, relationship_status, workplace, join_date, email, birthday = row

            # Create or get the entity
            entity = Entity(type='person', name=f"{first_name} {last_name}")
            session.add(entity)
            session.flush()  # This will assign an ID to the entity

            # Create the person
            person = Person(
                entity_id=entity.id,
                first_name=first_name,
                last_name=last_name,
                sex=sex.lower() if sex else None,
                relationship_status=relationship_status.lower().replace(' ', '_') if relationship_status else None
            )
            session.add(person)

            # Create entity identifiers
            identifiers = [
                ('phone', phone),
                ('username', facebook_id),
                ('email', email)
            ]

            for id_type, id_value in identifiers:
                if id_value:
                    identifier = EntityIdentifier(
                        entity_id=entity.id,
                        identifier_type=id_type,
                        identifier_value=id_value
                    )
                    session.add(identifier)

    session.commit()
    session.close()

if __name__ == "__main__":
    load_facebook_data('data/sample-facebook.txt', 'postgresql://username:password@localhost/dbname')
