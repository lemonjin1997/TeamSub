from __future__ import annotations

import base64
import hashlib
import os
from operator import and_
from typing import Any

import bleach
from sqlalchemy.orm import aliased
from werkzeug.datastructures import FileStorage

from app.constants import *
from app.core.action_requirement import action_requirement_factory
from app.core.model import *
from app.srptools import SRPContext, SRPServerSession
from app.srptools.constants import HASH_SHA_256

user_login_cache = {}


# TODO extract magic numbers in constants
# TODO make better use of new lines to create visual separation of code for readability
# TODO missing type hints somewhere
# TODO depedency injection for nested actions somehow

def hashing_function(content: str) -> bytes:
    content += content + str(datetime.now())
    t_sha = hashlib.sha512()
    t_sha.update(content.encode('utf-8'))
    hashed_password = base64.urlsafe_b64encode(t_sha.digest())
    return hashed_password


# TODO what if file_path exists and file error was thrown
def save_file(content: str, thread_id: int) -> bytes:
    file_name = hashing_function(content).decode("utf-8")
    file_path = "./filePath" + "/" + str(thread_id)
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    file_path += "/" + file_name
    open(file_path, "x")
    file = open(file_path, "w")
    file.write(content)
    file.close()
    return file_name


def read_file(file_name: str, thread_id: int) -> str:
    file_path = "./filePath" + "/" + str(thread_id) + "/" + file_name
    file = open(file_path, "r")
    content = file.read()
    file.close()
    return content


def save_img(img: FileStorage) -> str:
    file_name = hashing_function(img.filename)
    file_path = "./static/img"
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    file_path += "/" + file_name.decode("utf-8") + ".png"
    open(file_path, "x")
    img.save(file_path)
    return file_name.decode("utf-8") + ".png"


class ForumAction:

    def __init__(self,
                 session=db.session,
                 action_model=ForumActionModel,
                 user_model=UserModel,
                 role_has_forum_action_model=RoleHasForumActionModel,
                 requirement_factory=action_requirement_factory):
        self.session = session
        self.action_model = action_model
        self.requirement_factory = requirement_factory
        self.role_has_forum_action_model = role_has_forum_action_model
        self.user_model = user_model

    def get_name(self) -> str:
        return self.__class__.__name__

    def is_user_allowed(self, user: UserInstanceModel) -> tuple[bool, list[str]]:
        user_model = self.session.get(self.user_model, user.user_id)
        action_model = self.action_model.query.filter(self.action_model.name == self.get_name()).scalar()

        role_has_access = self.role_has_forum_action_model.query.filter(
            self.role_has_forum_action_model.role_id == user_model.role_id,
            self.role_has_forum_action_model.forum_action_id == action_model.id
        ).scalar() is not None

        if not role_has_access:
            return False, ["User not allowed to perform action"]

        requirements = self.requirement_factory.create_for(action_model.id)
        messages = []
        for requirement in requirements:
            success, message = requirement.check(user_model, session=self.session)
            if not success:
                messages.append(message)
        return not messages, messages

    def perform(self, *args, **kwargs) -> Any:
        pass


class LoginInstance(ForumAction):

    def __init__(self, id, ip_location, browser_header, encryption_key, user_instance_model=UserInstanceModel,
                 user_model=UserModel, **kwargs):
        super().__init__(**kwargs)

        self.id = id
        self.ip_location = ip_location
        self.browser_header = browser_header
        self.encryption_key = encryption_key
        self.user_instance_model = user_instance_model
        self.user_model = user_model

    def perform(self) -> Any:
        user_instance = self.user_instance_model.query.filter(
            self.user_instance_model.user_id == self.id
        ).scalar()
        user = self.user_model.query.filter(
            self.user_model.id == self.id, self.user_model.last_banned_by == None
        ).scalar()
        if not user.is_banned:
            timeNow = datetime.now()
            if user_instance is None:
                user_instance = self.user_instance_model(self.id, self.ip_location, self.browser_header)
                user_instance.user_id = self.id
                user_instance.ip_location = self.ip_location
                user_instance.browser_header = self.browser_header
                user_instance.encryption_key = self.encryption_key
                user_instance.login_timestamp = timeNow
                self.session.add(user_instance)
                self.session.commit()
            else:
                user_instance.user_id = self.id
                user_instance.ip_location = self.ip_location
                user_instance.browser_header = self.browser_header
                user_instance.encryption_key = self.encryption_key
                user_instance.login_timestamp = timeNow
                self.session.commit()
            user.last_login_timestamp = timeNow
            self.session.commit()
        else:
            print("user is banned")


class QueryUserInstance(ForumAction):
    def __init__(self, id, user_instance_model=UserInstanceModel, **kwargs):
        super().__init__(**kwargs)
        self.id = id
        self.user_instance_model = user_instance_model

    def perform(self) -> Any:
        user_instance = self.user_instance_model.query.filter(
            self.user_instance_model.user_id == self.id
        ).scalar()
        tmp_dic = {
            "time": user_instance.login_timestamp,
            "ip_location": user_instance.ip_location,
            "browser_header": user_instance.browser_header,
            "encryption_key": user_instance.encryption_key
        }
        return tmp_dic


