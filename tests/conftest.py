import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models.meta import Base
from src import models
from src.entrypoints.web.wsgi import make_app
from src.message_bus import MessageBusABC

from tests.helpers.headers import Headers
from depot.manager import DepotManager
from falcon import testing
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


@pytest.fixture(scope="module")
def api(db_engine):
    # setup

    yield api_factory_(config=TestConfig)

    # teardown


@pytest.fixture()
def api_factory(db_engine):
    return api_factory_


def api_factory_(
        config=TestConfig,
        message_bus: MessageBusABC = None,
        depot_: DepotManager = None
):
    if not depot_:
        # clear depot middleware before creating client
        # between setup/teardown
        # because DepotManager it's singletone
        DepotManager._depots = {}

    app = make_app(config, message_bus, depot=depot_)
    client = testing.TestClient(app)

    return client
