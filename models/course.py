from models.db import db


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(10), nullable=False)
    course_department = db.Column(db.String(20), nullable=False)
    course_type = db.Column(db.String(10), nullable=False)
    course_number = db.Column(db.String(10), nullable=False)
    course_status = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return "<Course %r>" % self.course_code
