from flask import Blueprint

from app.forum_api import forum_blueprint
from app.moderator_api import moderator_blueprint
from app.user_api import user_blueprint

api_blueprint = Blueprint("api", __name__)
api_blueprint.register_blueprint(user_blueprint)
api_blueprint.register_blueprint(forum_blueprint)
api_blueprint.register_blueprint(moderator_blueprint)
