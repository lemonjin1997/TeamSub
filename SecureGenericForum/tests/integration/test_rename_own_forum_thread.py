from app.core.forum_action import RenameOwnForumThread
from test_fixture_setup import *


class TestRenameOwnForumThread:

    def test_user_can_rename_own_forum_thread(self, dummy_dataset):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        user = dummy_objects["users"][1]
        instances = dummy_objects["instances"]
        user_instance = instances[user.id]
        uthread = dummy_objects["uthreads"][0]
        new_name = "IO@)QW)WMQFKORR)@ORQKWQR"

        # Execute
        action = RenameOwnForumThread(new_name, uthread.id, session=session)
        allowed, error_messages = action.is_user_allowed(user_instance)

        # Validate
        if not allowed:
            errors.append("User should be allowed to rename own thread")
            errors.extend(error_messages)

        assert not errors, "Error messages:\n{}".format("\n".join(errors))

    def test_moderator_can_rename_own_forum_thread(self, dummy_dataset):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        moderator = dummy_objects["moderators"][0]
        instances = dummy_objects["instances"]
        moderator_instance = instances[moderator.id]
        thread = dummy_objects["threads"][0]
        new_name = "IO@)QW)WMQFKORR)@ORQKWQR"

        # Execute
        action = RenameOwnForumThread(new_name, thread.id, session=session)
        allowed, error_messages = action.is_user_allowed(moderator_instance)

        # Validate
        if not allowed:
            errors.append("Moderator should be allowed to rename own thread")
            errors.extend(error_messages)

        assert not errors, "Error messages:\n{}".format("\n".join(errors))

    def test_moderator_rename_own_forum_thread_with_new_name(self, dummy_dataset):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        moderator = dummy_objects["moderators"][0]
        instances = dummy_objects["instances"]
        moderator_instance = instances[moderator.id]
        thread = dummy_objects["threads"][0]
        new_name = "IO@)QW)WMQFKORR)@ORQKWQR"

        # Execute
        action = RenameOwnForumThread(new_name, thread.id, session=session)
        success, error_messages = action.perform(moderator)

        # Validate
        if not success:
            errors.append("Moderator failed to rename thread with new name")
            errors.extend(error_messages)
        else:
            thread_model = session.get(ForumThreadModel, thread.id)
            if thread_model.name != new_name:
                errors.append("Thread was not renamed to new name")

        assert not errors, "Error messages:\n{}".format("\n".join(errors))

    def test_normal_user_rename_own_forum_thread_with_new_name(self, dummy_dataset):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        user = dummy_objects["users"][1]
        instances = dummy_objects["instances"]
        user_instance = instances[user.id]
        thread = dummy_objects["uthreads"][0]
        new_name = "IO@)QW)WMQFKORR)@ORQKWQR"

        # Execute
        action = RenameOwnForumThread(new_name, thread.id, session=session)
        success, error_messages = action.perform(user)

        # Validate
        if not success:
            errors.append("User failed to rename thread with new name")
            errors.extend(error_messages)
        else:
            thread_model = session.get(ForumThreadModel, thread.id)
            if thread_model.name != new_name:
                errors.append("Thread was not renamed to new name")

        assert not errors, "Error messages:\n{}".format("\n".join(errors))

    def test_moderator_rename_own_forum_thread_with_same_name(self, dummy_dataset):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        moderator = dummy_objects["moderators"][0]
        instances = dummy_objects["instances"]
        moderator_instance = instances[moderator.id]
        thread = dummy_objects["threads"][0]

        # Execute
        action = RenameOwnForumThread(thread.name, thread.id, session=session)
        success, error_messages = action.perform(moderator)

        # Validate
        if success:
            errors.append("Moderator should not be allowed to rename thread to the same name")
            errors.extend(error_messages)

        assert not errors, "Error messages:\n{}".format("\n".join(errors))

    def test_user_rename_own_forum_thread_with_same_name(self, dummy_dataset):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        user = dummy_objects["users"][1]
        instances = dummy_objects["instances"]
        user_instance = instances[user.id]
        thread = dummy_objects["uthreads"][0]

        # Execute
        action = RenameOwnForumThread(thread.name, thread.id, session=session)
        success, error_messages = action.perform(user)

        # Validate
        if success:
            errors.append("Moderator should not be allowed to rename thread to the same name")
            errors.extend(error_messages)

        assert not errors, "Error messages:\n{}".format("\n".join(errors))
