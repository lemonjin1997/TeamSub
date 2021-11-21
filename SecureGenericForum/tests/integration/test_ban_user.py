from app.core.forum_action import BanUser
from test_fixture_setup import *


class TestBanUser:

    @pytest.mark.parametrize("invoker_group, invoker_index, target_group, target_index", [
        ["moderators", 0, "users", 0],
        ["moderators", 0, "users", 1]
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
        action = BanUser(invoker_instance.user_id, target_instance.user_id, session=session)
        success, error_messages = action.perform()
        if not success:
            errors.append(f"{invoker_group} {invoker_index} ban {invoker_group} {invoker_index} failed")
            errors.extend(error_messages)

        else:
            # Validate
            user_model = session.get(UserModel, target_instance.user_id)
            if user_model.last_banned_by != invoker.id:
                errors.append("Last banned by does not match moderator id")
            if user_model.banned_timestamp is None:
                errors.append("Banned timestamp not set properly")

        assert not errors, "Error messages:\n{}".format("\n".join(errors))

    @pytest.mark.parametrize("invoker_group, invoker_index, target_group, target_index", [
        ["moderators", 0, "administrators", 0],
        ["moderators", 0, "moderators", 1]
    ])
    def test_invoker_invalid_ban_target(self, dummy_dataset, invoker_group, invoker_index, target_group, target_index):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        invoker = dummy_objects[invoker_group][invoker_index]
        target = dummy_objects[target_group][target_index]
        instances = dummy_objects["instances"]
        invoker_instance = instances[invoker.id]
        target_instance = instances[target.id]

        # Execute
        action = BanUser(invoker_instance.user_id, target_instance.user_id, session=session)
        success, error_messages = action.perform()
        if success:
            errors.append(f"{invoker_group} {invoker_index} should not be able to ban {target_group} {target_index}")
            errors.extend(error_messages)

        assert not errors, "Error messages:\n{}".format("\n".join(errors))

    @pytest.mark.parametrize("invoker_group, invoker_index, target_group, target_index", [
        ["moderators", 0, "users", 0]
    ])
    def test_role_can_ban(self, dummy_dataset, invoker_group, invoker_index, target_group, target_index):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        invoker = dummy_objects[invoker_group][invoker_index]
        target = dummy_objects[target_group][target_index]
        instances = dummy_objects["instances"]
        invoker_instance = instances[invoker.id]
        target_instance = instances[target.id]

        # Execute
        action = BanUser(invoker_instance.user_id, target_instance.user_id, session=session)
        allowed, error_messages = action.is_user_allowed(invoker_instance)

        # Validate
        if not allowed:
            errors.append(f"{invoker_group} {invoker_index} unable to ban {target_group} {target_index}")
            errors.extend(error_messages)

        assert not errors, "Error messages:\n{}".format("\n".join(errors))

    @pytest.mark.parametrize("invoker_group, invoker_index, target_group, target_index", [
        ["administrators", 0, "users", 0],
        ["users", 0, "users", 0]
    ])
    def test_role_cannot_ban(self, dummy_dataset, invoker_group, invoker_index, target_group, target_index):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        invoker = dummy_objects[invoker_group][invoker_index]
        target = dummy_objects[target_group][target_index]
        instances = dummy_objects["instances"]
        invoker_instance = instances[invoker.id]
        target_instance = instances[target.id]

        # Execute
        action = BanUser(invoker_instance.user_id, target_instance.user_id, session=session)
        allowed, error_messages = action.is_user_allowed(invoker_instance)

        # Validate
        if allowed:
            errors.append(f"{invoker_group} {invoker_index} should not be allowed to ban {target_group} {target_index}")
            errors.extend(error_messages)

        assert not errors, "Error messages:\n{}".format("\n".join(errors))

    def test_moderator_ban_banned_user(self, dummy_dataset):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        moderator = dummy_objects["moderators"][0]
        user_banned = dummy_objects["banned"][0]
        instances = dummy_objects["instances"]
        moderator_instance =    instances[moderator.id]
        banned_instance = instances[user_banned.id]

        # Execute
        action = BanUser(moderator_instance.user_id, banned_instance.user_id, session=session)
        success, error_messages = action.perform()
        if success:
            errors.append("Moderator should not be able to stack bans on banned user")
            errors.extend(error_messages)

        assert not errors, "Error messages:\n{}".format("\n".join(errors))
