import pytest

from blog_platform import create_app


@pytest.fixture
def app():
    app = create_app(testing=True)
    yield app


@pytest.fixture
def client(app):
    return app.test_client()
