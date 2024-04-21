from App.database import db
from App.models import Exercise
class UserRoutine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=True)
    routine_name = db.Column(db.String(256), nullable=False, unique=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('user_routines', lazy=True))
    exercise = db.relationship('Exercise')

    def __init__(self, routine_name, user_id):
        self.routine_name = routine_name
        self.user_id = user_id

    def add_exercise(self, exercise_id):
        exercise = Exercise.query.get(exercise_id)
        if exercise:
            self.exercises.append(exercise)
            db.session.commit()
            return True
        return False
        
    def remove_exercise(self, exercise_id):
        exercise = Exercise.query.get(exercise_id)
        if exercise in self.exercises:
            self.exercises.remove(exercise)
            db.session.commit()
            return True
        return False

    def clear_routine(self):
        exercises = UserRoutine.query.filter_by(routine_name=self.routine_name, user_id=self.user_id).all()
        for exercise in exercises:
            db.session.delete(exercise)
        db.session.commit()

    def get_exercises(self):
        exercises = UserRoutine.query.filter_by(routine_name=self.routine_name, user_id=self.user_id).all()
        return exercises

    def update_routine_name(self, new_name):
        self.routine_name = new_name
        db.session.commit()

    @staticmethod
    def get_user_routines(user_id):
        user_routines = UserRoutine.query.filter_by(user_id=user_id).all()
        return user_routines