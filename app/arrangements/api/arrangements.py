from app import db
from app.arrangements import arrangement_bp
from app.arrangements.models import Arrangement
from app.arrangements.schemas import ArrangementsBasicResponseSchema

arrangement_basic_response_schema = ArrangementsBasicResponseSchema()


@arrangement_bp.get('/test')
def get_test():
	arrangement = db.session.query(Arrangement).first()

	return arrangement_basic_response_schema.dump(arrangement)
