from app.core.action_requirement import *
from app.core.forum_action import *
from app.core.model import *
from os import environ


def setup_constants(session):
    setup_action_constants(session, AUDIT_ACTION_IDS, ForumUserActionModel, AUDIT_USER_MODEL_ACTIONS)
    setup_action_constants(session, AUDIT_ACTION_IDS, ForumPostActionModel, AUDIT_POST_MODEL_ACTIONS)
    setup_action_constants(session, AUDIT_ACTION_IDS, ForumCategoryActionModel, AUDIT_CATEGORY_MODEL_ACTIONS)
    setup_action_constants(session, AUDIT_ACTION_IDS, ForumThreadActionModel, AUDIT_THREAD_MODEL_ACTIONS)
    setup_action_constants(session, AUDIT_ACTION_IDS, UserLikesForumPostActionModel, AUDIT_USER_LIKE_POST_ACTIONS)
    #setup_action_constants(session, AUDIT_ACTION_IDS, , AUDIT_ACTION_ADMIN_EDIT_ROLE)
    setup_role_constants(session, RoleModel, ROLE_IDS, ROLES)


def setup_action_constants(session, global_action_ids, base_model, actions):
    models = session.query(base_model).all()
    existing_actions = [x.action for x in models]
    missing_actions = [action for action in actions if action not in existing_actions]
    missing_models = list(map(base_model, missing_actions))
    session.bulk_save_objects(missing_models, return_defaults=True)
    session.commit()

    models.extend(missing_models)
    for model in models:
        if model.action in global_action_ids and global_action_ids[model.action] != model.id:
            raise Exception("Holy moly discrepancy between constant ids")
        global_action_ids[model.action] = model.id


def setup_role_constants(session, base_model, global_role_ids, all_roles):
    models = session.query(base_model).all()
    existing_names = [x.name for x in models]
    missing_models = [base_model(name, level) for name, level in all_roles.items() if name not in existing_names]
    session.bulk_save_objects(missing_models, return_defaults=True)
    session.commit()
    models.extend(missing_models)
    for model in models:
        if model.name in global_role_ids and global_role_ids[model.name] != model.id:
            raise Exception("Holy moly discrepancy between constant ids")
        global_role_ids[model.name] = model.id


def setup_and_map_enum_names_to_model(session, base_model, enum_clss):
    models = session.query(base_model).all()
    existing_names = [x.name for x in models]
    missing_names = [x.__name__ for x in enum_clss if x.__name__ not in existing_names]
    missing_models = [base_model(x) for x in missing_names]
    session.bulk_save_objects(missing_models, return_defaults=True)
    session.commit()
    models.extend(missing_models)

    name_mapping = {x.name: x for x in models}

    return name_mapping


def setup_action_and_requirements_mapping(session, requirements_mapping, action_name_mapping, requirement_name_mapping):
    mapped_models = []
    for action_cls, requirements in requirements_mapping.items():
        action_name = action_cls.__name__
        action_model = action_name_mapping[action_name]
        for requirement_cls in requirements:
            requirement_name = requirement_cls.__name__
            requirement_model = requirement_name_mapping[requirement_name]
            model = ForumActionHasRequirementModel(action_model.id, requirement_model.id)
            mapped_models.append(model)
    session.bulk_save_objects(mapped_models)
    session.commit()


def setup_role_and_action_mapping(session, action_name_mapping):
    action_mapping = {
        ROLE_USER: [
            # Basic
            RegisterUser,
            Login,
            ViewUserProfile,
            ResetPassword,
            EditOwnProfileName,
            EditOwnProfileImage,
            ListForumCategories,
            GetForumCategoryMetaInformation,
            ListForumThreads,
            GetForumThreadMetaInformation,
            ListForumPosts,
            CreateForumPosts,
            UpdateOwnForumPost,
            UserLikePost,

            # Constrained
            CreateForumThread,
            RenameOwnForumThread
        ],
        ROLE_MODERATOR: [
            # Basic
            RegisterUser,
            Login,
            ViewUserProfile,
            ResetPassword,
            EditOwnProfileName,
            EditOwnProfileImage,
            ListForumCategories,
            GetForumCategoryMetaInformation,
            ListForumThreads,
            GetForumThreadMetaInformation,
            ListForumPosts,
            CreateForumPosts,
            UpdateOwnForumPost,
            UserLikePost,

            # Moderator only
            EditOthersProfileName,
            EditOthersProfileImage,
            CreateForumCategory,
            RenameForumCategory,
            DeleteForumCategory,
            RenameOthersForumThread,
            DeleteForumThread,
            UpdateOthersForumPost,
            BanUser,
            UnbanUser,

            # Constrained
            CreateForumThread,
            RenameOwnForumThread
        ],
        ROLE_ADMIN: [
            # Basic
            Login

            # TODO Missing role management feature
        ]
    }
    mapped_models = []
    for role_name, actions in action_mapping.items():
        for action_cls in actions:
            action_name = action_cls.__name__
            role_id = ROLE_IDS[role_name]
            action_model = action_name_mapping[action_name]
            model = RoleHasForumActionModel(role_id, action_model.id)
            mapped_models.append(model)
    session.bulk_save_objects(mapped_models)
    session.commit()


