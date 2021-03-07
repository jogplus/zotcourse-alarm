from models.db import db

# https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/#many-to-many-relationships
User_Course = db.Table(
    "user_course",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("course_id", db.Integer, db.ForeignKey("course.id"), primary_key=True),
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20))
    phone_carrier = db.Column(db.Integer)
    is_receives_text = db.Column(db.Boolean, default=False)
    is_receives_email = db.Column(db.Boolean, default=True)
    courses = db.relationship(
        "Course",
        secondary=User_Course,
        lazy=True,
        backref=db.backref("users", lazy=True),
    )

    def __repr__(self):
        return "<User %r>" % self.email
