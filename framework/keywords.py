"""
Link to task: https://github.com/fedorovpv/testing
"""
import sqlite3
import random
import subprocess
from time import sleep
import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from robot.api import logger
from robot.utils.robottime import get_timestamp
from python_functions import GetServicesRequestSender, \
    EnableServiceRequestSender, CheckClientServicesRequestSender


def subprocess_send_command(cmd, exp_rc=0):
    """Function to execute linux commands using Python"""
    sub_process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    out, err = sub_process.communicate()
    act_rc = sub_process.returncode
    out1, err1 = post_send_command_actions(cmd, exp_rc, out, err, act_rc)
    return out1, err1, act_rc


class AssertionErrorWithInfo(AssertionError):
    """class for informative errors"""
    def __init__(self, message, more_info=None):
        self.more_info = more_info
        super(AssertionErrorWithInfo, self).__init__(message)


def post_send_command_actions(cmd, exp_rc, out, err, act_rc):
    """Function to handle subprocess results"""
    if exp_rc is not None and not isinstance(exp_rc, list):
        exp_rc = [int(exp_rc)]
    elif exp_rc is not None:
        exp_rc = [int(item) for item in exp_rc]

    if exp_rc is not None:
        if act_rc not in exp_rc:
            raise AssertionErrorWithInfo(
                "Error occurred  during '%s' execution: "
                "got rc='%s' but expected %s. \nError: %s" % (
                    cmd, act_rc, exp_rc, err))
    return out, err


def start_application():
    """Main setup function for test case"""
    logger_debug("Starting 'testing_web_1' application...")
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logger_debug(subprocess_send_command('pwd'))
    os.chdir("{0}/testing".format(path))
    logger_debug(subprocess_send_command('pwd'))
    logger_debug(subprocess_send_command(['ls', '-la']))
    logger_debug("Executing 'docker-compose build' command...")
    subprocess_send_command(["docker-compose", "build"])
    logger_debug("Executing 'docker-compose up -d' command...")
    subprocess_send_command(["docker-compose", "up", "-d"])
    logger_debug("Application successfully started")


def stop_application():
    """Main teardown function for test case"""
    logger_debug("Stopping 'testing_web_1' application...")
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logger_debug(subprocess_send_command('pwd'))
    os.chdir("{0}/testing".format(path))
    logger_debug(subprocess_send_command('pwd'))
    logger_debug("Executing 'docker-compose down' command...")
    subprocess_send_command(["docker-compose", "down"])
    logger_debug("Application successfully stopped")


def generate_name(length):
    """Function to generate random names"""
    vowels = ['a', 'e', 'i', 'o', 'u']
    consonants = ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm',
                  'n', 'p', 'q', 'r', 's', 't', 'v', 'x', 'y', 'z']
    if length <= 0:
        return False
    full_syl = ''
    for i in range(length):
        decision = random.choice(('consonant', 'vowel'))

        if full_syl[-1:].lower() in vowels:
            decision = 'consonant'
        if full_syl[-1:].lower() in consonants:
            decision = 'vowel'

        if decision == 'consonant':
            syl_choice = random.choice(consonants)
        else:
            syl_choice = random.choice(vowels)

        if full_syl == '':
            full_syl += syl_choice.upper()
        else:
            full_syl += syl_choice
    return full_syl


class MyError(Exception):
    """class for more informative error"""
    def __init__(self, message):
        Exception.__init__(self, message)


def prettify_message(msg, add_time=True):
    """Function for informative logging"""
    timestamp = '' if add_time is False else '%s: ' % get_timestamp(daysep='-')
    pretty_msg = '\n%s%s' % (timestamp, msg)
    return pretty_msg


def logger_debug(msg):
    """Messages logger"""
    new_msg = prettify_message(msg)
    logger.info(new_msg)
    logger.console(new_msg)


