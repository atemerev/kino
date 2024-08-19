from sqlalchemy import Column, Integer, String, Date, Enum, ForeignKey, JSON, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Source(Base):
    __tablename__ = 'sources'
    id = Column(Integer, primary_key=True)
    type = Column(Enum('account_leak', 'social_media', 'website', 'other', name='source_type'), nullable=False)
    name = Column(String, nullable=False)
    metadata = Column(JSON)

class Entity(Base):
    __tablename__ = 'entities'
    id = Column(Integer, primary_key=True)
    type = Column(Enum('person', 'organization', 'location', 'other', name='entity_type'), nullable=False)
    name = Column(String, nullable=False)
    metadata = Column(JSON)
    source_timestamp = Column(DateTime(timezone=True))

class Person(Base):
    __tablename__ = 'persons'
    id = Column(Integer, primary_key=True)
    entity_id = Column(Integer, ForeignKey('entities.id'))
    first_name = Column(String)
    last_name = Column(String)
    sex = Column(Enum('male', 'female', 'other', name='sex'))
    relationship_status = Column(Enum('single', 'married', 'divorced', 'widowed', 'separated', 'in_relationship', 'other', name='relationship_status'))
    current_location_id = Column(Integer, ForeignKey('locations.id'))
    origin_location_id = Column(Integer, ForeignKey('locations.id'))
    metadata = Column(JSON)

class Location(Base):
    __tablename__ = 'locations'
    id = Column(Integer, primary_key=True)
    entity_id = Column(Integer, ForeignKey('entities.id'))
    name = Column(String, nullable=False)
    official_name = Column(String)
    country_code = Column(String(2))
    longitude = Column(Numeric(9, 6))
    latitude = Column(Numeric(8, 6))
    geoname_id = Column(Integer)
    location_type = Column(Enum('city', 'place', 'country', 'continent', 'region', 'other', name='location_type'))
    population = Column(Integer)
    metadata = Column(JSON)

class Authority(Base):
    __tablename__ = 'authorities'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    metadata = Column(JSON)

class EntityIdentifier(Base):
    __tablename__ = 'entity_identifiers'
    id = Column(Integer, primary_key=True)
    entity_id = Column(Integer, ForeignKey('entities.id'))
    authority_id = Column(Integer, ForeignKey('authorities.id'))
    identifier_type = Column(Enum('phone', 'email', 'username', 'user_id', 'tax_number', 'passport', 'national_id', 'other', name='identifier_type'), nullable=False)
    identifier_value = Column(String, nullable=False)
    metadata = Column(JSON)

class Artifact(Base):
    __tablename__ = 'artifacts'
    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey('sources.id'))
    type = Column(Enum('document', 'social_media_post', 'account_dump', 'web_page', 'other', name='artifact_type'), nullable=False)
    content = Column(String, nullable=False)
    metadata = Column(JSON)
    source_timestamp = Column(DateTime(timezone=True))
