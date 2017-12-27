*** Settings ***
Documentation    Suite description
Library  keywords.py

*** Variables ***
${SUITE STATUS}  PASS

*** Keywords ***
Main Test Setup
    start_application

Main Test Teardown
    log to console  Starting Test case Teardown\n
    stop application
    run keyword if test failed  log to console  FAIL ${TEST NAME}\n\n
    run keyword if test passed  log to console  PASS ${TEST NAME}\n\n

#Main Teardown
#    email results  sender_email=database_testing@mail.com  recipients_email=cilicium_2@mail.ru  path_to_log=${CURDIR}/logs/log.html  result=${SUITE STATUS}