from flask import Blueprint, session
from flask import render_template
from flask import request
from flask import redirect
from flask import flash
from flask_wtf import csrf
from flask.helpers import url_for
from flask_login import login_required
from datetime import datetime, timedelta
from app.core.aesgcm import crypto as AES

from app.core.forum_action import * 
from app.core.sec_util import Util
from app.app import app

import logging

logger = logging.getLogger(__name__)
forum_blueprint = Blueprint("forum", __name__)


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


@forum_blueprint.route("/home", methods=["GET"])
@forum_blueprint.route("/home/<page>", methods=["GET"])
@login_required
def home(page="1"):
    
    curr_page, total_page = 1, 1
    error_msg = "Unexpected error"

    session_bool, text = logged_in_check()

    if text == "LOGOUT":
        return redirect(url_for("api.user.logout"))

    try:
        # Check if page is a string and only contains numbers else return invalid
        if Util(page).is_string_only_num(): 
            # Store sanitised variable
            san_page = Util(page).is_string_only_num()
        else:
            return "Invalid page", 404
        
        user_id = session.get('id')

        user = GetUserModel(user_id).perform()
        invoker_user = ViewUserProfile(user_id).perform(user)
        categories_list = ListForumCategories().perform(user, int(san_page)) # returns [] or error message


        if categories_list != []:
            curr_page, total_page = categories_list[0]['page'], categories_list[0]['total_page']
        mod_flag = True if ROLES[invoker_user['role_name']] == ROLES[ROLE_MODERATOR] else False 

        #encrypt
        if not app.config['TESTING']:
            
            user_encryption_key = QueryUserInstance(user_id).perform()["encryption_key"]
            for element in categories_list:
                for key, value in element.items():
                    if key == "name":
                        element[key] = str(AES(user_encryption_key).encrypt(str(value)))
    
    except Exception as e:
        logger.error(e)
        return "Invalid page", 404

    return render_template("home.html", categories=categories_list,
            page=curr_page, total_page=total_page, user=invoker_user, mod_flag=mod_flag)


@forum_blueprint.route("/category/<id>", methods=["GET"])
@forum_blueprint.route("/category/<id>/<page>", methods=["GET"])
@login_required
def category_page(id, page="1"):
    curr_page, total_page = 1, 1
    user_id = session.get('id')
    
    session_bool, text = logged_in_check()

    if text == "LOGOUT":
        return redirect(url_for("api.user.logout"))
    
    try: 
        # Check if id is a string and only contains numbers else return invalid
        if Util(id).is_string_only_num():
            # Store sanitised variable
            san_id = int(Util(id).is_string_only_num())
        else:
            return "Invalid page", 404
        
        # Check if page is a string and only contains numbers else return invalid
        if Util(page).is_string_only_num(): 
            # Store sanitised variable
            san_page = int(Util(page).is_string_only_num())
        else:
            return "Invalid page", 404
        
        user = GetUserModel(user_id).perform()
        invoker_user = ViewUserProfile(user_id).perform(user)
        threads_list = ListForumThreads(san_id).perform(user, san_page)
        category = GetForumCategoryMetaInformation(san_id).perform()

        # If threads_list is empty return invalid
        if threads_list != []:
            curr_page, total_page = threads_list[0]['page'], threads_list[0]['total_page']
        
        mod_flag = True if ROLES[invoker_user['role_name']] == ROLES[ROLE_MODERATOR] else False
        
        if category is None:
            return "Invalid page", 404
    
    except Exception as e:
        logger.error(e)
        return "Invalid page", 404

    if not app.config['TESTING']:
        # try:
        #encrypt
        user_encryption_key = QueryUserInstance(user_id).perform()["encryption_key"]
        for element in threads_list:
            for key, value in element.items():
                if key == "name":
                    element[key] = str(AES(user_encryption_key).encrypt(str(value)))
        
        category["name"] = str(AES(user_encryption_key).encrypt(str(category["name"])))
        
        # except Exception as e:
        #     return "Invalid page", 404

    return render_template("category.html", threads=threads_list, category=category, 
        page=curr_page, total_page=total_page, user=invoker_user, mod_flag=mod_flag)


