Feature: Category
    In order to manage content
    As a moderator
    I want to be able to manage categories

    Background: Assume that only some category exists
        Given the following dummy forum setup


    Scenario Outline: Successfully create category

    Examples: Valid Names
    | info |
    | test |


    Scenario Outline: Fail to create category due to name taken

    Examples: Duplicated Names
    | info |
    | test |


    Scenario Outline: Fail to create category due to insufficient permission

    Examples: Duplicated Names
    | info |
    | test |


    Scenario Outline: Successfully rename category

    Examples: Valid Names
    | info |
    | test |


    Scenario Outline: Fail to rename category due to name taken

    Examples: Duplicated Names
    | info |
    | test |


    Scenario Outline: Fail to rename category due to insufficient permission

    Examples: Valid Names
    | info |
    | test |


    Scenario Outline: Successfully delete category

    Examples: Valid Names
    | info |
    | test |


    Scenario Outline: Fail to delete category due to insufficient permission

    Examples: Valid Names
    | info |
    | test |