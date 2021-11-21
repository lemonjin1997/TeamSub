import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.model import *
from app.setup import setup, setup_dummy_data


@pytest.fixture(scope='function')
def setup_database():
    engine = create_engine('sqlite:///')
    db.Model.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    setup(session)
    yield session
    session.close()


@pytest.fixture(scope='function')
def dummy_dataset(setup_database):
    session = setup_database
    dummy_objects = setup_dummy_data(session)
    yield session, dummy_objects