@forum_blueprint.route("/category/create", methods=["POST"])
@login_required
def create_category():

    form_data = dict(request.form)
    error_msg = "Unexpected error"
    user_id = session.get('id')

    session_bool, text = logged_in_check()

    if text == "LOGOUT":
        return redirect(url_for("api.user.logout"))

    try:
        name = form_data['name']
        user = GetUserModel(session['id']).perform()

        if not app.config['TESTING']:
            #decrypt
            user_encryption_key = QueryUserInstance(user_id).perform()["encryption_key"]
            name = str(AES(user_encryption_key).decrypt(str(name)))

        # Check if name is a string and only contains numbers else return invalid
        if not Util(name).check_content():
            error_msg = "Invalid input"
            raise ValueError(error_msg)
        
        else:
            # Store sanitised variable
            sans_name = Util(name).check_content()
            CreateForumCategory(sans_name).perform(user)
   
    except Exception as e:
        logger.error(e)
        flash(error_msg)

    return redirect(request.headers['Referer'])


@forum_blueprint.route("/category/delete", methods=["POST"])
@login_required
def delete_category():

    form_data = dict(request.form)
    error_msg = "Unexpected error"

    session_bool, text = logged_in_check()

    if text == "LOGOUT":
        return redirect(url_for("api.user.logout"))

    try:
        category_id = form_data['id']
        user = GetUserModel(session['id']).perform()

        # Check if category_id is a string and only contains numbers else return invalid
        if not Util(str(category_id)).is_string_only_num():
            
            error_msg = "Unexpected error"
            raise ValueError(error_msg)
        
        else:
            # Store sanitised variable
            san_category_id = Util(str(category_id)).is_string_only_num()
            DeleteForumCategory(san_category_id).perform(user)

    except Exception as e:
        logger.error(e)
        flash(error_msg)
    
    return redirect(request.headers['Referer'])


@forum_blueprint.route("/category/rename", methods=["POST"])
@login_required
def rename_category():

    form_data = dict(request.form)
    error_msg = "Unexpected error"
    user_id = session.get('id')

    session_bool, text = logged_in_check()

    if text == "LOGOUT":
        return redirect(url_for("api.user.logout"))

    try:
        name = form_data['name']
        category_id = form_data['id']
        user = GetUserModel(session['id']).perform()

        if not app.config['TESTING']:
            #decrypt    
            user_encryption_key = QueryUserInstance(user_id).perform()["encryption_key"]
            name = str(AES(user_encryption_key).decrypt(str(name)))

        # Check if name violate any of the illegal characters else store it
        if not Util(name).check_content():
            error_msg = "Invalid input"
            raise ValueError(error_msg)
        else:
            # Store sanitised variable
            san_name = Util(name).check_content()
            # Check if category_id is a string and only contains numbers and store it
            san_category_id = Util(str(category_id)).is_string_only_num()

            RenameForumCategory(san_name, san_category_id).perform(user)
    
    except Exception as e:
        logger.error(e)
        flash(error_msg)
    
    return redirect(request.headers['Referer'])


