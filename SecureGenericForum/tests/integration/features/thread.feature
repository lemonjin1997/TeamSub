Feature: Category
    In order to manage content
    As a user
    I want to be able to manage threads

    Background: Assume that only some thread exists
        Given the following dummy forum setup

    Scenario Outline: Successfully create thread as a moderator

    Examples: Valid Names
    | info |
    | test |


    Scenario Outline: Successfully create thread as a user

    Examples: Valid Names
    | info |
    | test |


    Scenario Outline: Fail to create thread due to name taken

    Examples: Duplicated Names
    | info |
    | test |


    Scenario Outline: Fail to create thread due to insufficient permission

    Examples: Duplicated Names
    | info |
    | test |


    Scenario Outline: Successfully rename thread as a user

    Examples: Valid Names
    | info |
    | test |


    Scenario Outline: Successfully rename other thread as a moderator

    Examples: Valid Names
    | info |
    | test |


    Scenario Outline: Fail to rename thread due to name taken

    Examples: Duplicated Names
    | info |
    | test |


    Scenario Outline: Fail to rename thread due to insufficient permission

    Examples: Valid Names
    | info |
    | test |


    Scenario Outline: Successfully delete thread

    Examples: Valid Names
    | info |
    | test |


    Scenario Outline: Successfully delete other thread as a moderator

    Examples: Valid Names
    | info |
    | test |


    Scenario Outline: Fail to delete thread due to insufficient permission

    Examples: Valid Names
    | info |
    | test |