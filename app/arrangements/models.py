from app import db


class Arrangement(db.Model):
	__tablename__ = 'arrangements'
	id = db.Column(db.Integer, primary_key = True)
	start_date = db.Column(db.DateTime(timezone = True))
	end_date = db.Column(db.DateTime(timezone = True))
	description = db.Column(db.String, nullable = False)
	destination = db.Column(db.String, nullable = False)
	vacancies = db.Column(db.Integer, nullable = False)
	price = db.Column(db.Float, nullable = False)

	def __init__(self, start_date, end_date, description, destination, vacancies, price):
		self.start_date = start_date
		self.end_date = end_date
		self.description = description
		self.destination = destination
		self.vacancies = vacancies
		self.price = price
