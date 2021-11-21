from __future__ import annotations

from sqlalchemy.sql.expression import true

from app.app import db
from app.core.model import RoleModel, UserLikesForumPostModel, ForumPostModel
from app.core.model import UserModel, ForumActionHasRequirementModel, ForumActionRequirementModel


class ActionRequirementFactory:

    def __init__(self):
        self.available_actions = {}

    def register_actions(self, cls):
        self.available_actions[cls.__name__] = cls
        return cls

    def create(self, requirement_name: str) -> ForumActionRequirement:
        pass

    def create_for(self, action_id: int, session=db.session) -> list[ForumActionRequirement]:
        requirement_ids = session.query(ForumActionHasRequirementModel).filter(
            ForumActionHasRequirementModel.forum_action_id == action_id).all()
        requirement_ids = [model.forum_action_requirement_id for model in requirement_ids]
        models = session.query(ForumActionRequirementModel).filter(
            ForumActionRequirementModel.id.in_(requirement_ids)).all()
        return [self.available_actions[model.name]() for model in models if model.name in self.available_actions]


action_requirement_factory = ActionRequirementFactory()


class ForumActionRequirement:

    def check(self, user: UserModel, *args, **kwargs) -> tuple[bool, list[str]]:
        pass


class UserMaximumRoleLevel(ForumActionRequirement):

    def __init__(self, minimum_role_level: int):
        self.minimum_role_level = minimum_role_level

    def check(self, user: UserModel, *args, session=db.session, **kwargs) -> tuple[bool, list[str]]:
        role_level = session.query(RoleModel).with_entities(RoleModel.level) \
            .filter(RoleModel.id == user.role_id) \
            .scalar()
        result = role_level <= self.minimum_role_level
        error_message = None if result else f"Insufficient role level, required {self.minimum_role_level}, found {role_level}"

        return result, [error_message]


@action_requirement_factory.register_actions
class UserMinimumModeratorRole(UserMaximumRoleLevel):

    def __init__(self):
        super().__init__(100)


class UserMinimumCumulativeLikes(ForumActionRequirement):

    def __init__(self, minimum_likes: int):
        self.minimum_likes = minimum_likes

    def check(self, user: UserModel, *args, session=db.session, **kwargs) -> tuple[bool, list[str]]:
        post_ids = session.query(ForumPostModel.id) \
            .filter(ForumPostModel.created_by == user.id) \
            .all()
        post_ids = [row[0] for row in post_ids]

        likes = session.query(UserLikesForumPostModel).filter(
            UserLikesForumPostModel.like == true(),
            UserLikesForumPostModel.post_id.in_(post_ids)
        ).count()

        result = likes >= self.minimum_likes
        error_message = None if result else f"Insufficient likes, required {self.minimum_likes}, found {likes}"

        return result, [error_message]


@action_requirement_factory.register_actions
class UserMinimum10CumulativeLikes(UserMinimumCumulativeLikes):

    def __init__(self):
        super().__init__(10)


@action_requirement_factory.register_actions
class UserMinimum10CumulativeLikesOrMinimumModeratorRole(UserMinimum10CumulativeLikes, UserMinimumModeratorRole):

    def __init__(self):
        UserMinimum10CumulativeLikes.__init__(self)
        UserMinimumModeratorRole.__init__(self)

    def check(self, user: UserModel, *args, **kwargs) -> tuple[bool, list[str]]:
        success, all_messages = UserMinimumModeratorRole.check(self, user, *args, **kwargs)
        if not success:
            success, messages = UserMinimum10CumulativeLikes.check(self, user, *args, **kwargs)
            all_messages.extend(messages)

        return success, all_messages