@forum_blueprint.route("/thread/<id>", methods=["GET"])
@forum_blueprint.route("/thread/<id>/<page>", methods=["GET"])
@login_required
def thread_page(id, page="1"):
    curr_page, total_page = 1, 1
    error_msg = "Unexpected error"
    user_id = session.get('id')

    session_bool, text = logged_in_check()

    if text == "LOGOUT":
        return redirect(url_for("api.user.logout"))

    try:
        # Check if id is a string and only contains numbers else return invalid
        if Util(id).is_string_only_num(): 
            # Store sanitised variable
            san_id = int(Util(id).is_string_only_num())
        else:
            return "Invalid page", 404

        # Check if page is a string and only contains numbers else return invalid
        if Util(page).is_string_only_num():
            # Store sanitised variable 
            san_page = int(Util(page).is_string_only_num())
        
        else:
            return "Invalid page", 404

        user = GetUserModel(user_id).perform()
        invoker_user = ViewUserProfile(user_id).perform(user)
        posts_list  = ListForumPosts(san_id).perform(user, san_page)
        thread = GetForumThreadMetaInformation(san_id).perform()

        # # Return invalid is thread is none
        # if thread == None:
        #     return "Invalid page", 404
            
        if posts_list != []:
            curr_page, total_page = posts_list[0]['page'], posts_list[0]['total_page']
        
        mod_flag = True if ROLES[invoker_user['role_name']] == ROLES[ROLE_MODERATOR] else False
    
    except Exception as e :
        logger.error(e)
        flash(error_msg)
        return "Invalid page", 404

    #encrypt
    try:
        if not app.config['TESTING']:
            user_encryption_key = QueryUserInstance(user_id).perform()["encryption_key"]
            for element in posts_list:
                for key, value in element.items():
                    if key == "comment":
                        element[key] = str(AES(user_encryption_key).encrypt(str(value)))
            thread["name"] = str(AES(user_encryption_key).encrypt(str(thread["name"])))
    
    except Exception as e:
        return "Invalid page", 404
    
    return render_template("thread.html", posts=posts_list, thread=thread,
        page=curr_page, total_page=total_page, user=invoker_user, mod_flag=mod_flag)


@forum_blueprint.route("/thread/create", methods=["POST"])
@login_required
def create_thread():

    form_data = dict(request.form)
    error_msg = "Unexpected error"
    user_id = session.get('id')

    session_bool, text = logged_in_check()

    if text == "LOGOUT":
        return redirect(url_for("api.user.logout"))

    try: 
        name = form_data['name']
        category_id = form_data['category_id']
        user = GetUserModel(session['id']).perform()

        if not app.config['TESTING']:
            #decrypt
            user_encryption_key = QueryUserInstance(user_id).perform()["encryption_key"]
            name = str(AES(user_encryption_key).decrypt(str(name)))

        # Check if name violate any of the illegal characters else store it
        if not Util(name).check_content():
            error_msg = "Invalid input"
            raise ValueError(error_msg)
        else:
            # Store sanitised variable 
            san_name = Util(name).check_content()
            # Check if category_id is a string and only contains numbers and store it
            san_category_id = Util(str(category_id)).is_string_only_num()

            success, error = CreateForumThread(san_name, san_category_id).perform(user)
            if not success:
                flash(error[0])

    except Exception as e:
        logger.error(e)
        flash(error_msg)

    return redirect(request.headers['Referer'])


@forum_blueprint.route("/thread/delete", methods=["POST"])
@login_required
def delete_thread():

    form_data = dict(request.form)
    error_msg = "Unexpected error"

    session_bool, text = logged_in_check()

    if text == "LOGOUT":
        return redirect(url_for("api.user.logout"))

    try:
        thread_id = form_data['thread_id']
        user = GetUserModel(session['id']).perform()
        
        # Check if thread_id is a string and only contains numbers and store it
        if not Util(str(thread_id)).is_string_only_num():
            error_msg = "Unexpected error"
            raise ValueError(error_msg)
        else:
            # Store sanitised variable 
            san_thread_id = Util(str(thread_id)).is_string_only_num()
            
            DeleteForumCategory(san_thread_id).perform(user)

    except Exception as e:
        logger.error(e)
        flash(error_msg)
    
    return redirect(request.headers['Referer'])

