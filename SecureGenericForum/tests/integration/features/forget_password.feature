Feature: Forget Password
    In order to retrieve and reset account password
    As a normal user
    I want to use forget password service to reset password

    Background: Assume that only some user account exists
        Given the following dummy forum setup


    Scenario Outline: Successful reset password

    Examples: Valid Information
    | info |
    | test |


    Scenario Outline: Fail reset password due to invalid information

    Examples: Invalid Information
    | info |
    | test |