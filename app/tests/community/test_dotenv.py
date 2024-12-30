import os
from dotenv import load_dotenv

# Load environment from .env file
load_dotenv()

# Retrieve Neo4j connection details from environment variables
uri = os.getenv("NEO4J_URI")
username = os.getenv("NEO4J_USER")
password = os.getenv("NEO4J_PASSWORD")

# Check if the environment variables were successfully loaded
if uri is None:
    print("Error: NEO4J_URI environment variable is not set.")
else:
    print(f"NEO4J_URI is set to: {uri}")

if username is None:
    print("Error: NEO4J_USER environment variable is not set.")
else:
    print(f"NEO4J_USER is set to: {username}")

if password is None:
    print("Error: NEO4J_PASSWORD environment variable is not set.")
else:
    print("NEO4J_PASSWORD is set.")  # We don't print the password for security reasons.