def init_db(db):
    # Create basic structure
    db.drop_all()
    db.create_all()
    db.session.commit()


def setup(session):
    setup_constants(session)

    requirements = [
        UserMinimumModeratorRole,
        UserMinimum10CumulativeLikesOrMinimumModeratorRole,
        UserMinimum10CumulativeLikes
    ]
    requirements_mapping = {
        RegisterUser: [],
        Login: [],
        ViewUserProfile: [],
        ResetPassword: [],
        EditOwnProfileName: [],
        EditOwnProfileImage: [],
        ListForumCategories: [],
        GetForumCategoryMetaInformation: [],
        ListForumThreads: [],
        GetForumThreadMetaInformation: [],
        ListForumPosts: [],
        CreateForumPosts: [],
        UpdateOwnForumPost: [],
        UserLikePost: [],
        EditOthersProfileName: [UserMinimumModeratorRole],
        EditOthersProfileImage: [UserMinimumModeratorRole],
        CreateForumCategory: [UserMinimumModeratorRole],
        RenameForumCategory: [UserMinimumModeratorRole],
        DeleteForumCategory: [UserMinimumModeratorRole],
        RenameOthersForumThread: [UserMinimumModeratorRole],
        DeleteForumThread: [UserMinimumModeratorRole],
        UpdateOthersForumPost: [UserMinimumModeratorRole],
        BanUser: [UserMinimumModeratorRole],
        UnbanUser: [UserMinimumModeratorRole],
        CreateForumThread: [UserMinimum10CumulativeLikesOrMinimumModeratorRole],
        RenameOwnForumThread: [UserMinimum10CumulativeLikesOrMinimumModeratorRole],
        DeleteForumPost: []  # This is internal, so should not be tagged to any role
    }
    actions = list(requirements_mapping.keys())
    requirement_name_mapping = setup_and_map_enum_names_to_model(session, ForumActionRequirementModel, requirements)
    action_name_mapping = setup_and_map_enum_names_to_model(session, ForumActionModel, actions)

    setup_action_and_requirements_mapping(session,
                                          requirements_mapping,
                                          action_name_mapping,
                                          requirement_name_mapping)

    setup_role_and_action_mapping(session, action_name_mapping)


