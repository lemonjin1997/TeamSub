from app.core.forum_action import RenameForumCategory
from test_fixture_setup import *


class TestRenameForumCategory:

    def test_admin_cannot_rename_forum_category(self, dummy_dataset):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        admin = dummy_objects["administrators"][0]
        instances = dummy_objects["instances"]
        admin_instance = instances[admin.id]
        category = dummy_objects["categories"][0]
        new_name = "IO@)QW)WMQFKORR)@ORQKWQR"

        # Execute
        action = RenameForumCategory(new_name, category.id, session=session)
        allowed, error_messages = action.is_user_allowed(admin_instance)

        # Validate
        if allowed:
            errors.append("Admin should not be allowed to rename category")
            errors.extend(error_messages)

        assert not errors, "Error messages:\n{}".format("\n".join(errors))

    def test_user_cannot_rename_forum_category(self, dummy_dataset):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        user = dummy_objects["users"][0]
        instances = dummy_objects["instances"]
        user_instance = instances[user.id]
        category = dummy_objects["categories"][0]
        new_name = "IO@)QW)WMQFKORR)@ORQKWQR"

        # Execute
        action = RenameForumCategory(new_name, category.id, session=session)
        allowed, error_messages = action.is_user_allowed(user_instance)

        # Validate
        if allowed:
            errors.append("User should not be allowed to rename category")
            errors.extend(error_messages)

        assert not errors, "Error messages:\n{}".format("\n".join(errors))

    def test_moderator_can_rename_forum_category(self, dummy_dataset):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        moderator = dummy_objects["moderators"][0]
        instances = dummy_objects["instances"]
        moderator_instance = instances[moderator.id]
        category = dummy_objects["categories"][0]
        new_name = "IO@)QW)WMQFKORR)@ORQKWQR"

        # Execute
        action = RenameForumCategory(new_name, category.id, session=session)
        allowed, error_messages = action.is_user_allowed(moderator_instance)

        # Validate
        if not allowed:
            errors.append("Moderator should be allowed to rename category")
            errors.extend(error_messages)

        assert not errors, "Error messages:\n{}".format("\n".join(errors))

    def test_moderator_rename_forum_category_with_new_name(self, dummy_dataset):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        moderator = dummy_objects["moderators"][0]
        instances = dummy_objects["instances"]
        moderator_instance = instances[moderator.id]
        category = dummy_objects["categories"][0]
        new_name = "IO@)QW)WMQFKORR)@ORQKWQR"

        # Execute
        action = RenameForumCategory(new_name, category.id, session=session)
        success, error_messages = action.perform(moderator)

        # Validate
        if not success:
            errors.append("Moderator failed to rename category with new name")
            errors.extend(error_messages)
        else:
            category_model = session.get(ForumCategoryModel, category.id)
            if category_model.name != new_name:
                errors.append("Category was not renamed to new name")

        assert not errors, "Error messages:\n{}".format("\n".join(errors))

    def test_moderator_rename_forum_category_with_same_name(self, dummy_dataset):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        moderator = dummy_objects["moderators"][0]
        instances = dummy_objects["instances"]
        moderator_instance = instances[moderator.id]
        category = dummy_objects["categories"][0]

        # Execute
        action = RenameForumCategory(category.name, category.id, session=session)
        success, error_messages = action.perform(moderator)

        # Validate
        if success:
            errors.append("Moderator should not be allowed to rename category to the same name")
            errors.extend(error_messages)

        assert not errors, "Error messages:\n{}".format("\n".join(errors))
