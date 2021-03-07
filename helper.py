import requests
import time
import os
import json
import subprocess
import webbrowser
import firebase_admin
import logging
from config import Config as config
from bs4 import BeautifulSoup
from models import Course
from firebase_admin import credentials, firestore

logger = logging.getLogger("app")


def get_course_request(params=None):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"
    }
    while True:
        try:
            response = requests.get(
                config.WEBSOC_BASE_URL, params=params, headers=headers
            )
            return response.content
        except Exception as e:
            logger.error("Course Request failed, retrying...", e)
            time.sleep(2)


def get_course_info(code, year_term):
    params = {"YearTerm": year_term, "CourseCodes": code, "Submit": "XML"}

    r = get_course_request(params=params)
    soup = BeautifulSoup(r, "lxml-xml")
    course_info = dict()
    for department in soup.find_all("department"):
        course_info["course_department"] = department.get("dept_code")
        for course in department.find_all("course"):
            course_info["course_number"] = course.get("course_number")
            for section in course.find_all("section"):
                course_info["course_code"] = section.find("course_code").text
                course_info["course_type"] = section.find("sec_type").text
                course_info["course_status"] = section.find("sec_status").text
    return Course(**course_info)


def open_in_browser(url):
    if config.OPEN_WINDOW_IN_BROWSER:
        webbrowser.open(url)


def register_url():
    if not config.USING_NGROK:
        open_in_browser(f"http://localhost:{config.PORT}")
        return

    with open(os.devnull, "w") as fp:
        subprocess.Popen(["./ngrok", "http", str(config.PORT)], stdout=fp, stderr=fp)

    failed = True
    ngrok_url = None
    time.sleep(5)  # Wait for ngrok to connect
    while failed:
        try:
            res = requests.get("http://localhost:4040/api/tunnels")
            res_unicode = res.content.decode("utf-8")
            res_json = json.loads(res_unicode)
            ngrok_url = res_json["tunnels"][0]["public_url"]
            logger.info(f"Ngrok open at: {ngrok_url}")
            failed = False
        except Exception:
            logger.error("Ngrok connection failed, retrying...")
            time.sleep(5)
    if config.USING_FIRESTORE:
        cred = credentials.Certificate(config.SERVICE_ACCOUNT_FILE)
        firebase_admin.initialize_app(cred)
        firestore_db = firestore.client()
        doc_ref = firestore_db.collection("ngrok").document("latest")
        doc_ref.set({"url": ngrok_url})
    open_in_browser(ngrok_url)
