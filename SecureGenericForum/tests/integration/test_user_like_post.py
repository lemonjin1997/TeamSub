from app.core.forum_action import UserLikePost
from test_fixture_setup import *


class TestUserLikePost:

    @pytest.mark.parametrize("invoker_group, invoker_index, post_group, post_index", [
        ["administrators", 0, "posts", 0]
    ])
    def test_role_cannot_like_forum_post(self, dummy_dataset, invoker_group, invoker_index, post_group, post_index):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        invoker = dummy_objects[invoker_group][invoker_index]
        instances = dummy_objects["instances"]
        invoker_instance = instances[invoker.id]
        post = dummy_objects[post_group][post_index]

        # Execute
        action = UserLikePost(post.id, invoker.id, session=session)
        allowed, error_messages = action.is_user_allowed(invoker_instance)

        # Validate
        if allowed:
            errors.append(f"{invoker_group} {invoker_index} should not be allowed to like post")
            errors.extend(error_messages)

        assert not errors, "Error messages:\n{}".format("\n".join(errors))

    @pytest.mark.parametrize("invoker_group, invoker_index, post_group, post_index", [
        ["moderators", 0, "posts", 0],
        ["users", 0, "posts", 0]
    ])
    def test_role_can_like_forum_post(self, dummy_dataset, invoker_group, invoker_index, post_group, post_index):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        invoker = dummy_objects[invoker_group][invoker_index]
        instances = dummy_objects["instances"]
        invoker_instance = instances[invoker.id]
        post = dummy_objects[post_group][post_index]

        # Execute
        action = UserLikePost(invoker.id, post.id, session=session)
        allowed, error_messages = action.is_user_allowed(invoker_instance)

        # Validate
        if not allowed:
            errors.append(f"{invoker_group} {invoker_index} should be allowed to like post")
            errors.extend(error_messages)

        assert not errors, "Error messages:\n{}".format("\n".join(errors))

    @pytest.mark.parametrize("invoker_group, invoker_index, post_group, post_index", [
        ["moderators", 0, "posts", 0],
        ["users", 0, "posts", 0]
    ])
    def test_role_success_likes_post(self, dummy_dataset, invoker_group, invoker_index, post_group, post_index):
        errors = []

        # Setup
        session, dummy_objects = dummy_dataset
        invoker = dummy_objects[invoker_group][invoker_index]
        instances = dummy_objects["instances"]
        invoker_instance = instances[invoker.id]
        post = dummy_objects[post_group][post_index]

        # Execute
        action = UserLikePost(invoker.id, post.id, session=session)
        success, error_messages = action.perform()

        # Validate
        if not success:
            errors.append(f"{invoker_group} {invoker_index} failed to like post")
            errors.extend(error_messages)
        else:
            exists = session.query(UserLikesForumPostModel.user_id == invoker.id) \
                         .filter(UserLikesForumPostModel.post_id == post.id) \
                         .first() is not None

            if not exists:
                errors.append(f"Post liked by {invoker_group} {invoker_index} not reflected in database")

        assert not errors, "Error messages:\n{}".format("\n".join(errors))
