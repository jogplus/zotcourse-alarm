import logging
import phonenumbers as pn
import helper
import background_job
from flask import Flask, render_template, session, redirect, request, url_for
from email_validator import validate_email, EmailNotValidError
from models import db, User, Course, User_Course
from config import Config as config

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.root.setLevel(logging.INFO)
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = config.DB_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = config.SECRET_KEY
db.init_app(app)
bgj = background_job.BackgroundJob(app)


@app.route("/")
def index():
    user_id = session.get("user_id")
    if user_id:
        user = User.query.get(user_id)
        if not user:
            return redirect(url_for("logout"))
        return render_template("index.html", user=user, courses=user.courses)
    return render_template("index.html")


@app.route("/course", methods=["POST"])
def add_course():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("index"))
    course_code = request.form.get("course_code")
    if not course_code:
        return redirect(url_for("index"))
    course = Course.query.filter_by(course_code=course_code).first()
    user = User.query.get(user_id)
    if course:
        # Don't have to check if user already added course
        user.courses.append(course)
        db.session.commit()
    else:
        course = helper.get_course_info(course_code, bgj.year_term)
        user.courses.append(course)
        db.session.commit()
    return redirect(url_for("index"))


@app.route("/course/delete")
def remove_course():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("index"))
    course_id = request.args.get("id")
    if not course_id:
        return redirect(url_for("index"))

    user = User.query.get(user_id)
    course = Course.query.get(course_id)
    user.courses.remove(course)

    # Remove course from Course table if no other users have it added
    user_courses = db.session.query(User_Course).filter_by(course_id=course_id).all()
    if not user_courses:
        db.session.delete(course)

    db.session.commit()
    return redirect(url_for("index"))


@app.route("/user", methods=["POST"])
def update_user():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("index"))
    user = User.query.get(user_id)
    user.is_receives_email = bool(request.form.get("is-receives-email"))
    user.is_receives_text = bool(request.form.get("is-receives-text"))
    if user.is_receives_text:
        try:
            phone_number = pn.parse(request.form.get("phone-number"), "US")
            if not pn.is_valid_number(phone_number):
                raise pn.NumberParseException
            user.phone_number = phone_number.national_number
            user.phone_carrier = int(request.form.get("phone-carrier"))
        except Exception:
            return redirect(url_for("index"))
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/login", methods=["POST"])
def login():
    # already logged in
    if session.get("user_id"):
        return redirect(url_for("index"))
    email = request.form.get("email")

    # missing email
    if not email:
        return redirect(url_for("index"))

    try:
        v = validate_email(email, allow_smtputf8=False)
        email = v["email"]  # replace with normalized form
    except EmailNotValidError:
        # email is not valid, exception message is human-readable
        return redirect(url_for("index"))

    user_id = db.session.query(User.id).filter_by(email=email).scalar()
    if user_id:
        # already registered
        session["user_id"] = user_id
    else:
        user = User(email=email)
        db.session.add(user)
        db.session.commit()
        session["user_id"] = user.id
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session["user_id"] = None
    return redirect(url_for("index"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        background_job.start(bgj)
    helper.register_url()
    app.run(port=config.PORT, debug=False, use_reloader=False)
