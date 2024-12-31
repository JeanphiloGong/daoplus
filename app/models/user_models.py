from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User:
    def __init__(self, username, email, password_hash=None, user_id=None):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.user_id = user_id

    def set_password(self, password):
        """Hash and set the password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """ Check if the provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def create_user(neo4j_service, username, email, password):
        """Create a new user in the Neo4j database."""
        password_hash = generate_password_hash(password)
        query = """
        CREATE (u:User {username: $username, email: $email, password_hash: $password_hash})
        RETURN ID(u) AS id, u.username AS username, u.email AS email, u.password_hash AS password_hash
        """
        result = neo4j_service.execute_query(query, {
            "username": username,
            "email": email,
            "password_hash": password_hash
        })
        if result:
            data = result[0]
            return User(username=data['username'], email=data['email'], password_hash=data['password_hash'], user_id=data['id'])
        return None

    @staticmethod
    def get_user_by_id(neo4j_service, user_id):
        """Get a user by ID from the Neo4j database."""
        query = """
        MATCH (u:User) WHERE ID(u) = $user_id
        RETURN ID(u) AS id, u.username AS username, u.email AS email, u.password_hash AS password_hash
        """
        result = neo4j_service.execute_query(query, {"user_id": int(user_id)})
        if result:
            data = result[0]
            return User(username=data['username'], email=data['email'], password_hash=data['password_hash'], user_id=data['id'])
        return None
        
    @staticmethod
    def get_user_by_username(neo4j_service, username):
        """Get a user by their username."""
        query = """
        MATCH (u:User {username: $username})
        RETURN ID(u) AS id, u.username AS username, u.email AS email, u.password_hash AS password_hash
        """
        result = neo4j_service.execute_query(query, {"username": username})
        if result:
            data = result[0]
            return User(username=data['username'], email=data['email'], password_hash=data['password_hash'], user_id=data['id'])
        return None

    def save(self, neo4j_service):
        """Save (update) the current user in the Neo4j database."""
        if self.user_id:
            query = """
            MATCH (u:User) WHERE ID(u) = $user_id
            SET u.username = $username, u.email = $email, u.password_hash = $password_hash
            RETURN u
            """
            neo4j_service.execute_write(query, {
                "user_id": self.user_id,
                "username": self.username,
                "email": self.email,
                "password_hash": self.password_hash
            })
        else:
            # Optionally handle creating a new user if not already created
            pass

    def get_id(self):
        """Return the user ID as a string for Flask-Login."""
        return str(self.user_id)

    def __repr__(self):
        return f"<User {self.username}>"