def log_step(msg):
    """Steps logger"""
    logger.console("\n")
    logger.console(msg)
    logger_debug(msg)


def connect_to_database(path_to_db):
    """Function to connect to database"""
    logger_debug("Connecting to database...")
    connection = sqlite3.connect(path_to_db).cursor()
    return connection


def close_database_connection(database):
    """Function to close connection to database"""
    logger_debug("Disconnecting from database...")
    database.close()


def select_all_data_from_clients_table(database):
    """Function to select all records from CLIENTS table"""
    logger_debug("Selecting all data from clients table...")
    database.execute("SELECT * FROM CLIENTS")
    output = database.fetchall()
    logger_debug(output)
    return output


def select_all_data_from_balance_table(database):
    """Function to select all records from BALANCES table"""
    logger_debug("Selecting all data from balance table...")
    database.execute("SELECT * FROM BALANCES")
    output = database.fetchall()
    logger_debug(output)
    return output


def select_client_with_positive_balance(database, default_balance=5):
    """Function to select any client with positive balance"""
    logger_debug("Selecting client with positive balance from database...")
    database.execute("SELECT CLIENTS_CLIENT_ID FROM BALANCES "
                     "WHERE BALANCE > 0 LIMIT 1")
    output = database.fetchone()
    if output:
        return output[0]
    else:
        create_client_with_positive_balance(database, default_balance)


def delete_client_from_all_tables(client_id, database):
    """Function to delete clients from both two tables"""
    logger_debug("Deleting client with client_id {0} "
                 "from CLIENTS and BALANCES tables...".format(client_id))
    database.execute("DELETE FROM CLIENTS WHERE "
                     "CLIENT_ID = {0}".format(client_id))
    database.execute("DELETE FROM BALANCES WHERE "
                     "CLIENTS_CLIENT_ID = {0}".format(client_id))


def select_clients_balance(client_id, database):
    """Function to get client balance"""
    logger_debug("Selecting balance for client with client_id={0}..."
                 .format(client_id))
    database.execute("SELECT BALANCE FROM BALANCES "
                     "WHERE CLIENTS_CLIENT_ID = {0}".format(client_id))
    output = database.fetchone()
    if output:
        return output[0]


def create_client_with_positive_balance(database, balance):
    """Function to create client with positive balance"""
    first_name = generate_name(random.randint(3, 10))
    last_name = generate_name(random.randint(3, 10))
    client_name = '{0} {1}'.format(first_name, last_name)
    logger_debug("New client creation with client_name "
                 "{0} and balance {1}...".format(client_name, balance))
    command = "INSERT INTO CLIENTS (CLIENT_NAME) VALUES (?)"
    database.execute(command, (client_name,))
    while True:
        logger_debug("Selecting client with client_name {0}"
                     .format(client_name))
        database.execute("SELECT CLIENT_ID FROM CLIENTS "
                         "WHERE CLIENT_NAME = ?", (client_name,))
        output = database.fetchone()
        if output:
            client_id = output[0]
            break
        else:
            sleep(1)
    logger_debug("Adding record to BALANCES table for client_id {0} "
                 "with balance {1}...".format(client_id, balance))
    command = "INSERT INTO BALANCES (CLIENTS_CLIENT_ID,BALANCE) VALUES (?,?)"
    database.execute(command, (client_id, balance))
    return client_id


def get_client_services(client_id):
    """Function to get clients enabled services"""
    output = json.loads(CheckClientServicesRequestSender
                        ({'client_id': int(client_id)}).send_message().text)
    enabled_services = list()
    if output:
        if int(output['count']) > 0:
            for service in output['items']:
                enabled_services.append(service['id'])
    return enabled_services


def get_list_of_all_services():
    """Function to get list of all services"""
    return json.loads(GetServicesRequestSender().send_message().text)['items']


