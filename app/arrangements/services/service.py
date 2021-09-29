from app import db
from app.arrangements.models import Arrangement, User
from datetime import datetime, timedelta
import bcrypt
from werkzeug.exceptions import BadRequest


class ArrangementService:
	# TODO - Remove this
	@staticmethod
	def get_test():
		arrangement = db.session.query(Arrangement).first()
		return arrangement

	@staticmethod
	def get_all(data):
		arrangements = db.session.query(Arrangement).paginate(page = data.get("page"), per_page = data.get("per_page"))
		return arrangements

	@staticmethod
	def get_available(data, id):
		from_date = datetime.now() + timedelta(days = 5)
		# TODO - Add condition: not reserved by user
		arrangements = db.session.query(Arrangement).filter(Arrangement.start_date >= from_date).paginate(
			page = data.get("page"), per_page = data.get("per_page"))
		return arrangements


class UserService:
	@staticmethod
	def get_by_id(id):
		arrangements = db.session.query(User).filter_by(User.id == id).one_or_none()
		return arrangements

	@staticmethod
	def register(data):
		name = data.get("name")
		surname = data.get("surname")
		email = data.get("email")
		username = data.get("username")
		password = data.get("password")
		type = data.get("type")

		check = db.session.query(User).filter(User.username == username).one_or_none()
		if check:
			raise BadRequest(f"Username {username} already exists")

		password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

		user = User(name, surname, email, username, password_hash, 0)

		if type != 0:
			# TODO - add account type request
			pass

		db.session.add(user)
		db.session.commit()