# TODO generate password salt and hash stuff?
# TODO storage location for post after inverting save post dependency
# TODO dummy profile pic?
def setup_dummy_data(session):
    time_now = datetime.utcnow()

    # Setup dummy users
    user_a = UserModel("TheUserA", "user_a@fakeserver.com", "N.A.", "N.A.", ROLE_IDS[ROLE_USER])
    user_a.verified_user = True
    
    user_b = UserModel("TheUserB", "user_b@fakeserver.com", "N.A.", "N.A.", ROLE_IDS[ROLE_USER])
    user_b.verified_user = True

    user_banned = UserModel("BannedUserA", "banned_user@fakeserver.com", "N.A.", "N.A.", ROLE_IDS[ROLE_USER])
    user_banned.verified_user = True
    
    user_likers = []
    for i in range(5):
        user_liker = UserModel(f"TheLiker{i}", f"user_liker{i}@fakeserver.com", "N.A.", "N.A.", ROLE_IDS[ROLE_USER])
        user_liker.verified_user = True
        user_likers.append(user_liker)

    moderator_a = UserModel("TheModeratorA", "moderator_a@fakeserver.com", "N.A.", "N.A.", ROLE_IDS[ROLE_MODERATOR])
    moderator_a.verified_user = True
    
    moderator_b = UserModel("TheModeratorB", "moderator_b@fakeserver.com", "N.A.", "N.A.", ROLE_IDS[ROLE_MODERATOR])
    moderator_b.verified_user = True
    
    admin = UserModel("TheAdmin", "admin@fakeserver.com", "N.A.", "N.A.", ROLE_IDS[ROLE_ADMIN])
    admin.verified_user = True
    
    users = [user_a, user_b, user_banned, moderator_a, moderator_b, admin, *user_likers]
    session.bulk_save_objects(users, return_defaults=True)
    session.commit()

    UpdateUserModelEmailVerified("user_a@fakeserver.com").perform()
    UpdateUserModelEmailVerified("user_b@fakeserver.com").perform()
    UpdateUserModelEmailVerified("banned_user@fakeserver.com").perform()
    UpdateUserModelEmailVerified("moderator_a@fakeserver.com").perform()
    UpdateUserModelEmailVerified("moderator_b@fakeserver.com").perform()
    UpdateUserModelEmailVerified("admin@fakeserver.com").perform()
    for i in range(5):
        UpdateUserModelEmailVerified(f"user_liker{i}@fakeserver.com").perform()

    # Setup fake bans
    user_banned = session.get(UserModel, user_banned.id)
    user_banned.last_banned_by = moderator_a.id
    user_banned.banned_timestamp = time_now
    session.commit()

    # Setup dummy instances
    instances = [UserInstanceModel(user.id, "0.0.0.0", "Script") for user in users]
    session.bulk_save_objects(instances, return_defaults=True)
    session.commit()

    # Setup dummy categories
    category_a1 = ForumCategoryModel("Category A1", time_now, moderator_a.id)
    category_b1 = ForumCategoryModel("Category B1", time_now, moderator_b.id)
    categories = [category_a1, category_b1]
    session.bulk_save_objects(categories, return_defaults=True)
    session.commit()

    # Setup dummy threads
    thread_a1_a1 = ForumThreadModel("Thread A1.A1", category_a1.id, time_now, moderator_a.id)
    thread_a1_a2 = ForumThreadModel("Thread A1.A2", category_a1.id, time_now, moderator_a.id)
    thread_b1_b1 = ForumThreadModel("Thread B1.B1", category_b1.id, time_now, moderator_b.id)
    thread_b1_b2 = ForumThreadModel("Thread B1.B2", category_b1.id, time_now, moderator_b.id)
    threads = [thread_a1_a1, thread_a1_a2, thread_b1_b1, thread_b1_b2]
    session.bulk_save_objects(threads, return_defaults=True)
    session.commit()

    # Setup dummy user threads
    uthread = ForumThreadModel("UThread", category_b1.id, time_now, user_b.id)
    uthreads = [uthread]
    session.bulk_save_objects(uthreads, return_defaults=True)
    session.commit()

    # Setup dummy post
    post_a1_a1_1 = ForumPostModel("N.A1", thread_a1_a1.id, time_now, user_a.id)
    post_a1_a2_1 = ForumPostModel("N.A2", thread_a1_a2.id, time_now, user_a.id)
    post_b1_b1_1 = ForumPostModel("N.A3", thread_b1_b1.id, time_now, user_b.id)
    post_b1_b2_1 = ForumPostModel("N.A4", thread_b1_b2.id, time_now, user_b.id)
    posts = [post_a1_a1_1, post_a1_a2_1, post_b1_b1_1, post_b1_b2_1]
    session.bulk_save_objects(posts, return_defaults=True)
    session.commit()

    # Setup moderator post
    mpost = ForumPostModel("M", thread_a1_a1.id, time_now, moderator_a.id)
    mposts = [mpost]
    session.bulk_save_objects(mposts, return_defaults=True)
    session.commit()

    # Setup dummy likes
    likes = []
    for user_liker in user_likers:
        likes_1 = UserLikesForumPostModel(user_liker.id, post_b1_b1_1.id, True)
        likes_2 = UserLikesForumPostModel(user_liker.id, post_b1_b2_1.id, True)
        likes.append(likes_1)
        likes.append(likes_2)
    session.bulk_save_objects(likes, return_defaults=True)
    session.commit()

    return {
        "users": [user_a, user_b],
        "banned": [user_banned],
        "likers": [user_likers],
        "moderators": [moderator_a, moderator_b],
        "administrators": [admin],
        "categories": categories,
        "threads": threads,
        "posts": posts,
        "likes": likes,
        "instances": {instance.user_id: instance for instance in instances},
        "uthreads": uthreads,
        "mposts": mposts
    }

def setup_default_user(session):
    # admin
    time_now = datetime.now()
    admin = UserModel(environ.get("A_NAME"), environ.get("A_EMAIL"), environ.get("A_SALT"), environ.get("A_HASH"),  1)
    admin.otp = environ.get("A_OTP")
    admin.last_login_timestamp = time_now
    
    moderator = UserModel(environ.get("M_NAME"), environ.get("M_EMAIL"), environ.get("M_SALT"), environ.get("M_HASH"), 2)
    moderator.otp = environ.get("M_OTP")
    moderator.last_login_timestamp = time_now
    
    user = UserModel(environ.get("U_NAME"), environ.get("U_EMAIL"), environ.get("U_SALT"), environ.get("U_HASH"), 3)
    user.otp = environ.get("U_OTP")
    user.last_login_timestamp = time_now
    
    users = [admin, moderator, user]

    session.bulk_save_objects(users, return_defaults=True)
    session.commit()

    UpdateUserModelEmailVerified(environ.get("A_EMAIL")).perform()
    UpdateUserModelEmailVerified(environ.get("M_EMAIL")).perform()
    UpdateUserModelEmailVerified(environ.get("U_EMAIL")).perform()

   

    #category
    category = ForumCategoryModel("General", time_now, moderator.id)
    category.modified_timestamp = time_now
    category.modified_by = moderator.id
    #thread
    thread = ForumThreadModel("Post here to get your 10 like", 1,time_now, moderator.id)
    thread.modified_timestamp = time_now
    thread.modified_by = moderator.id
    session.bulk_save_objects([category, thread], return_defaults=True)
    session.commit()   