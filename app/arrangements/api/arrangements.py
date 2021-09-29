from app.arrangements import arrangement_bp
from flask import request
from app.arrangements.schemas import ArrangementBasicResponseSchema, ArrangementFullResponseSchema, MetaSchema, \
	ArrangementsBasicResultSchema, ArrangementsFullResultSchema
from app.arrangements.services import ArrangementService

arrangement_basic_response_schema = ArrangementBasicResponseSchema()
arrangement_full_response_schema = ArrangementFullResponseSchema()
meta_schema = MetaSchema()
arrangements_basic_result_schema = ArrangementsBasicResultSchema()
arrangements_full_result_schema = ArrangementsFullResultSchema()


# TODO - Remove this
@arrangement_bp.get("test")
def get_test():
	arrangement = ArrangementService.get_test()

	return arrangement_full_response_schema.dump(arrangement)


@arrangement_bp.get("all")
def get_all():
	data = meta_schema.load(request.args.to_dict())

	# TODO - Grab data according to user type
	arrangements = ArrangementService.get_all(data = data)

	return arrangements_basic_result_schema.dump(arrangements)
