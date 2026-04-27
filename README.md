
Cloud File Manager

Overview
My project is a cloud-based file management system that allows users to store, organise, and
manage files using cloud technologies. It demonstrates the integration of multiple services into a
single working application.

Technologies Used
FastAPI (backend), MongoDB (data storage), Firebase Authentication (user login), Azurite (local
Azure Blob Storage emulator), HTML/CSS/JavaScript (frontend).

Features
User authentication, folder creation and navigation, file upload/download, file deletion, duplicate
detection using hashing, overwrite protection, metadata display, search and sorting.

How to Run:
1. Create virtual environment
2. Install dependencies using pip install -r requirements.txt
3. Start Azurite by running: azurite
Azurite runs at http://127.0.0.1:10000
4. Start server using uvicorn main:app --reload
5. Open http://127.0.0.1:8000

Authentication
Users log in via Firebase Authentication. Tokens are stored in cookies and verified by the backend.

Storage
File content is stored using Azurite (simulating Azure Blob Storage).
Metadata is stored in MongoDB.

Notes
Azurite must be running before starting the application.
Ensure MongoDB and Firebase are correctly configured.


