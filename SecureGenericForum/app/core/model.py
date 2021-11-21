from datetime import datetime

from app.app import db
from flask_login import UserMixin

# tables prefixed with a_ represents a clone table for audit purpose

class UserModel(db.Model, UserMixin):
    __tablename__ = "user"
    # query = db.Query

    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    name = db.Column(db.String(512), nullable=False)
    email = db.Column(db.String(512), unique=True, nullable=False)
    password_salt = db.Column(db.String(512), nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)
    profile_image_uri = db.Column(db.String(512), nullable=True)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"), nullable=False)
    failed_login_count = db.Column(db.Integer, nullable=False, default=0)
    last_posted_timestamp = db.Column(db.TIMESTAMP, nullable=True)
    last_login_timestamp = db.Column(db.TIMESTAMP, nullable=True)
    banned_timestamp = db.Column(db.TIMESTAMP, nullable=True)
    last_banned_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    otp = db.Column(db.String(512), nullable=True)
    verified_user = db.Column(db.Boolean, nullable=True)
    
    def __init__(self, name: str, email: str, password_salt: str, password_hash: str, role_id: int):
        self.name = name
        self.email = email
        self.password_salt = password_salt
        self.password_hash = password_hash
        self.role_id = role_id

    @property
    def is_banned(self) -> bool:
        return self.banned_timestamp is not None
        


