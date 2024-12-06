import os
import app
print("Static folder path:", os.path.join(os.getcwd(), 'static'))
print("Template folder path:", os.path.join(os.getcwd(), 'templates'))
print(f"Template folder path: {os.path.abspath(app.template_folder)}")
