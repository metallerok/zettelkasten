import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models.meta import Base
from src import models

from tests.helpers.headers import Headers

from config import TestConfig

import venusian


@pytest.fixture(scope="module")
def db_engine():
    venusian.Scanner().scan(models)
    engine = create_engine(TestConfig.db_uri)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield engine


@pytest.fixture(scope="module")
def db_session(db_engine):
    session = sessionmaker(
        db_engine, expire_on_commit=False
    )()

    yield session

    session.close()


@pytest.fixture(scope="function")
def headers() -> Headers:
    headers = Headers()

    yield headers
