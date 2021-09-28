from flask import Blueprint


arrangement_bp = Blueprint("arrangement", __name__, url_prefix = "/api/arrangements")

import app.arrangements.api
