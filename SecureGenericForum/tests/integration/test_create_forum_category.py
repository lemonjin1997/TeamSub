from app.core.forum_action import CreateForumCategory
from test_fixture_setup import *


class TestCreateForumCategory:

    def test_admin_cannot_create_forum_category(self, dummy_dataset):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        admin = dummy_objects["administrators"][0]
        instances = dummy_objects["instances"]
        admin_instance = instances[admin.id]
        new_name = "IO@)QW)WMQFKORR)@ORQKWQR"

        # Execute
        action = CreateForumCategory(new_name, session=session)
        allowed, error_messages = action.is_user_allowed(admin_instance)

        # Validate
        if allowed:
            errors.append("Admin should not be allowed to create category")
            errors.extend(error_messages)

        assert not errors, "Error messages:\n{}".format("\n".join(errors))

    def test_user_cannot_create_forum_category(self, dummy_dataset):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        user = dummy_objects["users"][0]
        instances = dummy_objects["instances"]
        user_instance = instances[user.id]
        new_name = "IO@)QW)WMQFKORR)@ORQKWQR"

        # Execute
        action = CreateForumCategory(new_name, session=session)
        allowed, error_messages = action.is_user_allowed(user_instance)

        # Validate
        if allowed:
            errors.append("User should not be allowed to create category")
            errors.extend(error_messages)

        assert not errors, "Error messages:\n{}".format("\n".join(errors))

    def test_moderator_can_create_forum_category(self, dummy_dataset):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        moderator = dummy_objects["moderators"][0]
        instances = dummy_objects["instances"]
        moderator_instance = instances[moderator.id]
        new_name = "IO@)QW)WMQFKORR)@ORQKWQR"

        # Execute
        action = CreateForumCategory(new_name, session=session)
        allowed, error_messages = action.is_user_allowed(moderator_instance)

        # Validate
        if not allowed:
            errors.append("Moderator should be allowed to create category")
            errors.extend(error_messages)

        assert not errors, "Error messages:\n{}".format("\n".join(errors))

    def test_moderator_create_forum_category_with_new_name(self, dummy_dataset):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        moderator = dummy_objects["moderators"][0]
        instances = dummy_objects["instances"]
        moderator_instance = instances[moderator.id]
        new_name = "IO@)QW)WMQFKORR)@ORQKWQR"

        # Execute
        action = CreateForumCategory(new_name, session=session)
        success, error_messages = action.perform(moderator)
        

        # Validate
        if not success:
            errors.append("Moderator failed to create category with new name")
            errors.extend(error_messages)
        else:
            exists = session.query(ForumCategoryModel) \
                         .filter(ForumCategoryModel.name == new_name) \
                         .filter(ForumCategoryModel.deleted_by == None) \
                         .filter(ForumCategoryModel.delete_timestamp == None) \
                         .first() is not None
            if not exists:
                errors.append("Category does not exists in db after creation")

        assert not errors, "Error messages:\n{}".format("\n".join(errors))

    def test_moderator_create_forum_category_with_existing_name(self, dummy_dataset):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        moderator = dummy_objects["moderators"][0]
        instances = dummy_objects["instances"]
        moderator_instance = instances[moderator.id]
        category = dummy_objects["categories"][0]

        # Execute
        action = CreateForumCategory(category.name, session=session)
        success, error_messages = action.perform(moderator)

        # Validate
        if success:
            errors.append("Moderator should not be allowed to create duplicated category")
            errors.extend(error_messages)

        assert not errors, "Error messages:\n{}".format("\n".join(errors))
