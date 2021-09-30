from app import db
from app.arrangements.models import Arrangement, User, TypeChangeRequest, Reservation
from datetime import datetime, timedelta
import bcrypt
from werkzeug.exceptions import BadRequest, NotAcceptable


class ArrangementService:
	@staticmethod
	def get_all(data):
		arrangements = db.session.query(Arrangement).paginate(page = data.get("page"), per_page = data.get("per_page"))
		return arrangements

	@staticmethod
	def get_available(data, id):
		from_date = datetime.now() + timedelta(days = 5)

		reservations = db.session.query(Reservation).filter(Reservation.user_id == id)
		exclude = [ex.arrangement_id for ex in reservations]

		arrangements = db.session.query(Arrangement).filter(Arrangement.start_date >= from_date)
		for ex in exclude:
			arrangements = arrangements.filter(Arrangement.id != ex)
		arrangements = arrangements.paginate(page = data.get("page"), per_page = data.get("per_page"))
		return arrangements

	@staticmethod
	def get_reservations(data, id):
		reservations = db.session.query(Arrangement.start_date, Arrangement.end_date, Arrangement.destination,
			Reservation.count, Reservation.price).join(Arrangement).filter(
			Arrangement.id == Reservation.arrangement_id).filter(Reservation.user_id == id).paginate(
			page = data.get("page"), per_page = data.get("per_page"))
		return reservations

	@staticmethod
	def get_created(data, id):
		arrangements = db.session.query(Arrangement).filter(Arrangement.admin_id == id).paginate(
			page = data.get("page"), per_page = data.get("per_page"))
		return arrangements

	@staticmethod
	def reserve(data, user_id):
		arrangement = db.session.query(Arrangement).filter(Arrangement.id == data.get("arrangement_id")).one_or_none()
		count = data.get("count")
		if count > arrangement.vacancies:
			raise NotAcceptable("Not enough vacancies")

		arrangement.vacancies = arrangement.vacancies - count

		price_of_one = arrangement.price
		price = count * price_of_one if count <= 3 else 3 * price_of_one + (count - 3) * price_of_one * 0.9

		reservation = Reservation(count, price, user_id, arrangement.id)

		db.session.add(reservation)
		db.session.commit()

		return reservation


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

		db.session.add(user)
		db.session.flush()

		if type != 0:
			request = TypeChangeRequest(type, user.id)
			db.session.add(request)

		db.session.commit()

		return user

	@staticmethod
	def request_type_change(new_type, user_id):
		request = db.session.query(TypeChangeRequest).filter(TypeChangeRequest.user_id == user_id).one_or_none()
		if request is not None:
			request.type = new_type
			request.accepted = None
			request.comment = None
		else:
			request = TypeChangeRequest(new_type, user_id)
			db.session.add(request)

		db.session.commit()

	@staticmethod
	def get_request_by_user_id(user_id):
		request = db.session.query(TypeChangeRequest).filter(TypeChangeRequest.user_id == user_id).one_or_none()
		return request
