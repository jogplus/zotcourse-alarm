import requests
import time
import random
import logging
from helper import get_course_request
from bs4 import BeautifulSoup
from config import Config as config
import smtplib
from models import db, Course
from threading import Thread

logger = logging.getLogger("app")


def start(bgj):
    thread = Thread(target=bgj.run)
    thread.daemon = True
    thread.start()


class BackgroundJob:
    # From https://kb.sandisk.com/app/answers/detail/a_id/17056/~/list-of-mobile-carrier-gateway-addresses
    PHONE_CARRIERS = {
        0: "vzwpix.com",  # Verizon
        1: "mms.att.net",  # ATT
        2: "mymetropcs.com",  # MetroPCS
        3: "pm.sprint.com",  # Sprint
        4: "tmomail.net",  # T-Mobile
    }

    def __init__(self, app):
        self.app = app
        self.year_term = config.YEAR_TERM
        if not self.year_term:
            year_term_html = self.get_current_term()
            self.year_term = year_term_html["value"]
            logger.info(f"Using Term: {year_term_html.text}")

    def run(self):
        with self.app.app_context():
            while True:
                try:
                    course_codes_count = db.session.query(Course).count()
                    if course_codes_count == 0:
                        time.sleep(20)
                        continue
                    for i in range(0, course_codes_count, 10):
                        logger.info(
                            f"Background Run: Courses {i+1}-{min(course_codes_count, i+10)} out of {course_codes_count}"
                        )
                        course_chunk = (
                            db.session.query(Course.course_code, Course.course_status)
                            .offset(i)
                            .limit(10)
                            .all()
                        )
                        self.get_bulk_course_info(course_chunk)
                        random_sleep_time = (
                            random.randint(
                                config.WAIT_TIME_LOWER, config.WAIT_TIME_UPPER
                            )
                            / 100
                        )
                        time.sleep(random_sleep_time)
                except Exception as e:
                    logger.error(e)

    def get_current_term(self):
        request_content = get_course_request()
        parsed_html = BeautifulSoup(request_content, "lxml")
        return parsed_html.find("select", {"name": "YearTerm"}).find_all(
            attrs={"selected": "selected"}
        )[0]

    def get_bulk_course_info(self, code_arr):
        params = {
            "YearTerm": self.year_term,
            "CourseCodes": ",".join([pair[0] for pair in code_arr]),
            "Submit": "XML",
        }

        r = get_course_request(params=params)
        soup = BeautifulSoup(r, "lxml-xml")
        for section in soup.find_all("section"):
            code = section.find("course_code").text
            new_course_status = section.find("sec_status").text
            current_course_status = [
                v[1] for i, v in enumerate(code_arr) if v[0] == code
            ].pop()
            if new_course_status != current_course_status:
                course = Course.query.filter_by(course_code=code).first()
                course.course_status = new_course_status
                db.session.commit()
                if new_course_status != "FULL" and new_course_status != "NewOnly":
                    self.send_notifications(course)

    def send_notifications(self, course):
        server = None
        failed = True
        while failed:
            try:
                server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
                server.login(config.EMAIL_USERNAME, config.EMAIL_PASSWORD)
                failed = False
            except Exception as e:
                logger.error("Notification Failed: make sure account has 'Less secure app access' enabled (see README)", e)
                time.sleep(5)
        params = {"YearTerm": config.YEAR_TERM, "CourseCodes": course.course_code}
        for user in course.users:
            url = (
                requests.Request("GET", config.WEBSOC_BASE_URL, params=params)
                .prepare()
                .url
            )
            if user.is_receives_email:
                subject = f"[Zotcourse Alarm] {course.course_type} {course.course_department} {course.course_number} is now {course.course_status}"
                text = f"You can now add {course.course_type} {course.course_department} {course.course_number} to your schedule.\n"
                text += f"Code: {course.course_code}\n"
                text += f"Link to Websoc: {url}"
                message = f"From: {config.EMAIL_USERNAME}\nTo: {user.email}\nSubject: {subject}\n\n{text}"
                server.sendmail(config.EMAIL_USERNAME, user.email, message)
            if user.is_receives_text:
                text = f"\n{course.course_type} {course.course_department} {course.course_number} is now {course.course_status}\n"
                text += f"Code: {course.course_code}\n"
                text += url
                phone_email = (
                    f"{user.phone_number}@{self.PHONE_CARRIERS[user.phone_carrier]}"
                )
                message = f"Subject: Zotcourse Alarm\nFrom: {config.EMAIL_USERNAME}\nTo: {phone_email}\n\n{text}"
                server.sendmail(config.EMAIL_USERNAME, phone_email, message)
        server.close()