def get_not_enabled_service_id(enabled_services, all_services):
    """Function to get id of not enabled service"""
    not_enabled_services = [service['id'] for service in all_services if
                            service['id'] not in enabled_services]
    if not_enabled_services:
        return random.choice(not_enabled_services)
    else:
        logger_debug("All services: {0}\nEnabled services: {1}"
                     .format(all_services, enabled_services))
        raise MyError("All services are enabled for this client")


def get_service_cost(service_id):
    """Function to get cost of service"""
    all_services = get_list_of_all_services()
    for service in all_services:
        if service['id'] == service_id:
            return service['cost']


def enable_service_for_client_id(client_id, service_id):
    """Function to set service enabled for specified client"""
    return EnableServiceRequestSender(
        {'client_id': client_id, 'service_id': service_id})\
        .send_message().status_code


def check_service_is_enabled(client_id, service_id):
    """Function to check if service is enabled"""
    logger_debug("Checking service {0} in client {1} enabled services"
                 .format(service_id, client_id))
    client_services = get_client_services(client_id)
    return check_service_is_in_client_services(service_id, client_services)


def check_service_is_in_client_services(service_id, client_services):
    """Function to check if service in client enabled services list"""
    logger_debug("Checking service {0} in client enabled services {1}"
                 .format(service_id, client_services))
    if service_id not in client_services:
        logger_debug("Service {0} is not enabled for this client"
                     .format(service_id))
        return False
    return True


def wait_for_service_is_enabled(client_id, service_id,
                                top_attempts=20, sleep_time=3):
    """Function to wait until service is enabled for specified client"""
    logger_debug("Start waiting for service {0} is enabled for client {1}"
                 .format(service_id, client_id))
    for i in range(int(top_attempts)):
        logger_debug("{0} attempts left".format((int(top_attempts) - i)))
        result = check_service_is_enabled(client_id, service_id)
        if result:
            logger_debug("Service {0} is enabled for client {1}"
                         .format(service_id, client_id))
            break
        else:
            if i != int(top_attempts) - 1:
                logger_debug('Waiting %s seconds...' % sleep_time)
                sleep(int(sleep_time))
            else:
                logger_debug(
                    'No attempts left while waiting keyword to be '
                    'finished successfully')


def compare_results(actual_result, expected_result):
    """Function to compare actual result with expected result"""
    logger_debug("Compare actual result {0} with calculated result {1}"
                 .format(actual_result, expected_result))
    logger_debug("{0} and {1} should be equal"
                 .format(actual_result, expected_result))
    if float(actual_result) != float(expected_result):
        raise MyError("{0} != {1}, but should"
                      .format(actual_result, expected_result))
    else:
        logger_debug("{0} == {1}"
                     .format(actual_result, expected_result))


# def email_results(sender_email, recipients_email, path_to_log, result):
#     path_to_log = path_to_log.encode("cp1252")
#     msg = MIMEMultipart('alternative')
#     msg['Subject'] = "{0} database test results".format(result)
#     msg['From'] = sender_email
#     msg['To'] = recipients_email.encode("cp1252")
#
#     text = "Hello colleagues!\nHere are the results of database testing\n"
#     html = """\
#     <html>
#       <head></head>
#       <body>
#         <p>Robot log file is attached to this e-mail<br>
#         </p>
#       </body>
#     </html>
#     """
#     part1 = MIMEText(text, 'plain')
#     part2 = MIMEText(html, 'html')
#     msg.attach(part1)
#     msg.attach(part2)
#     part = MIMEApplication(open(str(path_to_log), "rb").read())
#     part.add_header('Content-Disposition', 'attachment',
#                     filename=str(path_to_log))
#     msg.attach(part)
#     s = smtplib.SMTP("smtp.gmail.com:587")
#     s.starttls()
#     s.login("e-mail", "password")
#     logger_debug('Sending e-mail to {0}'.format(recipients_email))
#     s.sendmail(sender_email, recipients_email, msg.as_string())
#     s.quit()


