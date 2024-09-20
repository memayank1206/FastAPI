from http.client import responses

from .util import override_get_db, override_get_current_user
from .util import *
from ..routers.users import get_db, get_current_user
from fastapi import status

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_return_user(test_user):
    response = client.get("/users")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['username'] == 'codingwithmayank'

def test_change_password_success(test_user):
    response = client.put("/users/password", json={"password": "testpassword", "new_password": "new_password"})

    assert response.status_code==status.HTTP_204_NO_CONTENT

def test_change_password_invalid_current_password(test_user):
    response = client.put("/users/password", json={"password": "wrong password", "new_password": "new_password"})

    assert response.status_code==status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Error on password change'}