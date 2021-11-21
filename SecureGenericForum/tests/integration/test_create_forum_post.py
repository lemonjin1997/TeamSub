from app.core.forum_action import CreateForumPosts
from test_fixture_setup import *


class TestCreateForumPosts:

    def test_admin_cannot_create_forum_post(self, dummy_dataset):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        admin = dummy_objects["administrators"][0]
        instances = dummy_objects["instances"]
        admin_instance = instances[admin.id]
        thread = dummy_objects["threads"][0]
        content = "IO@)QW)WMQFKORR)@ORQKWQR"

        # Execute
        action = CreateForumPosts(content, thread.id, session=session)
        allowed, error_messages = action.is_user_allowed(admin_instance)

        # Validate
        if allowed:
            errors.append("Admin should not be allowed to create post")
            errors.extend(error_messages)

        assert not errors, "Error messages:\n{}".format("\n".join(errors))

    def test_user_can_create_forum_post(self, dummy_dataset):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        user = dummy_objects["users"][0]
        instances = dummy_objects["instances"]
        user_instance = instances[user.id]
        thread = dummy_objects["threads"][0]
        content = "IO@)QW)WMQFKORR)@ORQKWQR"

        # Execute
        action = CreateForumPosts(content, thread.id, session=session)
        allowed, error_messages = action.is_user_allowed(user_instance)

        # Validate
        if not allowed:
            errors.append("User should be allowed to create post")
            errors.extend(error_messages)

        assert not errors, "Error messages:\n{}".format("\n".join(errors))

    def test_moderator_can_create_forum_post(self, dummy_dataset):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        moderator = dummy_objects["moderators"][0]
        instances = dummy_objects["instances"]
        moderator_instance = instances[moderator.id]
        thread = dummy_objects["threads"][0]
        content = "IO@)QW)WMQFKORR)@ORQKWQR"

        # Execute
        action = CreateForumPosts(content, thread.id, session=session)
        allowed, error_messages = action.is_user_allowed(moderator_instance)

        # Validate
        if not allowed:
            errors.append("Moderator should be allowed to create post")
            errors.extend(error_messages)

        assert not errors, "Error messages:\n{}".format("\n".join(errors))

    def test_moderator_create_forum_post(self, dummy_dataset):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        moderator = dummy_objects["moderators"][0]
        instances = dummy_objects["instances"]
        moderator_instance = instances[moderator.id]
        thread = dummy_objects["threads"][0]
        content = "IO@)QW)WMQFKORR)@ORQKWQR"

        # Execute
        action = CreateForumPosts(content, thread.id, session=session)
        success, error_messages = action.perform(moderator)

        # Validate
        if not success:
            errors.append("Moderator failed to create post")
            errors.extend(error_messages)
        else:
            exists = session.query(ForumPostModel) \
                         .filter(ForumPostModel.parent_thread_id == thread.id) \
                         .filter(ForumPostModel.created_by == moderator.id) \
                         .first() is not None
            if not exists:
                errors.append("Post does not exists in db after creation")

        assert not errors, "Error messages:\n{}".format("\n".join(errors))

    def test_user_create_forum_post(self, dummy_dataset):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        user = dummy_objects["users"][0]
        instances = dummy_objects["instances"]
        user_instance = instances[user.id]
        thread = dummy_objects["uthreads"][0]
        content = "IO@)QW)WMQFKORR)@ORQKWQR"

        # Execute
        action = CreateForumPosts(content, thread.id, session=session)
        success, error_messages = action.perform(user)

        # Validate
        if not success:
            errors.append("User failed to create post")
            errors.extend(error_messages)
        else:
            exists = session.query(ForumPostModel) \
                         .filter(ForumPostModel.parent_thread_id == thread.id) \
                         .filter(ForumPostModel.created_by == user.id) \
                         .first() is not None
            if not exists:
                errors.append("Post does not exists in db after creation")

        assert not errors, "Error messages:\n{}".format("\n".join(errors))
