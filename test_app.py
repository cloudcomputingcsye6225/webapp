import pytest
from time import sleep
from api import app
from utilities import generate_random_string
import base64

first_name = generate_random_string(10)
last_name = generate_random_string(10)
username = f'{generate_random_string(10)}@{generate_random_string(10)}.com'
password = generate_random_string(10)
auth_encoded = base64.b64encode(f'{username}:{password}'.encode('utf-8')).decode('utf-8')
new_password = generate_random_string(10)
new_auth_encoded = base64.b64encode(f'{username}:{new_password}'.encode('utf-8')).decode('utf-8')

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_check_health(client):
    headers = {
            'Content-Type': 'application/json'
    }
    
    response = client.get('/healthz', headers = headers)
    assert response.status_code in [200, 503]

    response = client.post('/healthz', headers = headers)
    assert response.status_code == 405

    response = client.put('/healthz', headers = headers)
    assert response.status_code == 405
    
    response = client.delete('/healthz', headers = headers)
    assert response.status_code == 405

    response = client.patch('/healthz', headers = headers)
    assert response.status_code == 405

    response = client.head('/healthz', headers = headers)
    assert response.status_code == 405

    response = client.options('/healthz', headers = headers)
    assert response.status_code == 405

    response = client.get('/healthzsd', headers = headers)
    assert response.status_code == 404

    response = client.get('/healthz?user=123', headers = headers)
    assert response.status_code == 400

    response = client.get('/healthz', headers = headers, json = {})
    assert response.status_code == 400

    response = client.get('/healthz', headers = headers)
    assert response.status_code in [200, 503]

    assert response.headers['Content-Type'] == 'application/json'
    assert response.headers['Content-Length'] == '0'
    assert response.headers['Pragma'] == 'no-cache'
    assert response.headers['Cache-Control'] == 'no-cache, no-store, must-revalidate'

def test_create_user(client):
    user_data = {
        "first_name": first_name,
        "last_name": last_name,
        "username": username,
        "password": password
    }
    response = client.post('/v1/user', json=user_data)
    assert response.status_code == 201

def test_get_user_profile(client):
    response = client.get('/v1/user/self', headers={'Authorization': f'Basic {auth_encoded}'})
    assert response.status_code == 200

def test_update_user_profile(client):

    headers = {
        'Authorization': f'Basic {auth_encoded}'
    }
    updated_user_data = {
        "first_name": first_name,
        "last_name": last_name,
        "password": new_password
    }
    response = client.put('/v1/user/self', headers=headers, json=updated_user_data)
    assert response.status_code == 204

def test_get_user_profile_updated(client):
    response = client.get('/v1/user/self', headers={'Authorization': f'Basic {new_auth_encoded}'})
    assert response.status_code == 200

def test_invalid_route(client):
    response = client.get('/invalid_route')
    assert response.status_code == 404

if __name__ == "__main__":
    pytest.main()
