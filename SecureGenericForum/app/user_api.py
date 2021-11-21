from flask import Blueprint, session
from flask import session
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash
from time import sleep
from flask_login import current_user, login_required, logout_user, login_user
from flask_login.utils import login_user
from sqlalchemy.orm.exc import UnmappedInstanceError
from app.core.forum_action import *
from app.app import login_manager, db
from app.srptools import SRPContext, SRPContext, SRPServerSession
from app.srptools.constants import HASH_SHA_256
from app.core.aesgcm import crypto as AES
import logging
import pyotp
import qrcode
import base64
import io
import requests
from datetime import datetime, timedelta
from app.core.upload_validate import image_validation
from app.core.email import *
from .core.sec_util import Util
from app.core.model import UserModel

logger = logging.getLogger(__name__)
user_blueprint = Blueprint("user", __name__)

# Shared func to edit image. Used by /user/rename


def edit_image(request, own_flag, user):
    if 'file' in request.files:
        file = request.files['file']

        # Image Sanitization
        if image_validation(file):
            if own_flag:
                EditOwnProfileImage(file).perform(user)
            else:
                EditOthersProfileImage(file, request.form['id']).perform(user)


def is_human(captcha_response):
    """ Validating recaptcha response from google server
        Returns True captcha test passed for submitted form else returns False.
    """
    secret = str(app.config['RECAPTCHA_SECRET'])
    payload = {'response': captcha_response, 'secret': secret}
    try:
        response = requests.post(
            "https://www.google.com/recaptcha/api/siteverify", payload)
        result = response.json()

        if result['success']:
            return True

    except:
        return False

    return False


@login_manager.user_loader
def load_user(id):

    return db.session.get(UserModel, id)


def logged_in_check():
    id = session.get('id')
    pass_2fa = session.get('pass_2fa')
    try:
        if id is None:
            return False, "ERROR"

        if id is not None and pass_2fa is True:
            user_session_dist = QueryUserInstance(id).perform()
            login_time = user_session_dist['time'] if user_session_dist['time'] is not None else False
            if login_time:
                timeNow = datetime.now()
                end_time = (datetime.fromisoformat(
                    str(login_time))) + timedelta(minutes=30)
                if end_time > timeNow:
                    return True, "LOGIN"
                else:
                    return False, "LOGOUT"

        return False, "OTP"
    except:
        return False, "ERROR"


@user_blueprint.route("/verify", methods=["POST"])
def verify_process():

    if request.method == "POST":

        data = request.get_json(force=True)
        # Verify if result is a dict and contents are alpha numeric
        san_data = Util(data).is_dict_and_alphanumeric()

        if san_data:
            return VerifyUser().perform(san_data)

    return {}


@user_blueprint.route("/login", methods=["GET", "POST"])
def login_page():

    session_bool, text = logged_in_check()

    if session_bool:
        return redirect(url_for("api.forum.home"))
    elif text == "LOGOUT":
        return redirect(url_for("api.user.logout"))

    if request.method == "GET":
        return render_template("login.html")

    elif request.method == "POST":

        try:
            # Ensuring form has the required fields
            if not('email' in request.form and 'login-clientpub' in request.form and 'login-m1' in request.form and 'g-recaptcha-response' in request.form and len(request.form) == 5):
                flash("Invalid request")
                return render_template("login.html")

            email = request.form.get('email')
            clientpub = request.form.get('login-clientpub')
            m1 = request.form.get('login-m1')
            recaptcha = request.form.get('g-recaptcha-response')

            # Checking min and max length of captcha
            if not (Util(recaptcha, 1, 600).check_bound() and is_human(recaptcha)):
                flash("Recaptcha is invalid", "danger")
                return render_template("login.html")

            # Checking min and max length
            if not (Util(email, 1, 100).check_bound() and Util(clientpub, 1, 1000).check_bound() and Util(m1, 1, 1000).check_bound()):

                flash("Invalid length in either Email or password", "danger")
                return render_template("login.html")

            # Checking if is an email, alphanumeric and if user exists
            if not (Util(email).is_email() and Util(clientpub).is_alnum() and Util(m1).is_alnum() and CheckUserModelEmail(email).perform()):
                flash("Incorrect email/password or account is not verified", "danger")
                return render_template("login.html")

            # Storing sanitised values
            san_email = Util(email).is_email()
            san_clientpub = Util(clientpub).is_alnum()
            san_m1 = Util(m1).is_alnum()
            try:
                result, id, key = ConfirmLogin(
                    san_email, san_clientpub, san_m1).perform()
            except:
                flash("Incorrect email/password or account is not verified", "danger")
                return render_template("login.html")

            if result:

                ip_location = str(request.access_route[0])
                browser_header = str(request.headers.get('User-Agent'))
                encryption_key = key.decode()
                LoginInstance(id, ip_location, browser_header,
                              encryption_key).perform()
                session.clear()
                session['pass_2fa'] = False
                session['id'] = id

                return redirect(url_for("api.user.otp_page"))

            else:
                flash("Incorrect email/password or account is not verified", "danger")
                return render_template("login.html")

        except:
            flash("Incorrect email/password or account is not verified", "danger")
            return redirect(url_for('api.user.login_page'))

    else:
        flash("Incorrect email/password or account is not verified", "danger")
        return redirect(url_for('api.user.login_page'))

