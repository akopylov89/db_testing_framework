*** Settings ***
Documentation    Suite description
Library  keywords.py

*** Keywords ***
Main Test Setup
    start_application

Main Test Teardown
    stop application