@forum_blueprint.route("/thread/rename", methods=["POST"])
@login_required
def rename_thread():

    form_data = dict(request.form)
    error_msg = "Unexpected error"
    user_id = session.get('id')

    session_bool, text = logged_in_check()

    if text == "LOGOUT":
        return redirect(url_for("api.user.logout"))

    try:
        name = form_data['name']
        thread_id = form_data['thread_id']
        user = GetUserModel(session['id']).perform()

        if not app.config['TESTING']:
            #decrypt
            user_encryption_key = QueryUserInstance( user_id).perform()["encryption_key"]
            name = str(AES(user_encryption_key).decrypt(str(name)))
        
        
        if not Util(name).check_content():
            error_msg = "Invalid input"
            raise ValueError(error_msg)
        
        else: # Check if post belongs to user or not 
            # Store sanitised variable 
            san_name = Util(name).check_content()
            # Check if thread_id is a string and only contains numbers and store it
            san_thread_id = Util(str(thread_id)).is_string_only_num()
            
            if form_data['user_id'] == user.id:    
                RenameOwnForumThread(san_name, san_thread_id).perform(user)
            else: 
                RenameOthersForumThread(san_name, san_thread_id).perform(user)
        
    except Exception as e:
        logger.error(e)
        flash(error_msg)

    return redirect(request.headers['Referer'])


@forum_blueprint.route("/post/create", methods=["POST"])
@login_required
def create_post():

    form_data = dict(request.form)
    error_msg = "Unexpected error"
    user_id = session.get('id')

    session_bool, text = logged_in_check()

    if text == "LOGOUT":
        return redirect(url_for("api.user.logout"))

    try:
        comment = form_data['comment']
        thread_id = form_data['thread_id']
        user = GetUserModel(session['id']).perform()

        if not app.config['TESTING']:
            #decrypt
            user_encryption_key = QueryUserInstance(user_id).perform()["encryption_key"]
            comment = str(AES(user_encryption_key).decrypt(str(comment)))
        
        # Check if name violate any of the illegal characters else store it
        if not Util(comment).check_content():
            error_msg = "Invalid input"
            raise ValueError(error_msg)
        else:
            # Store sanitised variable 
            san_comment = Util(comment).check_content()
            # Check if thread_id is a string and only contains numbers and store it
            san_thread_id = Util(str(thread_id)).is_string_only_num()
            
            CreateForumPosts(san_comment, san_thread_id).perform(user)
    except Exception as e:
        logger.error(e)
        flash(error_msg)
    
    return redirect(request.headers['Referer'])


@forum_blueprint.route("/post/update", methods=["POST"])
@login_required
def update_post():

    form_data = dict(request.form)
    error_msg = "Unexpected error"
    user_id = session.get('id')

    session_bool, text = logged_in_check()

    if text == "LOGOUT":
        return redirect(url_for("api.user.logout"))

    try:
        comment = form_data['comment']
        post_id = form_data['post_id']
        user = GetUserModel(session['id']).perform()

        if not app.config['TESTING']:
            #decrypt
            user_encryption_key = QueryUserInstance(user_id).perform()["encryption_key"]
            comment = str(AES(user_encryption_key).decrypt(str(comment)))
        
        # Check if name violate any of the illegal characters else store it 
        if not Util(comment).check_content():
            error_msg = "Invalid input"
            raise ValueError(error_msg)
        else: # Check if post belongs to user or not
            # Store sanitised variable 
            san_comment = Util(comment).check_content()
            # Check if post_id is a string and only contains numbers and store it
            san_post_id = Util(str(post_id)).is_string_only_num()
            
            if form_data['user_id'] == user.id:
                UpdateOwnForumPost(san_comment, san_post_id).perform(user)
            else: 
                UpdateOthersForumPost(san_comment, san_post_id).perform(user)
        
    except Exception as e:
        logger.error(e)
        flash(error_msg)
    
    return redirect(request.headers['Referer'])


@forum_blueprint.route("/post/like", methods=["POST"])
@login_required
def like_post():

    form_data = dict(request.form)
    error_msg = "Unexpected error"

    session_bool, text = logged_in_check()

    if text == "LOGOUT":
        return redirect(url_for("api.user.logout"))

    try:
        id = session['id']
        # Check if id is a string and only contains numbers
        UserLikePost(id , Util(str(form_data['id'])).is_string_only_num()).perform()
    except:
        flash(error_msg)
    
    return redirect(request.headers['Referer'])