class LoginFailCount(ForumAction):
    def __init__(self, user_id, user_model=UserModel, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.user_model = user_model

    def perform(self) -> Any:
        user = self.user_model.query.filter(self.user_model.id == self.user_id).scalar()
        user.failed_login_count += 1
        self.session.commit()


class RegisterUser(ForumAction):
    def __init__(self, name, email, password_salt, password_hash, role_id, profile_image_uri,
                 user_model=UserModel,
                 **kwargs):
        super().__init__(**kwargs)

        self.name = name
        self.email = email
        self.password_salt = password_salt
        self.password_hash = password_hash
        self.role_id = role_id
        self.profile_image_uri = profile_image_uri
        self.user_model = user_model
        # TODO audit user model

    def perform(self):
        emailCheck = self.user_model.query.filter(self.user_model.email == self.email).scalar()
        if emailCheck is None:
            tmp_user_model = self.user_model(self.name, self.email, self.password_hash, self.password_salt,
                                             self.role_id)
            tmp_user_model.password_hash = self.password_hash
            tmp_user_model.email = self.email
            tmp_user_model.name = self.name
            tmp_user_model.password_salt = self.password_salt
            tmp_user_model.role_id = self.role_id
            tmp_user_model.profile_image_uri = self.profile_image_uri
            tmp_user_model.verified_user = False
            self.session.add(tmp_user_model)
            self.session.commit()
            return True, []
        else:
            return None, ["Unique key conflict error"]


class VerifyUser(ForumAction):
    def __init__(self, user_model=UserModel, **kwargs):
        super().__init__(**kwargs)
        self.user_model = user_model
        # TODO audit user model

    def perform(self, data):

        # Checking if email is 
        if 'email' in data and len(data) == 1:
            email = data["email"]

            # CHECK IF EMAIL EXISTS
            if email is not None:
                user = self.user_model.query.filter(UserModel.email == email).scalar()

                if user:
                    gen = '2'
                    prime = 'AC6BDB41324A9A9BF166DE5E1389582FAF72B6651987EE07FC3192943DB56050A37329CBB4A099ED8193E0757767A13DD52312AB4B03310DCD7F48A9DA04FD50E8083969EDB767B0CF6095179A163AB3661A05FBD5FAAAE82918A9962F0B93B855F97993EC975EEAA80D740ADBF4FF747359D041D5C33EA71D281E446B14773BCA97B43A23FB801676BD207A436C6481F1D2B9078717461A5B9D32E688F87748544523B524B0D57D5EA77A2775D2ECFA032CFBDBF52FB3786160279004E57AE6AF874E7303CE53299CCC041C7BC308D82A5698F3A8D0C38271AE35F8E9DBFBB694B5C803D89F7AE435DE236D525F54759B65E372FCD68EF20FA7111F9E4AFF73'

                    # Create srp object
                    srp_test = SRPContext(email, prime=prime, generator=gen,
                                          bits_random=2048, hash_func=HASH_SHA_256, bits_salt=256)

                    server_session = SRPServerSession(
                        srp_test, user.password_hash)

                    # Creation sever public
                    server_public = server_session.public
                    # Current user paired with server session
                    user_login_cache[str(email)] = {}
                    user_login_cache[str(email)]["server_session"] = server_session

                    # Salt and server pub return to client to compute
                    response = {
                        "salt": user.password_salt,
                        "serverpub": server_public
                    }
                    return response
        return {}


class UpdateOTP(ForumAction):
    def __init__(self, email, otp, user_model=UserModel, **kwargs):
        super().__init__(**kwargs)
        self.email = email
        self.otp = otp
        self.user_model = user_model

    def perform(self) -> Any:
        user = self.user_model.query.filter(self.user_model.email == self.email).scalar()
        user.otp = self.otp
        self.session.commit()


class CheckOTP(ForumAction):
    def __init__(self, id, user_model=UserModel, **kwargs):
        super().__init__(**kwargs)
        self.id = id
        self.user_model = user_model

    def perform(self) -> Any:
        user = self.user_model.query.filter(
            self.user_model.id == self.id).scalar()
        return user.otp


class ConfirmLogin(ForumAction):
    def __init__(self, email, clientpub, m1, user_model=UserModel, **kwargs):
        super().__init__(**kwargs)
        self.email = email
        self.clientpub = clientpub
        self.m1 = m1
        self.user_model = user_model

    def perform(self):
        # Gather important info
        user = self.user_model.query.filter(self.user_model.email == self.email,
                                            self.user_model.verified_user == 1).scalar()
        server_session = user_login_cache[self.email]["server_session"]
        salt = user.password_salt

        # Server process client pub and salt
        server_session.process(self.clientpub, salt)

        # Check if proof matches
        result = server_session.verify_proof(self.m1)

        del user_login_cache[self.email]["server_session"]

        return result, user.id, server_session.key


class UpdateUserModelEmailVerified(ForumAction):
    def __init__(self, email, user_model=UserModel, **kwargs):
        super().__init__(**kwargs)
        self.email = email
        self.user_model = user_model

    def perform(self) -> Any:
        user = self.user_model.query.filter(self.user_model.email == self.email).scalar()
        if user.verified_user == False or user.verified_user is None:
            user.verified_user = True
        self.session.commit()


class Login(ForumAction):

    def __init__(self, email, password, user_model=UserModel, **kwargs):
        super().__init__(**kwargs)
        self.email = email
        self.password = password
        self.user_model = user_model
        # TODO audit user model

    def perform(self):
        tmp_user = self.user_model.query.filter(
            self.user_model.email == self.email,
            self.user_model.password_hash == self.password
        ).first()

        return tmp_user if not tmp_user.is_banned else None


class ViewUserProfile(ForumAction):
    def __init__(self, target_user_id: int, user_model=UserModel, role_model=RoleModel, **kwargs):
        super().__init__(**kwargs)
        self.target_user_id = target_user_id
        self.user_model = user_model
        self.role_model = role_model

    def perform(self, user: UserModel) -> dict:
        if not user.is_banned:

            target_user = self.user_model.query.filter(self.user_model.id == self.target_user_id).scalar()
            target_role = self.role_model.query.filter(self.role_model.id == target_user.role_id).scalar()

            user = self.user_model.query.filter(self.user_model.id == user.id).scalar()
            role = self.role_model.query.filter(self.role_model.id == user.role_id).scalar()
            if user.id == target_user.id or ROLES[target_role.name] != ROLES[ROLE_ADMIN]:
                return {
                    "id": target_user.id,
                    "profile_image_uri": "img/" + target_user.profile_image_uri if target_user.profile_image_uri is not None else "img/default_profile.png",
                    "name": bleach.clean(target_user.name),
                    "is_banned": target_user.is_banned,
                    "role_name": target_role.name
                }
            else:
                return None


class GetUserModel(ForumAction):
    def __init__(self, user_id: int, user_model=UserModel, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.user_model = user_model

    def perform(self) -> dict:
        user = self.user_model.query.filter(self.user_model.id == self.user_id).scalar()
        # user.profile_image_uri =  "img/" + user.profile_image_uri
        return user


class GetAllUsers(ForumAction):
    def __init__(self, user_model=UserModel, role_model=RoleModel, **kwargs):
        super().__init__(**kwargs)
        self.user_model = user_model
        self.role_model = role_model

    def perform(self, user: UserModel) -> dict:
        if not user.is_banned:
            users = self.user_model.query.join(self.role_model, self.user_model.role_id == self.role_model.id).filter(
                self.role_model.name != "Admin").all()
            tmp_list = []
            for user in users:
                tmp_dic = {
                    'id': user.id,
                    'name': user.name
                }
                tmp_list.append(tmp_dic)
            return tmp_list


class AdminEditRole(ForumAction):
    def __init__(self, role_name: str, user_id: int,
                 user_model=UserModel,
                 audit_user_model=AuditUserModel,
                 role_model=RoleModel,
                 **kwargs):
        super().__init__(**kwargs)
        self.role_name = role_name
        self.user_id = user_id
        self.user_model = user_model
        self.audit_user_model = audit_user_model
        self.role_model = role_model

    def perform(self, user: UserModel) -> None:
        if not user.is_banned:
            time_now = datetime.now()
            role_model = self.role_model.query.filter(self.role_model.name == self.role_name).scalar()

            user_model = self.session.get(self.user_model, self.user_id)
            user_model.role_id = role_model.id

            # action_id = AUDIT_ACTION_IDS[AUDIT_ACTION_ADMIN_EDIT_ROLE]
            # audit_model = self.audit_user_model(user_model, time_now, user.id, action_id)
            # self.session.add(audit_model)
            self.session.commit()


class CheckUserModelEmail(ForumAction):
    def __init__(self, user_email: str, user_model=UserModel, **kwargs):
        super().__init__(**kwargs)
        self.user_email = user_email
        self.user_model = user_model

    def perform(self) -> dict:
        user = self.user_model.query.filter(self.user_model.email == self.user_email).scalar()
        return True if user is not None else False


class ResetPassword(ForumAction):
    def __init__(self, password_salt: str, password_hash: str, user_email: str, user_model=UserModel, **kwargs):
        super().__init__(**kwargs)
        self.password_salt = password_salt
        self.password_hash = password_hash
        self.user_email = user_email
        self.user_model = user_model
        # TODO audit user model

    def perform(self):
        self.user_model.query.filter(self.user_model.email == self.user_email) \
            .update({self.user_model.password_hash: self.password_hash,
                     self.user_model.password_salt: self.password_salt})
        self.session.commit()


class EditOthersProfileName(ForumAction):
    def __init__(self, name, user_id: int,
                 user_model=UserModel,
                 audit_user_model=AuditUserModel,
                 **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.user_id = user_id
        self.user_model = user_model
        self.audit_user_model = audit_user_model

    def perform(self, user: UserModel) -> None:
        if not user.is_banned and user.verified_user:
            time_now = datetime.now()
            user_model = self.session.get(self.user_model, self.user_id)
            user_model.name = self.name
            action_id = AUDIT_ACTION_IDS[AUDIT_ACTION_USER_UPDATE_OTHERS_PROFILE_NAME]
            audit_model = self.audit_user_model(user_model, time_now, user.id, action_id)
            self.session.add(audit_model)
            self.session.commit()


class EditOwnProfileName(ForumAction):
    def __init__(self, name,
                 user_model=UserModel,
                 audit_user_model=AuditUserModel,
                 **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.user_model = user_model
        self.audit_user_model = audit_user_model

    def perform(self, user: UserModel) -> None:
        if not user.is_banned and user.verified_user:
            time_now = datetime.now()

            user.name = self.name

            action_id = AUDIT_ACTION_IDS[AUDIT_ACTION_USER_UPDATE_OWN_PROFILE_NAME]
            audit_model = self.audit_user_model(user, time_now, user.id, action_id)
            self.session.add(audit_model)
            self.session.commit()


class EditOthersProfileImage(ForumAction):
    def __init__(self, img, user_id: int, save_img_fn=save_img,
                 user_model=UserModel,
                 audit_user_model=AuditUserModel,
                 **kwargs):
        super().__init__(**kwargs)
        self.img = img
        self.user_id = user_id
        self.save_img_fn = save_img_fn
        self.user_model = user_model
        self.audit_user_model = audit_user_model

    def perform(self, user: UserModel) -> None:
        if not user.is_banned and user.verified_user:
            image_uri = self.save_img_fn(self.img)
            time_now = datetime.now()

            user_model = self.session.get(self.user_model, self.user_id)
            user_model.profile_image_uri = image_uri
            action_id = AUDIT_ACTION_IDS[AUDIT_ACTION_USER_UPDATE_OTHERS_PROFILE_IMAGE]
            audit_model = self.audit_user_model(user_model, time_now, user.id, action_id)
            self.session.add(audit_model)
            self.session.commit()


class EditOwnProfileImage(ForumAction):
    def __init__(self, img, save_img_fn=save_img,
                 user_model=UserModel,
                 audit_user_model=AuditUserModel,
                 **kwargs):
        super().__init__(**kwargs)
        self.img = img
        self.save_img_fn = save_img_fn
        self.user_model = user_model
        self.audit_user_model = audit_user_model

    def perform(self, user: UserModel) -> None:
        if not user.is_banned and user.verified_user:
            image_uri = self.save_img_fn(self.img)
            time_now = datetime.now()

            user.profile_image_uri = image_uri
            action_id = AUDIT_ACTION_IDS[AUDIT_ACTION_USER_UPDATE_OWN_PROFILE_IMAGE]
            audit_model = self.audit_user_model(user, time_now, user.id, action_id)
            self.session.add(audit_model)
            self.session.commit()


class ListForumCategories(ForumAction):

    def __init__(self, category_model=ForumCategoryModel, **kwargs):
        super().__init__(**kwargs)
        self.category_model = category_model

    def perform(self, user: UserModel, page: int):
        # I don't know but all the other create action sets modified_by to the user, is that intended
        if not user.is_banned and user.verified_user:
            tmp_paginate = self.category_model.query.filter(
                self.category_model.delete_timestamp == None
            ).paginate(page=page, per_page=5)

            tmp_list = []
            for forum_categories in tmp_paginate.items:
                tmp_dic = {
                    'id': forum_categories.id,
                    'name': bleach.clean(forum_categories.name),
                    'created_timestamp': forum_categories.create_timestamp,
                    'modified_timestamp': forum_categories.modified_timestamp,
                    'page': tmp_paginate.page,
                    'total_page': tmp_paginate.pages}
                tmp_list.append(tmp_dic)
            return tmp_list
        else:
            return []


class CreateForumCategory(ForumAction):

    def __init__(self, name: str,
                 category_model=ForumCategoryModel,
                 audit_category_model=AuditForumCategoryModel,
                 **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.category_model = category_model
        self.audit_category_model = audit_category_model

    def perform(self, user: UserModel):
        if not user.is_banned and user.verified_user:
            time_now = datetime.now()

            name_exists = self.session.query(self.category_model.id) \
                              .filter(self.category_model.name == self.name) \
                              .filter(self.category_model.delete_timestamp == None) \
                              .filter(self.category_model.deleted_by == None) \
                              .first() is not None

            if name_exists:
                return False, ["Duplicated category name."]

            category_model = self.category_model(self.name, time_now, user.id)
            category_model.name = self.name
            category_model.created_by = user.id
            category_model.create_timestamp = time_now
            category_model.modified_timestamp = time_now
            category_model.modified_by = user.id
            self.session.add(category_model)
            self.session.commit()

            action_id = AUDIT_ACTION_IDS[AUDIT_ACTION_CREATE_CATEGORY]
            audit_model = self.audit_category_model(category_model, time_now, user.id, action_id)
            self.session.add(audit_model)
            self.session.commit()

            return True, []


class RenameForumCategory(ForumAction):

    def __init__(self, name: str, category_id: int,
                 category_model=ForumCategoryModel,
                 audit_category_model=AuditForumCategoryModel,
                 **kwargs):
        super().__init__(**kwargs)
        self.category_id = category_id
        self.name = name
        self.category_model = category_model
        self.audit_category_model = audit_category_model

    def perform(self, user: UserModel):
        if not user.is_banned and user.verified_user:
            time_now = datetime.now()

            category_model = self.session.get(self.category_model, self.category_id)
            if category_model.name == self.name:
                return False, ["Renaming to same name"]

            category_model.name = self.name
            category_model.modified_timestamp = time_now
            category_model.modified_by = user.id
            action_id = AUDIT_ACTION_IDS[AUDIT_ACTION_RENAME_CATEGORY]
            audit_model = self.audit_category_model(category_model, time_now, user.id, action_id)
            self.session.add(audit_model)
            self.session.commit()

            return True, []


class DeleteForumCategory(ForumAction):

    def __init__(self, category_id: int,
                 category_model=ForumCategoryModel,
                 audit_category_model=AuditForumCategoryModel,
                 thread_model=ForumThreadModel,
                 **kwargs):
        super().__init__(**kwargs)
        self.category_id = category_id
        self.category_model = category_model
        self.audit_category_model = audit_category_model
        self.thread_model = thread_model

    def perform(self, user: UserModel):
        if not user.is_banned and user.verified_user:
            time_now = datetime.now()

            category_model = self.session.get(self.category_model, self.category_id)
            category_model.deleted_by = user.id
            category_model.delete_timestamp = time_now

            action_id = AUDIT_ACTION_IDS[AUDIT_ACTION_DELETE_CATEGORY]
            audit_model = self.audit_category_model(category_model, time_now, user.id, action_id)
            self.session.add(audit_model)
            self.session.commit()

            # TODO Same comment as delete thread action
            thread_models = self.thread_model.query.filter(
                self.thread_model.parent_category_id == self.category_id).all()
            for thread_model in thread_models:
                DeleteForumThread(thread_model.id).perform(user)


class GetForumCategoryMetaInformation(ForumAction):
    def __init__(self, category_id: int,
                 category_model=ForumCategoryModel,
                 **kwargs):
        super().__init__(**kwargs)
        self.category_id = category_id
        self.category_model = category_model

    def perform(self) -> dict:
        category_model = self.session.get(self.category_model, self.category_id)
        if category_model is None:
            return None
        return {
            "category_id": category_model.id,
            "name": category_model.name
        }


class ListForumThreads(ForumAction):

    def __init__(self, category_id: int,
                 user_model=UserModel,
                 thread_model=ForumThreadModel,
                 **kwargs):
        super().__init__(**kwargs)
        self.category_id = category_id
        self.thread_model = thread_model
        self.user_model = user_model

    def perform(self, user: UserModel, page: int):
        if not user.is_banned and user.verified_user:
            tmp_paginate = self.thread_model.query.join(
                self.user_model,
                self.user_model.id == self.thread_model.created_by
            ).filter(
                self.thread_model.parent_category_id == self.category_id,
                self.thread_model.delete_timestamp == None,
                self.thread_model.deleted_by == None
            ).add_columns(self.user_model) \
                .paginate(page=page, per_page=5)
            tmp_list = []
            for forum_thread, user in tmp_paginate.items:
                tmp_dic = {
                    'id': forum_thread.id,
                    'name': bleach.clean(forum_thread.name),
                    'created_timestamp': forum_thread.create_timestamp,
                    'modified_timestamp': forum_thread.modified_timestamp,
                    'created_by_name': bleach.clean(user.name),
                    'user_id': user.id,
                    'page': tmp_paginate.page,
                    'total_page': tmp_paginate.pages
                }
                tmp_list.append(tmp_dic)
            return tmp_list
        else:
            return []


class CreateForumThread(ForumAction):

    def __init__(self, name: str, parent_category_id: int,
                 thread_model=ForumThreadModel,
                 audit_thread_model=AuditForumThreadModel,
                 like_model=UserLikesForumPostModel,
                 post_model=ForumPostModel,
                 role_model=RoleModel,
                 **kwargs):
        super().__init__(**kwargs)
        self.parent_category_id = parent_category_id
        self.name = name
        self.thread_model = thread_model
        self.audit_thread_model = audit_thread_model
        self.like_model = like_model
        self.post_model = post_model
        self.role_model = role_model

    def perform(self, user: UserModel):

        check_user_count = self.session.query(self.like_model, self.post_model) \
            .filter(self.post_model.created_by == user.id, self.like_model.post_id == self.post_model.id).count()

        role_model = self.role_model.query.filter(self.role_model.name == ROLE_MODERATOR).scalar()

        if not user.is_banned and user.verified_user:

            if user.role_id != role_model.id:
                if check_user_count < 10:
                    return False, ['10 likes is required to create thread.']

            time_now = datetime.now()

            name_exists = self.session.query(self.thread_model.id) \
                              .filter(self.thread_model.name == self.name) \
                              .filter(self.thread_model.parent_category_id == self.parent_category_id) \
                              .filter(self.thread_model.delete_timestamp == None) \
                              .filter(self.thread_model.deleted_by == None) \
                              .first() is not None

            if name_exists:
                return False, ["Duplicated thread name."]

            thread_model = self.thread_model(self.name, self.parent_category_id, time_now, user.id)
            thread_model.name = self.name
            thread_model.created_by = user.id
            thread_model.parent_category_id = self.parent_category_id
            thread_model.create_timestamp = time_now
            thread_model.modified_timestamp = time_now
            thread_model.modified_by = user.id
            self.session.add(thread_model)
            self.session.commit()

            action_id = AUDIT_ACTION_IDS[AUDIT_ACTION_CREATE_THREAD]
            audit_model = self.audit_thread_model(thread_model, time_now, user.id, action_id)
            self.session.add(audit_model)
            self.session.commit()

            return True, []
        else:
            return False, ['User is not allowed']


class RenameOthersForumThread(ForumAction):

    def __init__(self, name: str, thread_id: int,
                 thread_model=ForumThreadModel,
                 audit_thread_model=AuditForumThreadModel,
                 **kwargs):
        super().__init__(**kwargs)
        self.thread_id = thread_id
        self.name = name
        self.thread_model = thread_model
        self.audit_thread_model = audit_thread_model

    def perform(self, user: UserModel):
        if not user.is_banned and user.verified_user:
            time_now = datetime.now()

            thread_model = self.session.get(self.thread_model, self.thread_id)
            if thread_model.name == self.name:
                return False, ["Renaming to same name"]
            thread_model.name = self.name
            thread_model.modified_by = user.id
            thread_model.modified_timestamp = time_now
            action_id = AUDIT_ACTION_IDS[AUDIT_ACTION_RENAME_OTHERS_THREAD]
            audit_model = self.audit_thread_model(thread_model, time_now, user.id, action_id)
            self.session.add(audit_model)
            self.session.commit()

            return True, []


class RenameOwnForumThread(ForumAction):

    def __init__(self, name: str, thread_id: int,
                 thread_model=ForumThreadModel,
                 audit_thread_model=AuditForumThreadModel,
                 **kwargs):
        super().__init__(**kwargs)
        self.thread_id = thread_id
        self.name = name
        self.thread_model = thread_model
        self.audit_thread_model = audit_thread_model

    def perform(self, user: UserModel) -> tuple[bool, list[str]]:
        if not user.is_banned and user.verified_user:
            time_now = datetime.now()

            thread_model = self.session.get(self.thread_model, self.thread_id)
            if thread_model.created_by != user.id:
                return False, ["Forum thread does not belong to user"]

            if thread_model.name == self.name:
                return False, ["Renaming to same name"]

            thread_model.name = self.name
            thread_model.modified_by = user.id
            thread_model.modified_timestamp = time_now
            action_id = AUDIT_ACTION_IDS[AUDIT_ACTION_RENAME_OWN_THREAD]
            audit_model = self.audit_thread_model(thread_model, time_now, user.id, action_id)
            self.session.add(audit_model)
            self.session.commit()

            return True, []


class DeleteForumThread(ForumAction):

    def __init__(self, thread_id: int,
                 post_model=ForumPostModel,
                 thread_model=ForumThreadModel,
                 audit_thread_model=AuditForumThreadModel,
                 **kwargs):
        super().__init__(**kwargs)
        self.thread_id = thread_id
        self.post_model = post_model
        self.thread_model = thread_model
        self.audit_thread_model = audit_thread_model

    def perform(self, user: UserModel):
        if not user.is_banned and user.verified_user:
            time_now = datetime.now()

            thread_model = self.session.get(self.thread_model, self.thread_id)
            thread_model.deleted_by = user.id
            thread_model.delete_timestamp = time_now
            action_id = AUDIT_ACTION_IDS[AUDIT_ACTION_DELETE_THREAD]
            audit_model = self.audit_thread_model(thread_model, time_now, user.id, action_id)
            self.session.add(audit_model)
            self.session.commit()

            # TODO create batch delete post action for efficient updates
            # TODO create batch delete post action for better permission checking
            # TODO check permission for that delete action
            # TODO think about how to dependency inject this action for testable code

            post_models = self.post_model.query.filter(self.post_model.parent_thread_id == self.thread_id).all()
            for post_model in post_models:
                DeleteForumPost(post_model.id).perform(user)


class GetForumThreadMetaInformation(ForumAction):
    def __init__(self, thread_id: int,
                 thread_model=ForumThreadModel,
                 **kwargs):
        super().__init__(**kwargs)
        self.thread_id = thread_id
        self.thread_model = thread_model

    def perform(self) -> dict:
        thread_model = self.session.get(self.thread_model, self.thread_id)
        if thread_model is None:
            return None
        return {
            "thread_id": thread_model.id,
            "name": thread_model.name
        }


class ListForumPosts(ForumAction):

    def __init__(self, thread_id: int,
                 user_model=UserModel,
                 post_model=ForumPostModel,
                 user_likes_forum_post_model=UserLikesForumPostModel,
                 **kwargs):
        super().__init__(**kwargs)
        self.thread_id = thread_id
        self.user_model = user_model
        self.post_model = post_model
        self.user_likes_forum_post_model = user_likes_forum_post_model

    def perform(self, user: UserModel, page: int):
        if not user.is_banned and user.verified_user:
            a1 = aliased(self.user_model)
            a2 = aliased(self.user_model)

            tmp_paginate = self.session.query(self.post_model, a1, a2) \
                .join(a1, a1.id == self.post_model.modified_by) \
                .join(a2, a2.id == self.post_model.created_by) \
                .filter(self.post_model.parent_thread_id == self.thread_id,
                        self.post_model.delete_timestamp == None,
                        self.post_model.deleted_by == None) \
                .with_entities(self.post_model, a1, a2) \
                .paginate(page=page, per_page=5)

            # tmp_paginate = self.post_model.query \
            #     .join(a2, a2.id == self.post_model.created_by) \
            #     .with_entities(self.post_model, a2) \
            #     .filter(self.post_model.parent_thread_id == self.thread_id,
            #             self.post_model.delete_timestamp == None,
            #             self.post_model.deleted_by == None) \
            #     .paginate(page=page, per_page=5)

            # Calculate how many likes for each post in view
            post_ids = [post.id for post, _, _ in tmp_paginate.items]
            likes_count_dic = {}
            for post_id in post_ids:
                likes_count = self.user_likes_forum_post_model.query.filter(
                    self.user_likes_forum_post_model.post_id == post_id,
                    self.user_likes_forum_post_model.like == True
                ).count()
                likes_count_dic[post_id] = likes_count

            tmp_list = []
            for forum_post, created_user, modified_user in tmp_paginate.items:
                tmp_dic = {
                    'id': forum_post.id,
                    'comment': bleach.clean(read_file(forum_post.content_uri, forum_post.parent_thread_id)),
                    'likes': likes_count_dic[forum_post.id],
                    'created_timestamp': forum_post.create_timestamp,
                    'modified_timestamp': forum_post.modified_timestamp,
                    'created_by_name': bleach.clean(created_user.name),
                    'modified_by_name': bleach.clean(modified_user.name),
                    'profile_image_uri': "/static/img/" + created_user.profile_image_uri if created_user.profile_image_uri is not None else "/static/img/default_profile.png",
                    'user_id': created_user.id,
                    'page': tmp_paginate.page,
                    'total_page': tmp_paginate.pages
                }
                tmp_list.append(tmp_dic)

            return tmp_list
        else:
            return []


class CreateForumPosts(ForumAction):

    def __init__(self, content: str, parent_thread_id: int,
                 post_model=ForumPostModel,
                 audit_post_model=AuditForumPostModel,
                 **kwargs):
        super().__init__(**kwargs)
        self.content = content
        self.parent_thread_id = parent_thread_id
        self.post_model = post_model
        self.audit_post_model = audit_post_model

    def perform(self, user: UserModel):
        if not user.is_banned and user.verified_user:
            content_uri = save_file(self.content, self.parent_thread_id)
            time_now = datetime.now()

            post_model = self.post_model(content_uri, self.parent_thread_id, time_now, user.id)
            post_model.content_uri = content_uri
            post_model.parent_thread_id = self.parent_thread_id
            post_model.created_by = user.id
            post_model.create_timestamp = time_now
            post_model.modified_by = user.id
            post_model.modified_timestamp = time_now
            self.session.add(post_model)
            self.session.commit()

            action_id = AUDIT_ACTION_IDS[AUDIT_ACTION_CREATE_POST]
            audit_model = self.audit_post_model(post_model, time_now, post_model.created_by, action_id)
            self.session.add(audit_model)
            self.session.commit()

            return True, []


class UpdateOthersForumPost(ForumAction):

    def __init__(self, content: str, post_id: int,
                 post_model=ForumPostModel,
                 audit_post_model=AuditForumPostModel,
                 **kwargs):
        super().__init__(**kwargs)
        self.post_id = post_id
        self.content = content
        self.post_model = post_model
        self.audit_post_model = audit_post_model

    def perform(self, user: UserModel) -> tuple[bool, list[str]]:
        time_now = datetime.now()
        if not user.is_banned and user.verified_user:
            post_model = self.session.get(self.post_model, self.post_id)
            if not post_model:
                return False, ["Post does not exists"]

            content_uri = save_file(self.content, post_model.parent_thread_id)
            post_model.content_uri = content_uri
            post_model.modified_by = user.id
            post_model.modified_timestamp = time_now

            action_id = AUDIT_ACTION_IDS[AUDIT_ACTION_UPDATE_OTHERS_POST]
            audit_model = self.audit_post_model(post_model, datetime.now(), user.id, action_id)
            self.session.add(audit_model)
            self.session.commit()

            return True, []


class UpdateOwnForumPost(ForumAction):

    def __init__(self, content: str, post_id: int,
                 post_model=ForumPostModel,
                 audit_post_model=AuditForumPostModel,
                 **kwargs):
        super().__init__(**kwargs)
        self.post_id = post_id
        self.content = content
        self.post_model = post_model
        self.audit_post_model = audit_post_model

    def perform(self, user: UserModel) -> tuple[bool, list[str]]:
        time_now = datetime.now()
        if not user.is_banned and user.verified_user:
            post_model = self.session.get(self.post_model, self.post_id)
            if not post_model:
                return False, ["Post does not exists"]

            if post_model.created_by != user.id:
                return False, ["Post does not belong to user"]

            content_uri = save_file(self.content, post_model.parent_thread_id)
            post_model.content_uri = content_uri
            post_model.modified_by = user.id
            post_model.modified_timestamp = time_now
            action_id = AUDIT_ACTION_IDS[AUDIT_ACTION_UPDATE_OWN_POST]
            audit_model = self.audit_post_model(post_model, datetime.now(), user.id, action_id)
            self.session.add(audit_model)
            self.session.commit()

            return True, []


class DeleteForumPost(ForumAction):
    def __init__(self, post_id: int,
                 post_model=ForumPostModel,
                 audit_post_model=AuditForumPostModel,
                 **kwargs):
        super().__init__(**kwargs)
        self.post_id = post_id
        self.post_model = post_model
        self.audit_post_model = audit_post_model

    def perform(self, user: UserModel) -> tuple[bool, list[str]]:
        if not user.is_banned and user.verified_user:
            post_model = self.session.get(self.post_model, self.post_id)
            if not post_model:
                return False, ["Post does not exists"]

            post_model.delete_timestamp = datetime.now()
            post_model.deleted_by = user.id
            action_id = AUDIT_ACTION_IDS[AUDIT_ACTION_DELETE_POST]
            audit_model = self.audit_post_model(post_model, post_model.delete_timestamp, post_model.deleted_by,
                                                action_id)
            self.session.add(audit_model)
            self.session.commit()
            return True, []


class UserLikePost(ForumAction):

    def __init__(self, user_id: int, post_id: int,
                 user_likes_forum_post_model=UserLikesForumPostModel,
                 audit_user_likes_forum_post_model=AuditUserLikesForumPostModel,
                 **kwargs):
        super().__init__(**kwargs)
        self.user_likes_forum_post_model = user_likes_forum_post_model
        self.audit_user_likes_forum_post_model = audit_user_likes_forum_post_model
        self.user_id = user_id
        self.post_id = post_id

    def perform(self):
        user = GetUserModel(self.user_id).perform()
        if not user.is_banned and user.verified_user:
            tmp_user_like = self.user_likes_forum_post_model.query.filter(
                and_(self.user_likes_forum_post_model.post_id == self.post_id,
                     self.user_likes_forum_post_model.user_id == self.user_id)
            ).scalar()
            if tmp_user_like:
                tmp_user_like.like = False if tmp_user_like.like else True
                self.session.commit()

            else:
                tmp = self.user_likes_forum_post_model(self.user_id, self.post_id, True)
                tmp.like = True
                tmp.user_id = self.user_id
                tmp.post_id = self.post_id
                self.session.add(tmp)
                self.session.commit()
                tmp_user_like = tmp

            action_id = AUDIT_ACTION_IDS[AUDIT_ACTION_USER_LIKE_POST]
            audit_model = self.audit_user_likes_forum_post_model(tmp_user_like, datetime.now(), self.user_id, action_id)
            self.session.add(audit_model)
            self.session.commit()

            return True, []


class BanUser(ForumAction):

    def __init__(self, invoker_id: int, target_id: int,
                 user_model=UserModel,
                 audit_user_model=AuditUserModel,
                 **kwargs):
        super().__init__(**kwargs)
        self.user_model = user_model
        self.audit_user_model = audit_user_model
        self.invoker_id = invoker_id
        self.target_id = target_id

    def perform(self) -> tuple[bool, list[str]]:
        user = GetUserModel(self.invoker_id).perform()
        if not user.is_banned:
            invoker = self.session.get(self.user_model, self.invoker_id)
            if not invoker:
                return False, ["Invoker id does not exists."]

            target = self.session.get(self.user_model, self.target_id)
            if not target:
                return False, ["Target id does not exists."]
            if target.role_id != ROLE_IDS[ROLE_USER]:
                return False, ["Target is not normal user."]

            if target.banned_timestamp is not None:
                return False, ["Target was already banned."]

            target.last_banned_by = self.invoker_id
            target.banned_timestamp = datetime.now()

            # TODO add action id
            action_id = AUDIT_ACTION_IDS[AUDIT_ACTION_USER_BANNED]
            audit_model = self.audit_user_model(target, datetime.now(), self.invoker_id, action_id)
            self.session.add(audit_model)
            self.session.commit()

            return True, []


class UnbanUser(ForumAction):

    def __init__(self, invoker_id: int, target_id: int,
                 user_model=UserModel,
                 audit_user_model=AuditUserModel,
                 **kwargs):
        super().__init__(**kwargs)
        self.audit_user_model = audit_user_model
        self.user_model = user_model
        self.invoker_id = invoker_id
        self.target_id = target_id

    def perform(self) -> tuple[bool, list[str]]:
        user = GetUserModel(self.invoker_id).perform()
        if not user.is_banned:
            # Will be used to update audit table
            invoker = self.session.get(self.user_model, self.invoker_id)
            if not invoker:
                return False, ["Invoker id does not exists."]

            target = self.session.get(self.user_model, self.target_id)
            if not target:
                return False, ["Target id does not exists."]

            if target.last_banned_by is None and target.banned_timestamp is None:
                return False, ["Target was not banned before."]

            time_now = datetime.now()

            target.banned_timestamp = None
            target.last_banned_by = None

            action_id = AUDIT_ACTION_IDS[AUDIT_ACTION_USER_UNBANNED]
            audit_model = self.audit_user_model(target, time_now, self.invoker_id, action_id)
            self.session.add(audit_model)
            self.session.commit()
            return True, []
