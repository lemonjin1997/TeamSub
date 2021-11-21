Feature: Change Password
    In order to protect my account
    As a normal user
    I want to use change password

    Background: Assume that only some user account exists
        Given the following dummy forum setup


    Scenario Outline: Successful change password

    Examples: Valid Information
    | info |
    | test |


    Scenario Outline: Fail change password due to some invalid condition (TODO)

    Examples: Invalid Information
    | info |
    | test |