Feature: Ban users
    In order to protect the community
    As a moderator
    I want to ban users

    Background Outline: Assume that only some user account exists
        Given the following dummy forum setup


    Scenario Outline: Successful ban user

    Examples: Information
    | info |
    | test |


    Scenario Outline: Fail to ban user (already banned)

    Examples: Information
    | info |
    | test |


    Scenario Outline: Successful unban user

    Examples: Information
    | info |
    | test |


    Scenario Outline: Fail to unban user (not banned)

    Examples: Information
    | info |
    | test |