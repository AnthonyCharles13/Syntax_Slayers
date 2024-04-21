from App.database import db
class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    description = db.Column(db.String(5000))
    exercise_type = db.Column(db.String(256), nullable=False)  
    bodypart = db.Column(db.String(256), nullable=False)  
    equipment = db.Column(db.String(256), nullable=False)  
    level = db.Column(db.String(256), nullable=False)
    rating = db.Column(db.Float)  
    rating_desc = db.Column(db.String(256)) 

    def get_json(self):  
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'exercises_type': self.type,
            'bodypart': self.bodypart,
            'equipment': self.equipment,
            'level': self.level,
            'rating': self.rating,
            'rating_desc': self.rating_desc
        }