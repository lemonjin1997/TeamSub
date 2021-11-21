Feature: Category
    In order to contribute content
    As a user
    I want to be able to manage posts

    Background: Assume that only some post exists
        Given the following dummy forum setup


    Scenario Outline: Successfully create post

    Examples: Post Information
    | info |
    | test |


    Scenario Outline: Fail to create post due to name taken

    Examples: Post Information
    | info |
    | test |


    Scenario Outline: Fail to create post due to insufficient permission

    Examples: Post Information
    | info |
    | test |


    Scenario Outline: Successfully edit post as a user

    Examples: Post Information
    | info |
    | test |


    Scenario Outline: Successfully edit other post as a moderator

    Examples: Post Information
    | info |
    | test |


    Scenario Outline: Successfully view edit information of a post

    Examples: Post Information with edit information?
    | info |
    | test |