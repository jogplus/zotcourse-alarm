from flask import Flask, redirect
import firebase_admin
from firebase_admin import firestore

app = Flask(__name__)
# Use the application default credentials
default_app = firebase_admin.initialize_app()
db = firestore.client()

@app.route('/')
def index():
    doc_ref = db.collection(u'ngrok').document(u'latest')
    try:
        doc = doc_ref.get().to_dict()
        ngrok_url = doc.get('url')
        return redirect(ngrok_url)
    except Exception as e:
        return 'Error with firestore: ' + str(e)
    
