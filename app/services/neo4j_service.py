import os
from neo4j import GraphDatabase
from dotenv import load_dotenv
from flask import current_app

class Neo4jService:
    def __init__(self, uri=None, user=None, password=None):
        """
        Initialize the Neo4jService with optional parameters.
        If parameters are provided, establish a connection immediately.
        """
        self.driver = None
        if uri and user and password:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def init_app(self, app):
        """
        Initialize the Neo4j driver using the Flask app's configuration.
        This method should be called during the app's initialization.
        """
        # Load environment variables if not already loaded
        load_dotenv()

        # Retrieve Neo4j connection details from app config or environment variables
        uri = app.config.get("NEO4J_URI") or os.getenv("NEO4J_URI")
        user = app.config.get("NEO4J_USER") or os.getenv("NEO4J_USER")
        password = app.config.get("NEO4J_PASSWORD") or os.getenv("NEO4J_PASSWORD")

        if not all([uri, user, password]):
            raise ValueError("Neo4j connection details are missing. Please set NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD.")

        # Initialize the Neo4j driver
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        app.neo4j_service = self  # Attach the service to the app instance

        # Register a teardown function to close the driver when the app context ends
        app.teardown_appcontext(self.close)

    def close(self, exception=None):
        """
        Close the Neo4j driver connection.
        This method is called automatically when the app context is torn down.
        """
        if self.driver:
            self.driver.close()
            self.driver = None

    def execute_query(self, query, parameters=None):
        """
        Execute a Cypher query with optional parameters.
        Returns the query result as a list of dictionaries.
        """
        if not self.driver:
            raise ConnectionError("Neo4j driver is not initialized.")
        
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return [record.data() for record in result]

    def execute_write(self, query, parameters=None):
        """
        Execute a write Cypher query (e.g., CREATE, UPDATE, DELETE).
        Returns the query result as a list of dictionaries.
        """
        return self.execute_query(query, parameters)
