## ask question happy path
* greet
  - utter_greet
* ask_stats{"question_type":"columns", "dataset": "titanic"}
  - action_answer
  - slot{"dataset":"titanic"}
* thanks
  - utter_goodbye

## ask question + dataset
* greet
  - utter_greet
* ask_stats{"question_type":"columns"}
  - utter_ask_dataset
* inform{"dataset": "titanic"}
  - action_answer
  - slot{"dataset":"titanic"}
* thanks
  - utter_goodbye

## happy path
* greet
  - utter_greet
* mood_great
  - utter_happy

## sad path 1
* greet
  - utter_greet
* mood_unhappy
  - utter_cheer_up
  - utter_did_that_help
* affirm
  - utter_happy

## sad path 2
* greet
  - utter_greet
* mood_unhappy
  - utter_cheer_up
  - utter_did_that_help
* deny
  - utter_goodbye

## say goodbye
* goodbye
  - utter_goodbye

## bot challenge
* bot_challenge
  - utter_iamabot
