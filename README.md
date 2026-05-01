Cloud File Manager
 
Overview
My project is a cloud-based file management system that allows users to store, organise, and manage files using cloud technologies. 
It shows how different cloud services can be combined into one working application.

 Technologies Used
FastAPI (backend), MongoDB (data storage), Firebase Authentication (user login), Azurite (local Azure Blob Storage emulator), HTML/CSS/JavaScript (frontend).

 Features
User authentication, folder creation and navigation, file upload/download, file deletion, duplicate detection using hashing, overwrite protection, metadata display, search and sorting.

what you need installed
Before running the application, ensure the following are installed and running:

- Python 3.10+
- MongoDB (running locally on default port 27017)
- Node.js (for Azurite)

 Setup Requirements

1. Install Azurite globally:
   npm install -g azurite

2. Start MongoDB:
   mongod

3. Firebase Configuration:
A Firebase project must be created
The Firebase configuration in `firebase-login.js` has been set up using my project credential

 How to Run
1. Create virtual environment
2. Install dependencies using:
   pip install -r requirements.txt
3. Start Azurite by running:
   azurite
   Azurite runs at http://127.0.0.1:10000
4. Start server using:
   uvicorn main:app --reload
5. Open:
   http://127.0.0.1:8000

Authentication
Users log in via Firebase Authentication. Tokens are stored in cookies and verified by the backend.

Storage
File content is stored using Azurite (simulating Azure Blob Storage).
Metadata is stored in MongoDB.

 Notes
Azurite must be running before starting the application.
Ensure MongoDB is running locally and Firebase credentials are properly configured in the frontend code.
