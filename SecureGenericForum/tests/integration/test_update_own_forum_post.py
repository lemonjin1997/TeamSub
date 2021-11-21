from app.core.forum_action import UpdateOwnForumPost
from test_fixture_setup import *


class TestUpdateOwnForumPost:

    def test_user_can_update_own_forum_post(self, dummy_dataset):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        user = dummy_objects["users"][0]
        instances = dummy_objects["instances"]
        user_instance = instances[user.id]
        post = dummy_objects["posts"][0]
        content = "IO@)QW)WMQFKORR)@ORQKWQR"

        # Execute
        action = UpdateOwnForumPost(content, post.id, session=session)
        allowed, error_messages = action.is_user_allowed(user_instance)

        # Validate
        if not allowed:
            errors.append("User should be allowed to update own post")
            errors.extend(error_messages)

        assert not errors, "Error messages:\n{}".format("\n".join(errors))

    def test_moderator_can_update_own_forum_post(self, dummy_dataset):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        moderator = dummy_objects["moderators"][0]
        instances = dummy_objects["instances"]
        moderator_instance = instances[moderator.id]
        post = dummy_objects["mposts"][0]
        content = "IO@)QW)WMQFKORR)@ORQKWQR"

        # Execute
        action = UpdateOwnForumPost(content, post.id, session=session)
        allowed, error_messages = action.is_user_allowed(moderator_instance)

        # Validate
        if not allowed:
            errors.append("Moderator should be allowed to update own post")
            errors.extend(error_messages)

        assert not errors, "Error messages:\n{}".format("\n".join(errors))

    def test_moderator_update_own_forum_post(self, dummy_dataset):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        moderator = dummy_objects["moderators"][0]
        instances = dummy_objects["instances"]
        moderator_instance = instances[moderator.id]
        post = dummy_objects["mposts"][0]
        content = "IO@)QW)WMQFKORR)@ORQKWQR"

        # Execute
        action = UpdateOwnForumPost(content, post.id, session=session)
        success, error_messages = action.perform(moderator)

        # Validate
        if not success:
            errors.append("Moderator failed to update post with content")
            errors.extend(error_messages)
        else:
            post_model = session.get(ForumPostModel, post.id)
            if post_model.modified_by != moderator.id:
                errors.append("Post modified by is not the owner")

        assert not errors, "Error messages:\n{}".format("\n".join(errors))

    def test_user_update_own_forum_post(self, dummy_dataset):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        user = dummy_objects["users"][0]
        instances = dummy_objects["instances"]
        user_instance = instances[user.id]
        post = dummy_objects["posts"][0]
        content = "IO@)QW)WMQFKORR)@ORQKWQR"

        # Execute
        action = UpdateOwnForumPost(content, post.id, session=session)
        success, error_messages = action.perform(user)

        # Validate
        if not success:
            errors.append("User failed to update post with new name")
            errors.extend(error_messages)
        else:
            post_model = session.get(ForumPostModel, post.id)
            if post_model.modified_by != user.id:
                errors.append("Post modified by is not the owner")

        assert not errors, "Error messages:\n{}".format("\n".join(errors))