# Allow user to reset their password
@user_blueprint.route("/reset", methods=["GET"])
def reset():

    session_bool, text = logged_in_check()

    if session_bool:
        return redirect(url_for("api.forum.home"))
    elif text == "LOGOUT":
        return redirect(url_for("api.user.logout"))

    if request.method == "GET":
        return render_template("forget_password.html")

    return redirect(url_for('api.user.login_page'))

# Function to send email to user
@user_blueprint.route("/reset/email", methods=["POST"])
async def email():
    if request.method == "POST":
        try:
            # Ensuring form has the required fields
            if not('email' in request.form and 'g-recaptcha-response' in request.form and len(request.form) == 3):
                flash("Invalid request", "danger")
                return redirect(url_for('api.user.reset'))

            email = request.form.get('email')
            recaptcha = request.form.get('g-recaptcha-response')

            # Checking min and max length of captcha
            if not (Util(recaptcha, 1, 600).check_bound() and is_human(recaptcha)):
                flash("Recaptcha is invalid", "danger")
                return redirect(url_for('api.user.reset'))

            # Checking min, max length and email
            if not (Util(email).is_email() and Util(email, 1, 100).check_bound()):
                flash("Invalid email format", "danger")
                return redirect(url_for('api.user.reset'))

            # Storing sanitised value
            san_email = Util(email).is_email()

            # Wait for email result
            result = await reset_mail(san_email)

            # If fail sleep
            if result is False:
                sleep(2)

            flash("Reset Email Sent", "success")
            return redirect(url_for('api.user.reset'))
        except:
            flash("Reset Email Sent", "success")
            return redirect(url_for('api.user.reset'))

    else:
        return redirect(url_for('api.user.login_page'))

