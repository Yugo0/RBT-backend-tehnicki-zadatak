from app import db


class Arrangement(db.Model):
	__tablename__ = "arrangements"
	id = db.Column(db.Integer, primary_key = True)
	start_date = db.Column(db.DateTime(timezone = True), nullable = False)
	end_date = db.Column(db.DateTime(timezone = True), nullable = False)
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


class User(db.Model):
	__tablename__ = "users"
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String, nullable = False)
	surname = db.Column(db.String, nullable = False)
	email = db.Column(db.String, nullable = False)
	username = db.Column(db.String, nullable = False)
	password_hash = db.Column(db.String, nullable = False)
	type = db.Column(db.Integer, nullable = False)  # 0 - TOURIST, 1 - TRAVEL GUIDE, 2 - ADMIN

	type_change_requests = db.relationship("TypeChangeRequest", backref = "users", lazy = True)

	def __init__(self, name, surname, email, username, password_hash, type):
		self.name = name
		self.surname = surname
		self.email = email
		self.username = username
		self.password_hash = password_hash
		self.type = type


class TypeChangeRequest(db.Model):
	__tablename__ = "type_change_requests"

	id = db.Column(db.Integer, primary_key = True)
	type = db.Column(db.Integer, nullable = False)  # 0 - TOURIST, 1 - TRAVEL GUIDE, 2 - ADMIN
	accepted = db.Column(db.Boolean())
	comment = db.Column(db.String())
	user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable = False)

	def __init__(self, type, user_id):
		self.type = type
		self.user_id = user_id
