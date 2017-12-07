*** Settings ***
Documentation    Suite description
Library  Collections
Library  keywords.py
Resource  Setup_teardown.robot
Test Setup  Main Test Setup
Test Teardown  Main Test Teardown

*** Test Cases ***
TC0001 Check balance after service addition
    log_step  === Step 1. Create connection to database ===
    ${database} =  connect_to_database  path_to_db=../testing/web/clients.db

    log_step  === Step 2. Select client with positive balance ===
    ${client_id}  select_client_with_positive_balance  ${database}  default_balance=5
    ${client_balance}  select_clients_balance  ${client_id}  ${database}

    log_step  === Step 3. Select client enabled services ===
    ${enabled_services}  get_client_services  ${client_id}

    log_step  === Step 4. Get all services ===
    ${all_services} =  get_list_of_all_services

    log_step  === Step 5. Get not enabled service for client ===
    ${not_enabled_service_id} =  get_not_enabled_service_id  ${enabled_services}  ${all_services}
    ${not_enabled_service_cost} =  get_service_cost  ${not_enabled_service_id}

    log_step  === Step 6. Enable service for client ===
    ${ex_code} =  enable_service_for_client_id  ${client_id}  ${not_enabled_service_id}
    should be equal as integers  ${ex_code}  202

    log_step  === Step 7. Wait for service is enabled ===
    wait_for_service_is_enabled  ${client_id}  ${not_enabled_service_id}  top_attempts=30  sleep_time=2
    ${enabled_services2}  get_client_services  ${client_id}

    log_step  === Step 8. Get client balance ===
    ${final_client_balance} =  select_clients_balance  ${client_id}  ${database}

    log_step  === Step 9. Check that balance is correct ===
    ${calc_final_balance} =  EVALUATE  ${client_balance}-${not_enabled_service_cost}
    compare_results  ${final_client_balance}  ${calc_final_balance}
    close database connection  ${database}