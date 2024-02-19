from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
import pandas as pd


Base = declarative_base()


class Movie(Base):
    __tablename__ = 'movie'
    id = Column(String(8), primary_key=True)
    title = Column(String(128))
    year = Column(Integer)
    runtime = Column(Integer)
    parental_guide = Column(String(8))
    gross_us_canada = Column(Float)


class Person(Base):
    __tablename__ = 'person'
    id = Column(String(8), primary_key=True)
    full_name = Column(String(32))


class Cast(Base):
    __tablename__ = 'cast'
    id = Column(Integer, primary_key=True, autoincrement=True)
    movie_id = Column(String(8), ForeignKey('movie.id', name='fk_cast_movie'))
    person_id = Column(String(8), ForeignKey('person.id', name='fk_cast_person'))
    movie = relationship("Movie", backref="cast")
    person = relationship("Person", backref="cast")


class Crew(Base):
    __tablename__ = 'crew'
    id = Column(Integer, primary_key=True, autoincrement=True)
    movie_id = Column(String(8), ForeignKey('movie.id'))
    person_id = Column(String(8), ForeignKey('person.id'))
    role = Column(String(8))
    movie = relationship("Movie", backref="crew")
    person = relationship("Person", backref="crew")


class Genre(Base):
    __tablename__ = 'genre'
    id = Column(Integer, primary_key=True, autoincrement=True)
    movie_id = Column(String(8), ForeignKey('movie.id'))
    genre = Column(String(16))
    movie = relationship("Movie", backref="genre")


# engine = create_engine('sqlite:///movie.db')
# Read the CSV file
df = pd.read_csv('modified_movies.csv')


engine = create_engine('mysql+pymysql://root:Sanaz1374%40%23@localhost:3306/movie')

"""Cast.__table__.drop(engine, checkfirst=True)
Crew.__table__.drop(engine, checkfirst=True)
Genre.__table__.drop(engine, checkfirst=True)
Movie.__table__.drop(engine, checkfirst=True)
"""

Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()


# Iterate over DataFrame rows and insert into the database
for index, row in df.iterrows():
    # gross_usa = None if pd.isna(row['gross_usa']) else row['gross_usa']
    movie = Movie(
        id=row['ID'],
        title=row['title'],
        year=row['year'],
        runtime=row['duration'],
        parental_guide=row['parental_guide'],
        gross_us_canada=row['gross_usa']
    )
    session.add(movie)
# Commit the session to save changes
session.commit()

for index, row in df.iterrows():
    genres = row['genres'].split(', ')
    for genre in genres:
        genre = Genre(
            movie_id=row['ID'],
            genre=genre
        )
        session.add(genre)

# Commit the session to save changes
session.commit()

"""dic = {}
for index, row in df.iterrows():
    directors = row['directors'].split(', ')
    for director in directors:
        if director not in dic:
            dic[director] = row['director IDs'].split(', ')[directors.index(director)]

    creators = row['creators'].split(', ')
    for creator in creators:
        if creator not in dic:
            dic[creator] = row['creator IDs'].split(', ')[creators.index(creator)]

    actors = row['actors'].split(', ')
    for actor in actors:
        if actor not in dic:
            dic[actor] = row['actor IDs'].split(', ')[actors.index(actor)]


for key, value in dic.items():
    person = Person(
        id=value,
        full_name=key
    )
    session.add(person)
"""

dic = {}
for index, row in df.iterrows():
    # Processing directors
    director_names = row['directors'].split(', ')
    director_ids = row['director IDs'].split(', ')
    for name, id in zip(director_names, director_ids):
        if id not in dic.keys():
            dic[id] = name

    # Repeat the same for creators and actors
    creator_names = row['creators'].split(', ')
    creator_ids = row['creator IDs'].split(', ')
    for name, id in zip(creator_names, creator_ids):
        if id not in dic.keys():
            dic[id] = name

    actor_names = row['actors'].split(', ')
    actor_ids = row['actor IDs'].split(', ')
    for name, id in zip(actor_names, actor_ids):
        if id not in dic.keys():
            dic[id] = name

for key, value in dic.items():
    person = Person(
        id=key,
        full_name=value
    )
    session.add(person)

# Commit the session to save changes
session.commit()

for index, row in df.iterrows():
    movie_id = row['ID']
    for actor_id in row['actor IDs'].split(', '):
        #actor_id = row['actor IDs'].split(', ')[row['actors'].split(', ').index(actor)]
        cast = Cast(
            movie_id=movie_id,
            person_id=actor_id
        )
        session.add(cast)

# Commit the session to save changes
session.commit()

for index, row in df.iterrows():
    movie_id = row['ID']
    # for each movie id get the directors and creators and their roles and add them to the crew table
    directors = row['directors'].split(', ')
    creators = row['creators'].split(', ')
    for director in directors:
        director_id = row['director IDs'].split(', ')[directors.index(director)]
        crew = Crew(
            movie_id=movie_id,
            person_id=director_id,
            role='Director'
        )
        session.add(crew)
        
    for creator in creators:
        creator_id = row['creator IDs'].split(', ')[creators.index(creator)]
        crew = Crew(
            movie_id=movie_id,
            person_id=creator_id,
            role='Writer'
        )
        session.add(crew)


# Commit the session to save changes
session.commit()

# Close the session
session.close()