class ForumCategoryModel(db.Model):
    __tablename__ = "forum_category"
    # query = db.Query

    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    name = db.Column(db.String(512), unique=False, nullable=False)
    create_timestamp = db.Column(db.TIMESTAMP, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    delete_timestamp = db.Column(db.TIMESTAMP, nullable=True)
    deleted_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    modified_timestamp = db.Column(db.TIMESTAMP, nullable=True)
    modified_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

    def __init__(self, name: str, create_timestamp: datetime, created_by: int):
        self.name = name
        self.create_timestamp = create_timestamp
        self.created_by = created_by


class ForumThreadModel(db.Model):
    __tablename__ = "forum_thread"
    # query = db.Query

    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    name = db.Column(db.String(512), unique=False, nullable=False)
    parent_category_id = db.Column(db.Integer, db.ForeignKey("forum_category.id"), nullable=False)
    create_timestamp = db.Column(db.TIMESTAMP, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    delete_timestamp = db.Column(db.TIMESTAMP, nullable=True)
    deleted_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    modified_timestamp = db.Column(db.TIMESTAMP, nullable=True)
    modified_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

    def __init__(self, name: str, parent_category_id: int, create_timestamp: datetime, created_by: int):
        self.name = name
        self.parent_category_id = parent_category_id
        self.create_timestamp = create_timestamp
        self.created_by = created_by


class ForumPostModel(db.Model):
    __tablename__ = "forum_post"
    # query = db.Query

    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    content_uri = db.Column(db.String(512), nullable=False)
    parent_thread_id = db.Column(db.Integer, db.ForeignKey("forum_thread.id"), nullable=False)
    create_timestamp = db.Column(db.TIMESTAMP, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    delete_timestamp = db.Column(db.TIMESTAMP, nullable=True)
    deleted_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    modified_timestamp = db.Column(db.TIMESTAMP, nullable=True)
    modified_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

    def __init__(self, content_uri: str, parent_thread_id: int, create_timestamp: datetime, created_by: int):
        self.content_uri = content_uri
        self.parent_thread_id = parent_thread_id
        self.create_timestamp = create_timestamp
        self.created_by = created_by


class UserLikesForumPostModel(db.Model):
    __tablename__ = "user_likes_forum_post"
    # query = db.Query

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("forum_post.id"), primary_key=True, nullable=False)
    like = db.Column(db.Boolean, nullable=False)

    def __init__(self, user_id: int, post_id: int, like: bool):
        self.user_id = user_id
        self.post_id = post_id
        self.like = like


# permission tables

class RoleModel(db.Model):
    __tablename__ = "role"
    # query = db.Query

    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    name = db.Column(db.String(512), unique=True, nullable=False)
    level = db.Column(db.Integer, unique=True, nullable=False)

    def __init__(self, name: str, level: int):
        self.name = name
        self.level = level


class ForumActionModel(db.Model):
    __tablename__ = "forum_action"
    # query = db.Query

    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    name = db.Column(db.String(512), unique=True, nullable=False)

    def __init__(self, name: str):
        self.name = name


class ForumActionRequirementModel(db.Model):
    __tablename__ = "forum_action_requirement"
    # query = db.Query

    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    name = db.Column(db.String(512), unique=True, nullable=False)

    def __init__(self, name: str):
        self.name = name


class ForumActionHasRequirementModel(db.Model):
    __tablename__ = "forum_action_has_requirement"
    # query = db.Query

    forum_action_id = db.Column(db.Integer, db.ForeignKey("forum_action.id"), primary_key=True, nullable=False)
    forum_action_requirement_id = db.Column(db.Integer, db.ForeignKey("forum_action_requirement.id"), primary_key=True,
                                            nullable=False)

    def __init__(self, forum_action_id: int, forum_action_requirement_id: int):
        self.forum_action_id = forum_action_id
        self.forum_action_requirement_id = forum_action_requirement_id


class RoleHasForumActionModel(db.Model):
    __tablename__ = "role_has_forum_action"
    # query = db.Query

    role_id = db.Column(db.Integer, db.ForeignKey("role.id"), primary_key=True, nullable=False)
    forum_action_id = db.Column(db.Integer, db.ForeignKey("forum_action.id"), primary_key=True, nullable=False)

    def __init__(self, role_id, forum_action_id):
        self.role_id = role_id
        self.forum_action_id = forum_action_id


class UserInstanceModel(db.Model):
    __tablename__ = "user_instance"
    # query = db.Query

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True, nullable=False)
    ip_location = db.Column(db.String(512), nullable=False)
    login_timestamp = db.Column(db.TIMESTAMP, nullable=True)
    browser_header = db.Column(db.String(512), nullable=False)
    encryption_key = db.Column(db.String(512), nullable=True)

    def __init__(self, user_id: int, ip_location: str, browser_header: str):
        self.user_id = user_id
        self.ip_location = ip_location
        self.browser_header = browser_header

    @property
    def is_active(self) -> bool:
        return True

    def get_id(self) -> int:
        return self.user_id

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def is_anonymous(self) -> bool:
        return False


class AuditUserModel(db.Model):
    __tablename__ = "a_user"
    # query = db.Query

    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String(512), nullable=False)
    email = db.Column(db.String(512), nullable=False)
    password_salt = db.Column(db.String(512), nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)
    profile_image_uri = db.Column(db.String(512), nullable=True)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"), nullable=False)
    failed_login_count = db.Column(db.Integer, nullable=False, default=0)
    last_posted_timestamp = db.Column(db.TIMESTAMP, nullable=True)
    last_login_timestamp = db.Column(db.TIMESTAMP, nullable=True)
    banned_timestamp = db.Column(db.TIMESTAMP, nullable=True)
    last_banned_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

    modified_timestamp = db.Column(db.TIMESTAMP, nullable=False)
    modified_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    action_id = db.Column(db.Integer, db.ForeignKey("user_action.id"), nullable=False)

    def __init__(self, model: UserModel, modified_timestamp: datetime, modified_by: int, action_id: int):
        self.user_id = model.id
        self.name = model.name
        self.email = model.email
        self.password_salt = model.password_salt
        self.password_hash = model.password_hash
        self.profile_image_uri = model.profile_image_uri
        self.role_id = model.role_id
        self.failed_login_count = model.failed_login_count
        self.last_posted_timestamp = model.last_posted_timestamp
        self.last_login_timestamp = model.last_login_timestamp
        self.banned_timestamp = model.banned_timestamp
        self.last_banned_by = model.last_banned_by

        self.modified_timestamp = modified_timestamp
        self.modified_by = modified_by
        self.action_id = action_id


class ForumUserActionModel(db.Model):
    __tablename__ = "user_action"
    # query = db.Query

    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    action = db.Column(db.String(512), unique=True, nullable=False)

    def __init__(self, action: str):
        self.action = action


