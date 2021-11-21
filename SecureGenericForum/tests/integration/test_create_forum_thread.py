from app.core.forum_action import CreateForumThread
from test_fixture_setup import *


class TestCreateForumThread:

    def test_admin_cannot_create_forum_thread(self, dummy_dataset):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        admin = dummy_objects["administrators"][0]
        instances = dummy_objects["instances"]
        admin_instance = instances[admin.id]
        category = dummy_objects["categories"][0]
        new_name = "IO@)QW)WMQFKORR)@ORQKWQR"

        # Execute
        action = CreateForumThread(new_name, category.id, session=session)
        allowed, error_messages = action.is_user_allowed(admin_instance)

        # Validate
        if allowed:
            errors.append("Admin should not be allowed to create thread")
            errors.extend(error_messages)

        assert not errors, "Error messages:\n{}".format("\n".join(errors))

    def test_user_without_10_likes_cannot_create_forum_thread(self, dummy_dataset):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        user = dummy_objects["users"][0]
        instances = dummy_objects["instances"]
        user_instance = instances[user.id]
        category = dummy_objects["categories"][0]
        new_name = "IO@)QW)WMQFKORR)@ORQKWQR"

        # Execute
        action = CreateForumThread(new_name, category.id, session=session)
        allowed, error_messages = action.is_user_allowed(user_instance)

        # Validate
        if allowed:
            errors.append("User should not be allowed to create thread")
            errors.extend(error_messages)

        assert not errors, "Error messages:\n{}".format("\n".join(errors))

    def test_user_without_10_likes_cannot_create_forum_thread(self, dummy_dataset):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        user = dummy_objects["users"][0]
        instances = dummy_objects["instances"]
        user_instance = instances[user.id]
        category = dummy_objects["categories"][0]
        new_name = "IO@)QW)WMQFKORR)@ORQKWQR"

        # Execute
        action = CreateForumThread(new_name, category.id, session=session)
        allowed, error_messages = action.is_user_allowed(user_instance)

        # Validate
        if allowed:
            errors.append("User without 10 likes should not be allowed to create thread")
            errors.extend(error_messages)

        assert not errors, "Error messages:\n{}".format("\n".join(errors))

    def test_user_with_at_least_10_likes_can_create_forum_thread(self, dummy_dataset):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        user = dummy_objects["users"][1]
        instances = dummy_objects["instances"]
        user_instance = instances[user.id]
        category = dummy_objects["categories"][0]
        new_name = "IO@)QW)WMQFKORR)@ORQKWQR"

        # Execute
        action = CreateForumThread(new_name, category.id, session=session)
        allowed, error_messages = action.is_user_allowed(user_instance)

        # Validate
        if not allowed:
            errors.append("User with at least 10 likes should be allowed to create thread")
            errors.extend(error_messages)

        assert not errors, "Error messages:\n{}".format("\n".join(errors))

    def test_moderator_can_create_forum_thread(self, dummy_dataset):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        moderator = dummy_objects["moderators"][0]
        instances = dummy_objects["instances"]
        moderator_instance = instances[moderator.id]
        category = dummy_objects["categories"][0]
        new_name = "IO@)QW)WMQFKORR)@ORQKWQR"

        # Execute
        action = CreateForumThread(new_name, category.id, session=session)
        allowed, error_messages = action.is_user_allowed(moderator_instance)

        # Validate
        if not allowed:
            errors.append("Moderator should be allowed to create thread")
            errors.extend(error_messages)

        assert not errors, "Error messages:\n{}".format("\n".join(errors))

    def test_moderator_create_forum_thread_with_new_name(self, dummy_dataset):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        moderator = dummy_objects["moderators"][0]
        instances = dummy_objects["instances"]
        moderator_instance = instances[moderator.id]
        category = dummy_objects["categories"][0]
        new_name = "IO@)QW)WMQFKORR)@ORQKWQR"

        # Execute
        action = CreateForumThread(new_name, category.id, session=session)
        success, error_messages = action.perform(moderator)

        # Validate
        if not success:
            errors.append("Moderator failed to create thread with new name")
            errors.extend(error_messages)
        else:
            exists = session.query(ForumThreadModel) \
                         .filter(ForumThreadModel.name == new_name) \
                         .filter(ForumThreadModel.parent_category_id == category.id) \
                         .filter(ForumThreadModel.deleted_by == None) \
                         .filter(ForumThreadModel.delete_timestamp == None) \
                         .first() is not None
            if not exists:
                errors.append("Thread does not exists in db after creation")

        assert not errors, "Error messages:\n{}".format("\n".join(errors))

    def test_moderator_create_forum_thread_with_existing_name(self, dummy_dataset):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        moderator = dummy_objects["moderators"][0]
        instances = dummy_objects["instances"]
        moderator_instance = instances[moderator.id]
        thread = dummy_objects["threads"][0]
        category = dummy_objects["categories"][0]

        # Execute
        action = CreateForumThread(thread.name, category.id, session=session)
        success, error_messages = action.perform(moderator)

        # Validate
        if success:
            errors.append("Moderator should not be allowed to create duplicated thread")
            errors.extend(error_messages)

        assert not errors, "Error messages:\n{}".format("\n".join(errors))

    def test_user_at_least_10_likes_create_forum_thread_with_new_name(self, dummy_dataset):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        user = dummy_objects["users"][1]
        instances = dummy_objects["instances"]
        user_instance = instances[user.id]
        category = dummy_objects["categories"][0]
        new_name = "IO@)QW)WMQFKORR)@ORQKWQR"

        # Execute
        action = CreateForumThread(new_name, category.id, session=session)
        success, error_messages = action.perform(user)

        # Validate
        if not success:
            errors.append("User with at least 10 likes failed to create thread with new name")
            errors.extend(error_messages)
        else:
            exists = session.query(ForumThreadModel) \
                         .filter(ForumThreadModel.name == new_name) \
                         .filter(ForumThreadModel.parent_category_id == category.id) \
                         .filter(ForumThreadModel.deleted_by == None) \
                         .filter(ForumThreadModel.delete_timestamp == None) \
                         .first() is not None
            if not exists:
                errors.append("Thread does not exists in db after creation")

        assert not errors, "Error messages:\n{}".format("\n".join(errors))

    def test_user_at_least_10_likes_create_forum_thread_with_existing_name(self, dummy_dataset):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        user = dummy_objects["users"][0]
        instances = dummy_objects["instances"]
        user_instance = instances[user.id]
        thread = dummy_objects["threads"][0]
        category = dummy_objects["categories"][0]

        # Execute
        action = CreateForumThread(thread.name, category.id, session=session)
        success, error_messages = action.perform(user)

        # Validate
        if success:
            errors.append("User with at least 10 likes should not be allowed to create duplicated thread")
            errors.extend(error_messages)

        assert not errors, "Error messages:\n{}".format("\n".join(errors))