# Function to reset token and reset password
@user_blueprint.route("/reset/token", methods=["POST"])
@user_blueprint.route("/reset/token/<token>", methods=["GET"])
def reset_token(token=None):

    if request.method == "GET":

        # Checking min, max length and token
        if not (Util(token).check_token() and Util(token, 1, 200).check_bound()):
            flash("Token is invalid or expired", "danger")
            return redirect(url_for('api.user.reset'))

        # Storing sanitised token
        san_token = Util(token).check_token()

        # Validating token
        token_result = validate_token(san_token)

        # Reset password if pass
        if token_result:
            return render_template("reset_password.html", email=token_result, token=token)

        flash("Token is invalid or expired", "danger")
        return redirect(url_for('api.user.reset'))

    elif request.method == "POST":

        try:
            # Ensuring form has the required fields
            if not('token' in request.form and 'email' in request.form and 'verifier' in request.form and 'salt' in request.form and len(request.form) == 5):
                flash("Invalid request")
                return redirect(url_for('api.user.reset'))

            token = request.form.get('token')
            email = request.form.get('email')
            verifier = request.form.get('verifier')
            salt = request.form.get('salt')

            # Checking min, max length and token
            if not (Util(token).check_token() and Util(token, 1, 200).check_bound()):
                flash("Token is invalid or expired", "danger")
                return redirect(url_for('api.user.reset'))

            # Checking min, max length and email
            if not (Util(email).is_email() and Util(email, 1, 100).check_bound()):
                flash("Email is invalid", "danger")
                return redirect(url_for('api.user.reset'))

            # Checking min, max length and salt, verifier is alpha numeric
            if not (Util(verifier).is_alnum() and Util(salt).is_alnum() and Util(verifier, 1, 600).check_bound() and Util(salt, 1, 100).check_bound()):
                flash("Incorrect email or password", "danger")
                return redirect(url_for("api.user.login_page"))

            # Storing sanitised variable
            san_token = Util(token).check_token()
            san_email = Util(email).is_email()
            san_salt = Util(salt).is_alnum()
            san_verifier = Util(verifier).is_alnum()

            # Validating token
            token_result = validate_token(san_token)

            if str(token_result) == str(san_email):
                result = CheckUserModelEmail(san_email).perform()
                if result:
                    ResetPassword(san_salt, san_verifier, san_email).perform()
                    flash("Password Changed", "success")
                    return redirect(url_for("api.user.login_page"))

            flash("Token is invalid or expired", "danger")
            return redirect(url_for('api.user.reset'))
        except:
            flash("Token is invalid or expired", "danger")
            return redirect(url_for('api.user.reset'))

    else:

        return redirect(url_for("api.user.login_page"))


@user_blueprint.route("/register", methods=["GET", "POST"])
async def register_page():

    session_bool, text = logged_in_check()

    if session_bool:
        return redirect(url_for("api.forum.home"))
    elif text == "LOGOUT":
        return redirect(url_for("api.user.logout"))

    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":
        try:
            # Ensuring form has the required fields
            if not('name' in request.form and 'email' in request.form and 'verifier' in request.form and 'salt' in request.form and 'g-recaptcha-response' in request.form and len(request.form) == 6):
                flash("Invalid request")
                return render_template("register.html")

            name = request.form.get('name')
            email = request.form.get('email')
            salt = request.form.get('salt')
            verifier = request.form.get('verifier')
            recaptcha = request.form.get('g-recaptcha-response')

            # Checking min, max length and email
            if not (Util(recaptcha, 1, 600).check_bound() and is_human(recaptcha)):
                flash("Recaptcha is invalid", "danger")
                return render_template("register.html")

            # Checking min, max length and alphanumeric of name
            if not (Util(name).is_alnum() and Util(name, 1, 50).check_bound()):
                flash("Username is invalid", "danger")
                return render_template("register.html")

            # Checking min, max length and format of email
            if not (Util(email).is_email() and Util(email, 1, 100).check_bound()):
                flash("Email is invalid", "danger")
                return render_template("register.html")

            # Checking min, max length and salt, verifier is alpha numeric
            if not (Util(verifier).is_alnum() and Util(salt).is_alnum() and Util(verifier, 1, 600).check_bound() and Util(salt, 1, 100).check_bound()):
                flash("Incorrect email or password", "danger")
                return render_template("register.html")

            # Storing sanitised variable
            san_name = Util(name).is_alnum()
            san_email = Util(email).is_email()
            san_salt = Util(salt).is_alnum()
            san_verifier = Util(verifier).is_alnum()

            success, error = RegisterUser(
                san_name, san_email, san_salt, san_verifier, 3, None).perform()

            if not success:
                flash("Email Exists", "danger")
                return render_template("register.html")

            else:

                await verify_mail(san_email)
                flash("Please verify your email within 5mins before logging in", "success")
                return redirect(url_for('api.user.login_page'))
        except:
            flash("Invalid Request", "danger")
            return render_template("register.html")

    return redirect(url_for('api.user.login_page'))

