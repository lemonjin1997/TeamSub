Feature: Register
    In order to use this application
    As a normal user
    I want to be able to create an account for this application

    Background: Assume that only some user account exists
        Given the following dummy forum setup


    Scenario Outline: Successful registration
        Given I navigate to register page
        And I enter <name>, <email> and <password>
        When I click on submit button
        Then the registration is successful

    Examples: Valid Accounts
        | name  | email         | password  |
        | gal   | gal@gal.com   | gagal     |


    Scenario Outline: Fail registration due to name taken
        Given I navigate to register page
        And I enter <name>, <email> and <password>
        When I click on submit button
        Then I receive name taken error message

    Examples: Accounts with duplicated name
        | name  | email         | password  |
        | dude  | gal@gal.com   | gagal     |


    Scenario Outline: Fail registration due to email taken
        Given I navigate to register page
        And I enter <name>, <email> and <password>
        When I click on submit button
        Then I receive email taken error message

    Examples: Accounts with duplicated email
        | name  | email         | password  |
        | gal   | dude@dude.com | gagal     |


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


