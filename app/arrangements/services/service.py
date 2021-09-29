from app import db
from app.arrangements.models import Arrangement, User
from datetime import datetime, timedelta
import bcrypt
from werkzeug.exceptions import BadRequest


class ArrangementService:
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
		user = db.session.query(User).filter(User.id == id).one_or_none()
		return user

	@staticmethod
	def get_by_username(username):
		user = db.session.query(User).filter(User.username == username).one_or_none()
		return user

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

		password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

		user = User(name, surname, email, username, password_hash, 0)

		if type != 0:
			# TODO - Add account type request
			pass

		db.session.add(user)
		db.session.commit()

		return user
