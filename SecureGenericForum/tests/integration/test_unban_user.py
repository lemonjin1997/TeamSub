from app.core.forum_action import UnbanUser
from test_fixture_setup import *


class TestUnbanUser:

    @pytest.mark.parametrize("invoker_group, invoker_index, target_group, target_index", [
        ["moderators", 0, "banned", 0]
    ])
    def test_invoker_valid_ban_target(self, dummy_dataset, invoker_group, invoker_index, target_group, target_index):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        invoker = dummy_objects[invoker_group][invoker_index]
        target = dummy_objects[target_group][target_index]
        instances = dummy_objects["instances"]
        invoker_instance = instances[invoker.id]
        target_instance = instances[target.id]

        # Execute
        action = UnbanUser(invoker_instance.user_id,target_instance.user_id, session=session)
        success, error_messages = action.perform()
        if not success:
            errors.append(f"{invoker_group} {invoker_index} unban {invoker_group} {invoker_index} failed")
            errors.extend(error_messages)
        else:
            # Validate
            user_model = session.get(UserModel, target_instance.user_id)
            if user_model.last_banned_by is not None:
                errors.append("Last banned by not cleared")
            if user_model.banned_timestamp is not None:
                errors.append("Banned timestamp not cleared")

        assert not errors, "Error messages:\n{}".format("\n".join(errors))

    @pytest.mark.parametrize("invoker_group, invoker_index, target_group, target_index", [
        ["moderators", 0, "users", 0]
    ])
    def test_invoker_invalid_unban_target(self, dummy_dataset, invoker_group, invoker_index, target_group,
                                          target_index):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        invoker = dummy_objects[invoker_group][invoker_index]
        target = dummy_objects[target_group][target_index]
        instances = dummy_objects["instances"]
        invoker_instance = instances[invoker.id]
        target_instance = instances[target.id]

        # Execute
        action = UnbanUser(invoker_instance.user_id, target_instance.user_id, session=session)
        success, error_messages = action.perform()
        if success:
            errors.append(f"{invoker_group} {invoker_index} should not unban not-banned {target_group} {target_index}")
            errors.extend(error_messages)

        assert not errors, "Error messages:\n{}".format("\n".join(errors))

    @pytest.mark.parametrize("invoker_group, invoker_index, target_group, target_index", [
        ["moderators", 0, "banned", 0]
    ])
    def test_role_can_unban(self, dummy_dataset, invoker_group, invoker_index, target_group, target_index):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        invoker = dummy_objects[invoker_group][invoker_index]
        target = dummy_objects[target_group][target_index]
        instances = dummy_objects["instances"]
        invoker_instance = instances[invoker.id]
        target_instance = instances[target.id]

        # Execute
        action = UnbanUser(invoker_instance.user_id, target_instance.user_id, session=session)
        allowed, error_messages = action.is_user_allowed(invoker_instance)

        # Validate
        if not allowed:
            errors.append(f"{invoker_group} {invoker_index} unable to unban {target_group} {target_index}")
            errors.extend(error_messages)

        assert not errors, "Error messages:\n{}".format("\n".join(errors))

    @pytest.mark.parametrize("invoker_group, invoker_index, target_group, target_index", [
        ["administrators", 0, "banned", 0],
        ["users", 0, "banned", 0]
    ])
    def test_role_cannot_unban(self, dummy_dataset, invoker_group, invoker_index, target_group, target_index):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        invoker = dummy_objects[invoker_group][invoker_index]
        target = dummy_objects[target_group][target_index]
        instances = dummy_objects["instances"]
        invoker_instance = instances[invoker.id]
        target_instance = instances[target.id]

        # Execute
        action = UnbanUser(invoker_instance.user_id, target_instance.user_id, session=session)
        allowed, error_messages = action.is_user_allowed(invoker_instance)

        # Validate
        if allowed:
            errors.append(
                f"{invoker_group} {invoker_index} should not be allowed to unban {target_group} {target_index}")
            errors.extend(error_messages)

        assert not errors, "Error messages:\n{}".format("\n".join(errors))
