import pytest
from generated_file import User, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Create a test engine
engine = create_engine('sqlite:///:memory:')

# Create all tables in the engine
Base.metadata.create_all(engine)

# Create a configured "Session" class
Session = sessionmaker(bind=engine)

def test_user_registration_happy_path():
    """Test user registration with valid username and email."""
    session = Session()
    user = User(username='john_doe', email='john.doe@example.com')
    session.add(user)
    session.commit()
    assert user.id is not None
    assert user.username == 'john_doe'
    assert user.email == 'john.doe@example.com'
    session.close()

def test_user_editing_happy_path():
    """Test user editing with valid username and email."""
    session = Session()
    user = User(username='john_doe', email='john.doe@example.com')
    session.add(user)
    session.commit()
    user.username = 'jane_doe'
    user.email = 'jane.doe@example.com'
    session.commit()
    assert user.id is not None
    assert user.username == 'jane_doe'
    assert user.email == 'jane.doe@example.com'
    session.close()

def test_user_registration_edge_case_empty_username():
    """Test user registration with empty username."""
    session = Session()
    user = User(username='', email='john.doe@example.com')
    with pytest.raises(ValueError):
        session.add(user)
    session.close()

def test_user_registration_edge_case_empty_email():
    """Test user registration with empty email."""
    session = Session()
    user = User(username='john_doe', email='')
    with pytest.raises(ValueError):
        session.add(user)
    session.close()

def test_user_registration_edge_case_duplicate_username():
    """Test user registration with duplicate username."""
    session = Session()
    user1 = User(username='john_doe', email='john.doe@example.com')
    session.add(user1)
    session.commit()
    user2 = User(username='john_doe', email='jane.doe@example.com')
    with pytest.raises(IntegrityError):
        session.add(user2)
    session.close()

def test_user_registration_edge_case_duplicate_email():
    """Test user registration with duplicate email."""
    session = Session()
    user1 = User(username='john_doe', email='john.doe@example.com')
    session.add(user1)
    session.commit()
    user2 = User(username='jane_doe', email='john.doe@example.com')
    with pytest.raises(IntegrityError):
        session.add(user2)
    session.close()

def test_user_to_dict():
    """Test user to dictionary conversion."""
    session = Session()
    user = User(username='john_doe', email='john.doe@example.com')
    session.add(user)
    session.commit()
    user_dict = user.to_dict()
    assert user_dict['id'] is not None
    assert user_dict['username'] == 'john_doe'
    assert user_dict['email'] == 'john.doe@example.com'
    session.close()