import logging

from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flask_login import login_required, current_user

from app.app import app as app_config
from app.core.forum_action import *
from app.core.sec_util import Util
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
moderator_blueprint = Blueprint("moderator", __name__)


def logged_in_check():
    id = session.get('id')
    pass_2fa = session.get('pass_2fa')
    try:
        if id is None:
            return False, "LOGOUT"

        if id is not None and pass_2fa is True:
            user_session_dist = QueryUserInstance(id).perform()
            login_time = user_session_dist['time'] if user_session_dist['time'] is not None else False
            if login_time:
                timeNow = datetime.now()
                end_time = (datetime.fromisoformat(str(login_time))) + \
                    timedelta(minutes=30)
                if end_time > timeNow:
                    return True, "LOGIN"
                else:
                    return False, "LOGOUT"

        return False, "OTP"
    except:
        return False, "ERROR"


# this route is use specifally for selenium ui testing to set the session
@moderator_blueprint.route("/test/session", methods=["GET"])
@login_required
def test_session():
    if app_config.config['TESTING'] == True:
        session.clear()
        session['id'] = app_config.config['TEST_SESSION_MOD']
        session['pass_2fa'] = True

        return redirect(url_for("api.forum.home"))
    else:
        return "Invalid page", 404


@moderator_blueprint.route("/moderator/ban", methods=["POST"])
# @login_required
def ban_user():
    form_data = dict(request.form)
    error_msg = "Unexpected error"

    session_bool, text = logged_in_check()

    if text == "LOGOUT":
        return redirect(url_for("api.user.logout"))

    try:
        user_id = int(session['id'])
        target_id = int(form_data['id'])
        action = BanUser(user_id, target_id)
        allowed, error_messages = action.is_user_allowed(UserInstanceModel.query.get(user_id))

        if not allowed:
            raise Exception("\n".join(error_messages))

        success, msg = action.perform()
        if not success:
            raise Exception(msg)

    except Exception as e:
        logger.error(e)
        flash(error_msg)

    return redirect(request.headers['Referer'])


@moderator_blueprint.route("/moderator/unban", methods=["POST"])
@login_required
def unban_user():
    form_data = dict(request.form)
    error_msg = "Unexpected error"
    session_bool, text = logged_in_check()

    if text == "LOGOUT":
        return redirect(url_for("api.user.logout"))

    try:
        success, msg = UnbanUser(int(session['id']), form_data['id']).perform()
        if not success:
            raise Exception(msg)
    except Exception as e:
        logger.error(e)
        flash(error_msg)

    return redirect(request.headers['Referer'])


# No Error message because admin page is hidden.
# Verbose Error messages may expose system.
# By default, re-routes to home
@moderator_blueprint.route("/admin/home", methods=["GET"])
@login_required
def admin_page():
    try:

        session_bool, text = logged_in_check()

        if text == "LOGOUT":
            return redirect(url_for("api.user.logout"))

        user_id = session['id']

        if user_id != 1:
            return "Invalid page", 404

        user = GetUserModel(user_id).perform()
        user_profile = ViewUserProfile(user_id).perform(user)

        action = ViewUserProfile(user_id)
        allowed, error_messages = action.is_user_allowed(user)
        if allowed:
            action.perform(user)
        else:
            flash(error_messages)

        # Only allow user to access admin page IF role == admin
        if ROLES[user_profile['role_name']] == ROLES[ROLE_ADMIN]:
            user_list = GetAllUsers().perform(user)
            return render_template("admin.html", user_list=user_list, roles=[ROLE_USER, ROLE_MODERATOR])
    except Exception as e:
        logger.error(e)
        # return "Invalid page", 404

    return render_template("admin.html")


@moderator_blueprint.route("/admin/update", methods=["POST"])
@login_required
def admin_update():
    form_data = dict(request.form)
    error_msg = "Unexpected error"

    session_bool, text = logged_in_check()

    if text == "LOGOUT":
        return redirect(url_for("api.user.logout"))

    if request.method == "POST":

        try:

            user_id = session['id']
            user = GetUserModel(user_id).perform()

            if user_id != 1:
                return "Invalid page", 404

            target_user_id = form_data['user_id']  # TODO: VALIDATE
            role_name = form_data['role_name']  # TODO: VALIDATE
            print(role_name)
            print(target_user_id)
            # Checking target_user_id is string and only has numbers
            if Util(target_user_id).is_string_only_num():
                san_target_user_id = Util(target_user_id).is_string_only_num()
            else:
                error_msg = "Input error"
                raise KeyError(error_msg)

            # Checking role_name is alphanumeric
            if Util(role_name).is_string_alpha():
                san_role_name = Util(role_name).is_string_alpha()
            else:
                error_msg = "Input error"
                raise KeyError(error_msg)

            print(san_role_name)
            print(san_target_user_id)
            AdminEditRole(san_role_name, san_target_user_id).perform(user)

        except Exception as e:
            logger.error(e)
            flash(error_msg)

    else:
        return redirect(url_for("api.moderator.admin_page"))

    return redirect(url_for("api.moderator.admin_page"))
