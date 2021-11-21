Feature: Login
    In order to use this application
    As a normal user
    I want to login into this application

    Background: Assume that only some user account exists
        Given the following dummy forum setup


    Scenario Outline: Successful login
        Given I navigate to login page
        And I login with <email> and <password>
        When I click on submit button
        Then I get redirected to otp page

    Examples: Valid Login Accounts
        | email         | password  |
        | dude@dude.com | dudude    |


    Scenario Outline: Fail login due to invalid credentials
        Given I navigate to login page
        And I login with <email> and <password>
        When I click on submit button
        Then I receive login error message

    Examples: Invalid Login Accounts
        | email         | password  |
        | gal@gal.com   | gagal     |


    Scenario Outline: Fail login due to invalid password
        Given I navigate to login page
        And I login with <email> and <password>
        When I click on submit button
        Then I receive login error message

    Examples: Invalid Login Accounts
        | email         | password  |
        | dude@dude.com | gagal     |