# function to verifiy token from email
@user_blueprint.route("/verify/token/<token>", methods=["GET"])
def verify_token(token=None):

    session_bool, text = logged_in_check()

    if session_bool:
        return redirect(url_for("api.forum.home"))
    elif text == "LOGOUT":
        return redirect(url_for("api.user.logout"))

    if request.method == "GET":

        # Checking min, max length and format of token
        if not (Util(token).check_token() and Util(token, 1, 200).check_bound()):
            flash("Token is invalid or expired", "danger")
            return redirect(url_for('api.user.login_page'))

        # Storing sanitised varibale
        san_token = Util(token).check_token()

        # Validating token
        token_result = validate_token(san_token)

        # if validated up the db
        if token_result:
            try:
                UpdateUserModelEmailVerified(token_result).perform()
                flash("Email verified successfully", "success")
                return redirect(url_for('api.user.login_page'))

            except:
                flash("Email verified failed, token is invalid or expired", "danger")
                return redirect(url_for("api.user.login_page"))

        else:

            flash("Token is invalid or expired", "danger")
            return redirect(url_for('api.user.login_page'))

    return redirect(url_for("api.user.login_page"))


@user_blueprint.route("/otp", methods=["GET", "POST"])
def otp_page():

    session_bool, text = logged_in_check()

    if text == "LOGOUT":
        return redirect(url_for("api.user.logout"))

    id = session.get('id')
    pass_2fa = session.get('pass_2fa')

    if id is not None and pass_2fa is True:
        return redirect(url_for("api.forum.home"))

    elif id is None:
        return redirect(url_for('api.user.login_page'))

    email = GetUserModel(id).perform().email
    otp_server_key = str(app.config['OTP_SECRET'])
    db_otp = CheckOTP(id).perform()

    if db_otp is None:
        has_otp = False
    else:
        has_otp = True

    if request.method == "GET" and pass_2fa is False:

        if has_otp:
            return render_template("otp.html", email=email, has_otp=has_otp)

        else:

            otp_secret = pyotp.random_base32()

            otp_link = pyotp.totp.TOTP(otp_secret).provisioning_uri(
                name=email, issuer_name='SecureGenericForum')

            if has_otp:
                return render_template("otp.html", email=email, has_otp=has_otp)
            else:
                otp_secret = pyotp.random_base32()
                otp_link = pyotp.totp.TOTP(otp_secret).provisioning_uri(
                    name=email, issuer_name='SecureGenericForum')

                encrypted_otp = str(
                    AES(otp_server_key).encrypt(str(otp_secret)))

                UpdateOTP(email, encrypted_otp).perform()
                otp_img = qrcode.make(otp_link)
                buffered = io.BytesIO()
                otp_img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

                return render_template("otp.html", email=email, has_otp=has_otp, img_str=img_str, id=id)

    elif request.method == "POST" and pass_2fa is False:
        try:
            # Ensuring form has the required fields
            if not('otp' in request.form and len(request.form) == 2):
                flash("Invalid request")
                return render_template("otp.html", email=email, has_otp=has_otp)

            form_otp = request.form.get('otp')

            # Checking min, max length and format of otp
            if not (Util(form_otp).is_string() and Util(form_otp, 1, 1000).check_bound()):
                flash("Incorrect OTP", "danger")
                return render_template("otp.html", email=email, has_otp=has_otp)

            # Storing sanitised variable
            san_form_otp = Util(form_otp).is_string()

            # Decrypt
            try:
                user_session_dist = QueryUserInstance(id).perform()
                otp_decrypt = AES(user_session_dist["encryption_key"]).decrypt(
                    str(san_form_otp))

                # Ensuring form has the required fields
                if not (Util(otp_decrypt).is_string_only_num() and len(otp_decrypt) == 6):
                    flash("Incorrect OTP", "danger")
                    return render_template("otp.html", email=email, has_otp=has_otp)

            except:
                otp_decrypt = False

            if otp_decrypt:

                try:
                    decrypted_otp = str(
                        AES(otp_server_key).decrypt(str(db_otp)))

                except:

                    return redirect(url_for('api.forum.home'))

                otp_session = pyotp.TOTP(decrypted_otp)
                success_otp = otp_session.verify(otp_decrypt)

                if success_otp is True:

                    session['pass_2fa'] = True
                    user = GetUserModel(id).perform()
                    login_user(user)
                    return redirect(url_for('api.forum.home'))

                else:
                    # fail_count + 1
                    LoginFailCount(id).perform()
                    flash("Incorrect OTP", "danger")
                    return render_template("otp.html")

            else:
                # fail_count + 1
                LoginFailCount(id).perform()
                flash("Incorrect OTP", "danger")  # change to account logck
                return render_template("otp.html")
        except:
            # fail_count + 1
            LoginFailCount(id).perform()
            flash("Incorrect OTP", "danger")  # change to account logck
            return render_template("otp.html")

    elif pass_2fa is True:
        return redirect(url_for('api.forum.home'))

    else:
        return redirect(url_for('api.user.login_page'))


