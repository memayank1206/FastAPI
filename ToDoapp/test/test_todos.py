from venv import logger
from ..routers.todos import get_db, get_current_user
from fastapi import status
from .util import *
from ..models import Todos

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)

@pytest.fixture
def test_todo():
    todo = Todos(
        title="Learn to code!",
        description="Need to learn everyday",
        priority = 5,
        complete = False,
        owner_id = 1
    )

    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()

def test_read_all_authenticated(test_todo):
    response = client.get("/todos")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'title':"Learn to code!",
        'description':"Need to learn everyday",
        'priority':5,
        'complete':False,
        'owner_id':1,
        'id': 1
    }]

def test_read_one_authenticated(test_todo):
    response = client.get("/todos/todo/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'title':"Learn to code!",
        'description':"Need to learn everyday",
        'priority':5,
        'complete':False,
        'owner_id':1,
        'id': 1
    }

def test_read_one_authenticated_not_found():
    response = client.get("/todos/todo/999")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo not found.'}

def test_create_todo(test_todo):
    request_data = {
        'title': 'New Todo!',
        'description': 'New Todo description',
        'priority': 5,
        'complete': False
    }

    response = client.post('/todos/todo/', json = request_data)
    assert response.status_code==201

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 2).first()
    logger.info(f"MODEL -------> {model}")

def test_update_todo(test_todo):
    request_data = {
        'title': 'Change title',
        'description': 'For learning',
        'priority': 5,
        'complete': False
    }
    response = client.put('/todos/todo/1', json=request_data)
    assert response.status_code==204

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model.title == 'Change title'

def test_update_todo_not_found(test_todo):
    request_data = {
        'title': 'Change title',
        'description': 'For learning',
        'priority': 5,
        'complete': False
    }
    response = client.put('/todos/todo/99', json=request_data)
    assert response.status_code==404
    assert response.json()=={'detail': 'Todo not found.'}

def test_delete_todo(test_todo):
    response = client.delete('/todos/todo/1')
    assert response.status_code==204

    db=TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None

def test_delete_todo_not_found():
    response = client.delete('/todos/todo/99')
    assert response.status_code==404

    assert response.json() == {'detail': 'Todo not found.'}

