from flask import current_app, g

print(current_app.name)  # Should print the app name
print(g)  # Flask's global object, useful for storing request-specific data
