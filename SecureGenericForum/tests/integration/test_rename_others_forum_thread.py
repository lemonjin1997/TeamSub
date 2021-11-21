from app.core.forum_action import RenameOthersForumThread
from test_fixture_setup import *


class TestRenameOtherForumThread:

    @pytest.mark.parametrize("invoker_group, invoker_index, thread_group, thread_index, new_name", [
        ["administrators", 0, "threads", 0, "IO@)QW)WMQFKORR)@ORQKWQR"],
        ["users", 1, "threads", 0, "IO@)QW)WMQFKORR)@ORQKWQR"]
    ])
    def test_role_cannot_rename_others_thread(self, dummy_dataset, invoker_group, invoker_index, thread_group,
                                              thread_index, new_name):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        invoker = dummy_objects[invoker_group][invoker_index]
        instances = dummy_objects["instances"]
        invoker_instance = instances[invoker.id]
        thread = dummy_objects[thread_group][thread_index]

        # Execute
        action = RenameOthersForumThread(new_name, thread.id, session=session)
        allowed, error_messages = action.is_user_allowed(invoker_instance)

        # Validate
        if allowed:
            errors.append(f"{invoker_group} {invoker_index} should not be allowed to rename others thread")
            errors.extend(error_messages)

        assert not errors, "Error messages:\n{}".format("\n".join(errors))

    @pytest.mark.parametrize("invoker_group, invoker_index, thread_group, thread_index, new_name", [
        ["moderators", 0, "uthreads", 0, "IO@)QW)WMQFKORR)@ORQKWQR"]
    ])
    def test_role_can_rename_others_thread(self, dummy_dataset, invoker_group, invoker_index, thread_group,
                                           thread_index, new_name):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        invoker = dummy_objects[invoker_group][invoker_index]
        instances = dummy_objects["instances"]
        invoker_instance = instances[invoker.id]
        thread = dummy_objects[thread_group][thread_index]

        # Execute
        action = RenameOthersForumThread(new_name, thread.id, session=session)
        allowed, error_messages = action.is_user_allowed(invoker_instance)

        # Validate
        if not allowed:
            errors.append(f"{invoker_group} {invoker_index} should be allowed to rename others thread")
            errors.extend(error_messages)

        assert not errors, "Error messages:\n{}".format("\n".join(errors))

    def test_moderator_rename_others_forum_thread_with_new_name(self, dummy_dataset):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        moderator = dummy_objects["moderators"][0]
        instances = dummy_objects["instances"]
        moderator_instance = instances[moderator.id]
        thread = dummy_objects["uthreads"][0]
        new_name = "IO@)QW)WMQFKORR)@ORQKWQR"

        # Execute
        action = RenameOthersForumThread(new_name, thread.id, session=session)
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

    def test_moderator_rename_others_forum_thread_with_same_name(self, dummy_dataset):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        moderator = dummy_objects["moderators"][0]
        instances = dummy_objects["instances"]
        moderator_instance = instances[moderator.id]
        thread = dummy_objects["threads"][0]

        # Execute
        action = RenameOthersForumThread(thread.name, thread.id, session=session)
        success, error_messages = action.perform(moderator)

        # Validate
        if success:
            errors.append("Moderator should not be allowed to rename thread to the same name")
            errors.extend(error_messages)

        assert not errors, "Error messages:\n{}".format("\n".join(errors))