@user_blueprint.route("/logout")
@login_required
def logout():
    try:
        session.clear()
    except UnmappedInstanceError as e:
        pass
    logout_user()
    return redirect(url_for('api.user.login_page'))


@user_blueprint.route("/user")
@user_blueprint.route("/user/<id>")
@login_required
def profile_page(id=None):
    error_msg = "Unexpected error"

    session_bool, text = logged_in_check()

    if text == "LOGOUT":
        return redirect(url_for("api.user.logout"))

    try:
        user_id = session.get('id')
        pass_2fa = session.get('pass_2fa')

        if user_id is None:
            return redirect(url_for('api.user.login_page'))

        elif user_id is not None and pass_2fa is False:
            return redirect(url_for("api.user.otp_page"))

        # Checking id is string and is numeric
        if not(Util(id).is_string_only_num()):
            target_user_id = user_id
            id = user_id

        else:

            # Storing sanitised variable
            target_user_id = id if Util(id).is_string_only_num() else user_id

        user = GetUserModel(user_id).perform()

        invoker_user = ViewUserProfile(user_id).perform(user)
        target_user = ViewUserProfile(target_user_id).perform(user)

        # Do authorization check for frontend display of buttons
        edit_flag = True if ROLES[invoker_user['role_name']] < ROLES[target_user['role_name']] \
            and ROLES[invoker_user['role_name']] != ROLES[ROLE_ADMIN] \
            or target_user['id'] == int(user_id) else False

        ban_flag = True if ROLES[invoker_user['role_name']] < ROLES[target_user['role_name']] \
            and ROLES[invoker_user['role_name']] == ROLES[ROLE_MODERATOR] \
            and target_user['id'] != int(user_id) else False

    except Exception as e:
        logger.error(e)
        flash(error_msg)
        return redirect(url_for("api.user.profile_page"))

    return render_template("profile.html", user=target_user, edit_flag=edit_flag, ban_flag=ban_flag)


@user_blueprint.route("/user/rename", methods=["POST"])
@login_required
def rename_user():
    error_msg = "Unexpected error"

    try:

        user_id = session.get('id')
        pass_2fa = session.get('pass_2fa')

        if user_id is None:
            return redirect(url_for('api.user.login_page'))

        elif user_id is not None and pass_2fa is False:
            return redirect(url_for("api.forum.otp_page"))

        # Ensuring form has the required fields
        if not('name' in request.form and 'id' in request.form and len(request.form) == 3):
            flash("Invalid request")
            return redirect(url_for("api.user.home"))

        name = request.form['name']
        target_user_id = request.form['id']

        # Checking name is alphanumeric and length
        if not (Util(name).is_alnum() and Util(name, 1, 50).check_bound()):
            return redirect(request.headers['Referer'])

        # Checking target_user_id is string and only has numbers
        if not (Util(target_user_id).is_string_only_num()):
            return redirect(request.headers['Referer'])

        # Checking name is alphanumeric
        san_name = name if Util(name).is_alnum() else None
        san_target_user_id = target_user_id if Util(
            target_user_id).is_string_only_num() else None

        user = GetUserModel(session['id']).perform()
        own_flag = (session['id'] == request.form['id'])

        if own_flag:
            EditOwnProfileName(san_name).perform(user)
            edit_image(request, own_flag, user)
        else:
            EditOthersProfileName(name, san_target_user_id).perform(user)
            edit_image(request, own_flag, user)

    except Exception as e:
        logger.error(e)
        flash(error_msg)

    return redirect(request.headers['Referer'])