class AuditForumCategoryModel(db.Model):
    __tablename__ = "a_forum_category"
    # query = db.Query

    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    category_id = db.Column(db.Integer, db.ForeignKey("forum_category.id"), nullable=False)
    name = db.Column(db.String(512), nullable=False)
    create_timestamp = db.Column(db.TIMESTAMP, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    delete_timestamp = db.Column(db.TIMESTAMP, nullable=True)
    deleted_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

    modified_timestamp = db.Column(db.TIMESTAMP, nullable=False)
    modified_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    action_id = db.Column(db.Integer, db.ForeignKey("forum_category_action.id"), nullable=False)

    def __init__(self, model: ForumCategoryModel, modified_timestamp: datetime, modified_by: int, action_id: int):
        self.category_id = model.id
        self.name = model.name
        self.create_timestamp = model.create_timestamp
        self.created_by = model.created_by
        self.delete_timestamp = model.delete_timestamp
        self.deleted_by = model.deleted_by

        self.modified_timestamp = modified_timestamp
        self.modified_by = modified_by
        self.action_id = action_id


class ForumCategoryActionModel(db.Model):
    __tablename__ = "forum_category_action"
    # query = db.Query

    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    action = db.Column(db.String(512), unique=True, nullable=False)

    def __init__(self, action: str):
        self.action = action


class AuditForumThreadModel(db.Model):
    __tablename__ = "a_forum_thread"
    # query = db.Query

    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    thread_id = db.Column(db.Integer, db.ForeignKey("forum_thread.id"), nullable=False)
    name = db.Column(db.String(512), nullable=False)
    parent_category_id = db.Column(db.Integer, db.ForeignKey("forum_category.id"), nullable=False)
    create_timestamp = db.Column(db.TIMESTAMP, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    delete_timestamp = db.Column(db.TIMESTAMP, nullable=True)
    deleted_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

    modified_timestamp = db.Column(db.TIMESTAMP, nullable=False)
    modified_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    action_id = db.Column(db.Integer, db.ForeignKey("forum_thread_action.id"), nullable=False)

    def __init__(self, model: ForumThreadModel, modified_timestamp: datetime, modified_by: int, action_id: int):
        self.thread_id = model.id
        self.name = model.name
        self.parent_category_id = model.parent_category_id
        self.create_timestamp = model.create_timestamp
        self.created_by = model.created_by
        self.delete_timestamp = model.delete_timestamp
        self.deleted_by = model.deleted_by

        self.modified_timestamp = modified_timestamp
        self.modified_by = modified_by
        self.action_id = action_id


class ForumThreadActionModel(db.Model):
    __tablename__ = "forum_thread_action"
    # query = db.Query

    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    action = db.Column(db.String(512), unique=True, nullable=False)

    def __init__(self, action: str):
        self.action = action


class AuditForumPostModel(db.Model):
    __tablename__ = "a_forum_post"
    # query = db.Query

    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey("forum_post.id"), nullable=False)
    content_uri = db.Column(db.String(512), nullable=False)
    parent_thread_id = db.Column(db.Integer, db.ForeignKey("forum_thread.id"), nullable=False)
    create_timestamp = db.Column(db.TIMESTAMP, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    delete_timestamp = db.Column(db.TIMESTAMP, nullable=True)
    deleted_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

    modified_timestamp = db.Column(db.TIMESTAMP, nullable=False)
    modified_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    action_id = db.Column(db.Integer, db.ForeignKey("forum_post_action.id"), nullable=False)

    def __init__(self, model: ForumPostModel, modified_timestamp: datetime, modified_by: int, action_id: int):
        self.post_id = model.id
        self.content_uri = model.content_uri
        self.parent_thread_id = model.parent_thread_id
        self.create_timestamp = model.create_timestamp
        self.created_by = model.created_by
        self.delete_timestamp = model.delete_timestamp
        self.deleted_by = model.deleted_by

        self.modified_timestamp = modified_timestamp
        self.modified_by = modified_by
        self.action_id = action_id


class ForumPostActionModel(db.Model):
    __tablename__ = "forum_post_action"
    # query = db.Query

    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    action = db.Column(db.String(512), unique=True, nullable=False)

    def __init__(self, action: str):
        self.action = action


class AuditUserLikesForumPostModel(db.Model):
    __tablename__ = "a_user_likes_forum_post"
    # query = db.Query

    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("forum_post.id"), nullable=False)
    like = db.Column(db.Boolean, nullable=False)

    modified_timestamp = db.Column(db.TIMESTAMP, nullable=False)
    modified_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    action_id = db.Column(db.Integer, db.ForeignKey("user_likes_forum_post_action.id"), nullable=False)

    def __init__(self, model: UserLikesForumPostModel, modified_timestamp: datetime, modified_by: int, action_id: int):
        self.user_id = model.user_id
        self.post_id = model.post_id
        self.like = model.like

        self.modified_timestamp = modified_timestamp
        self.modified_by = modified_by
        self.action_id = action_id


class UserLikesForumPostActionModel(db.Model):
    __tablename__ = "user_likes_forum_post_action"
    # query = db.Query

    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    action = db.Column(db.String(512), unique=True, nullable=False)

    def __init__(self, action: str):
        self.action = action
