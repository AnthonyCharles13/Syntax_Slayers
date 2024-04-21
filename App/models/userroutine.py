from App.database import db
class UserRoutine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)
    routine_name = db.Column(db.String(256), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('user_routines', lazy=True))
    exercise = db.relationship('Exercise')

    def add_exercise(self, exercise_id):
        exercises = Exercise.query.get(exercise_id)
        if exercises:
            try:
                new_exercise = UserRoutine(exercise_id=exercise_id, routine_name=self.routine_name, user_id=self.user_id)
                db.session.add(new_exercise)
                db.session.commit()
                return new_exercise
            except Exception as e:
                print(e)
                db.session.rollback()
                return None
        return None
        
    def remove_exercise(self, exercise_id):
        exercise_to_remove = UserRoutine.query.filter_by(exercise_id=exercise_id, routine_name=self.routine_name, user_id=self.user_id).first()
        if exercise_to_remove:
            db.session.delete(exercise_to_remove)
            db.session.commit()
            return True
        return None

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