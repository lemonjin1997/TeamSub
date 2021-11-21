Feature: OTP
    In order to verify my identiy for login attempts
    As a normal user
    I want to enter OTP code to do so

    Background: Assume that only some user account exists
        Given the following dummy forum setup


    Scenario Outline: Correct OTP
        Given I have successfully login with <email> and <password>
        And I have the otp <received_code>
        And I am at the OTP page
        And I enter OTP with <submit_code>
        When I click on submit button
        Then I get redirected to home page

    Examples: Valid OTP code
        | email         | password  | received_code | submit_code   |
        | dude@dude.com | dudude    | 123123        | 123123        |


    Scenario Outline: Incorrect OTP
        Given I have successfully login with <email> and <password>
        And I have the otp <received_code>
        And I am at the OTP page
        And I enter OTP with <submit_code>
        When I click on submit button
        Then I get redirected to login page
        And I see invalid OTP code error message

    Examples: Valid OTP code
        | email         | password  | received_code | submit_code   |
        | dude@dude.com | dudude    | 123123        | 321321        |