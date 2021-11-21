Feature: Profile
    In order to personalize my account
    As a normal user
    I want to have name and profile picture

    Background: Assume that only some user account exists (TODO add more setup info)
        Given the following dummy forum setup



    Scenario Outline: Rename successful

    Examples: New names
    | name  |
    | gal   |


    Scenario Outline: Rename failure due to name taken

    Examples: Duplicated Name
    | name  |
    | dude  |


    Scenario Outline: Change profile picture successful

    Examples: Valid profile picture?
    | info |
    | test |


    Scenario Outline: Change profile picture failure

    Examples: Invalid profile picture?
    | info |
    | test |