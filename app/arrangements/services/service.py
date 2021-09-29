from app import db
from app.arrangements.models import Arrangement


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
