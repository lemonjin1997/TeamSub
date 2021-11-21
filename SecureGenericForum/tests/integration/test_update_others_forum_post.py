from app.core.forum_action import UpdateOthersForumPost
from test_fixture_setup import *


class TestUpdateOthersForumPost:

    def test_admin_cannot_update_other_forum_post(self, dummy_dataset):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        admin = dummy_objects["administrators"][0]
        instances = dummy_objects["instances"]
        admin_instance = instances[admin.id]
        post = dummy_objects["posts"][0]
        content = "IO@)QW)WMQFKORR)@ORQKWQR"

        # Execute
        action = UpdateOthersForumPost(content, post.id, session=session)
        allowed, error_messages = action.is_user_allowed(admin_instance)

        # Validate
        if allowed:
            errors.append("Admin should not be allowed to update others post")
            errors.extend(error_messages)

        assert not errors, "Error messages:\n{}".format("\n".join(errors))

    def test_user_cannot_update_other_forum_post(self, dummy_dataset):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        user = dummy_objects["users"][0]
        instances = dummy_objects["instances"]
        user_instance = instances[user.id]
        post = dummy_objects["posts"][0]
        content = "IO@)QW)WMQFKORR)@ORQKWQR"

        # Execute
        action = UpdateOthersForumPost(content, post.id, session=session)
        allowed, error_messages = action.is_user_allowed(user_instance)

        # Validate
        if allowed:
            errors.append("User should not be allowed to update others post")
            errors.extend(error_messages)

        assert not errors, "Error messages:\n{}".format("\n".join(errors))

    def test_moderator_can_update_others_forum_post(self, dummy_dataset):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        moderator = dummy_objects["moderators"][0]
        instances = dummy_objects["instances"]
        moderator_instance = instances[moderator.id]
        post = dummy_objects["posts"][0]
        content = "IO@)QW)WMQFKORR)@ORQKWQR"

        # Execute
        action = UpdateOthersForumPost(content, post.id, session=session)
        allowed, error_messages = action.is_user_allowed(moderator_instance)

        # Validate
        if not allowed:
            errors.append("Moderator should be allowed to update others post")
            errors.extend(error_messages)

        assert not errors, "Error messages:\n{}".format("\n".join(errors))

    def test_moderator_update_others_forum_post(self, dummy_dataset):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        moderator = dummy_objects["moderators"][0]
        instances = dummy_objects["instances"]
        moderator_instance = instances[moderator.id]
        post = dummy_objects["posts"][0]
        content = "IO@)QW)WMQFKORR)@ORQKWQR"

        # Execute
        action = UpdateOthersForumPost(content, post.id, session=session)
        success, error_messages = action.perform(moderator)

        # Validate
        if not success:
            errors.append("Moderator failed to update others post with content")
            errors.extend(error_messages)
        else:
            post_model = session.get(ForumPostModel, post.id)
            if post_model.modified_by != moderator.id:
                errors.append("Post modified by is not the owner")

        assert not errors, "Error messages:\n{}".format("\n".join(errors))
