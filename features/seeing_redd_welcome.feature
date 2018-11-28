Feature: User sees welcome page

  Scenario: Access main site
     Given we are browsing surprisetech.pythonanywhere.com/
       Then we should see a "Welcome!"

  Scenario: Search tifu Subreddit and hot category
     Given we are browsing surprisetech.pythonanywhere.com/
     When we type tifu in search box and select hot category
       Then we should be at page surprisetech.pythonanywhere.com/count/tifu/hot

  Scenario: Have drop down menu for subreddit or user
    Given we are browsing surprisetech.pythonanywhere.com/
      Then we should see a menu to select subreddit or user

  Scenario: Have selection of search catergory
    Given we select menu to select subreddit
      Then we should see a menu to select category

  Scenario Outline: Logo button returns to welcome page
    Given we are browsing surprisetech.pythonanywhere.com/r/tifu/<category>
      When we select logo button
      Then we should be browsing surprisetech.pythonanywere.com
     Examples: Categories
       | category          |
       | hot               |
       | topalltime        |
       | top24hrs          |
       | controversialall   |
       | controversial24hrs |

