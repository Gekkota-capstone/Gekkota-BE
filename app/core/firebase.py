import firebase_admin
from firebase_admin import credentials

# Firebase 초기화
cred = credentials.Certificate("firebase-credentials.json")
firebase_admin.initialize_app(cred) 