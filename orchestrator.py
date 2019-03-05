import modules.telegram
import modules.clearpass
import modules.arubaos_switch
import modules.arubaos_controller
from pprint import pprint
from pprint import pformat
import time
import pytz
from datetime import datetime, timezone
from configparser import ConfigParser
import os
import json
from validate_email import validate_email # pip3 install validate_email
import logging

# global object
cppm = None
switches = None
mobility_master = None
bot = None
logger = None

def help(argv, chat_id):
    ''' Help '''
    logger.debug('help()')

    msg = "Usage:\n\
    /date\n\
    /help\n\
    /guest\n\
    /newguest <email>\n\
    /deleteguest <guest ID>\n\
    /switchlist\n\
    /showrun <switch IP>\n\
    /showvlan <switch IP>\n\
    /showclients <switch IP>\n\
    /showap\n"
    bot.send_message(chat_id, msg)

def invalid_command(argv, chat_id):
    ''' Invalid command, print correct usage '''
    logger.debug('invalid_command()')

    error_msg = "Invalid command\nUsage:\n\
    /date\n\
    /help\n\
    /guest\n\
    /newguest <email>\n\
    /deleteguest <guest ID>\n\
    /switchlist\n\
    /showrun <switch IP>\n\
    /showvlan <switch IP>\n\
    /showclients <switch IP>\n\
    /showap\n"
    bot.send_message(chat_id, error_msg)
    #print(error_msg)

def get_timestamp(argv, chat_id):
    ''' Print current timestamp '''

    logger.debug('get_timestamp()')

    # argv[0] = "/date"
    if len(argv) != 1:
        invalid_command(argv, chat_id)
        return

    ts = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    print(ts)
    bot.send_message(chat_id, ts)

# ------------------------ CLEARPASS ------------------------

def get_guest(argv, chat_id):
    ''' Print guest user account list '''

    logger.debug('get_guest()')

    # argv[0] = "/guest"
    if len(argv) != 1:
        invalid_command(argv, chat_id)
        return

    # check ClearPass token validity
    ret = cppm.check_token_validity()
    if (ret['status'] != 0):
        msg = "Problem with ClearPass token, error: {}".format(ret['result'])
        logger.error(f'{msg}')
        bot.send_message(chat_id, msg)
        return

    # get current guest account list
    ret = cppm.get_guest_account()
    if (ret['status'] != 0): # error
        msg = "Problem while retrieving guest accounts, \
              error: {}".format(ret['result'])
        logger.error(f'{msg}')
        bot.send_message(chat_id, msg)
        return

    str = "[GUEST USERS]\n"
    for data in ret['result']['_embedded']['items']:
        expire = datetime.fromtimestamp(
            data['expire_time'],
            pytz.timezone("Europe/Rome")
        ).strftime('%Y-%m-%d %H:%M:%S')

        str += "{0:10}{1}\n{2:10}{3}\n{4:10}{5}\n\n".format(
            'ID:', data['id'],
            'Email:', data['email'],
            'Expire:', expire)

    print(str)
    bot.send_message(chat_id, str)

def new_guest(argv, chat_id):
    ''' Create new guest account '''

    logger.debug('new_guest()')

    # argv[0] = "/newguest"
    # argv[1] = "<email>"
    if len(argv) != 2:
        invalid_command(argv, chat_id)
        return

    # check email syntax
    if not validate_email(argv[1]):
        msg = "Invalid email address"
        logger.debug(f'{msg}')
        bot.send_message(chat_id,msg)
        return

    # check ClearPass token validity
    ret = cppm.check_token_validity()
    if (ret['status'] != 0):
        msg = "Problem with ClearPass token, error: {}".format(ret['result'])
        logger.error(f'{msg}')
        bot.send_message(chat_id, msg)
        return

    ret = cppm.does_guest_exist("email", argv[1])
    # check for error in does_guest_exist()
    if (ret['status'] != 0):
        msg = "Problem while checking if user exists, \
              error: {}".format(ret['status'])
        logger.error(f'{msg}')
        bot.send_message(chat_id, msg)
        return

    # if ret is not an error it should be True or False
    if ret['result']:
        str = "User {} already exists".format(argv[1])
        logger.debug(f'{str}')
        bot.send_message(chat_id, str)
        return

    ret = cppm.post_guest_account(argv[1])
    # check for error in post_guest_account()
    if (ret['status'] != 0):
        msg = "Problem while creating new account, \
              error {}".format(ret['status'])
        logger.error(f'{msg}')
        bot.send_message(chat_id, msg)
        return

    str = "[NEW GUEST USERS DETAILS]\n"
    str += "{0:15}{1}\n{2:15}{3}\n{4:15}{5}\n\n".format(
        'ID:', ret['result'][0]['id'],
        'Email:', ret['result'][0]['email'],
        'Password:', ret['result'][1])

    print(str)
    logger.debug('New guest account created')
    bot.send_message(chat_id, str)

def delete_guest(argv, chat_id):
    ''' Delete guest account '''

    logger.debug('delete_guest()')

    # argv[0] = "/deleteguest"
    # argv[1] = "<guest id>"
    if len(argv) != 2:
        invalid_command(argv, chat_id)
        return

    # check if the user type is a int value
    if (not argv[1].isdigit()):
        bot.send_message(chat_id, "You must specify an integer value")
        logger.debug('The guest id is not an integer')
        return

    # check ClearPass token validity
    ret = cppm.check_token_validity()
    if (ret['status'] != 0):
        msg = "Problem with ClearPass token, error: {}".format(ret['result'])
        logger.error(f'{msg}')
        bot.send_message(chat_id, msg)
        return

    ret = cppm.does_guest_exist("id", argv[1])
    # check for error in does_guest_exist()
    if (ret['status'] != 0):
        msg = "Problem while checking if user exists, \
              error: {}".format(ret['status'])
        logger.error(f'{msg}')
        bot.send_message(chat_id, msg)
        return

    # if ret is not an error it should be True or False
    if not ret['result']:
        str = "User {} don't exists".format(argv[1])
        bot.send_message(chat_id, str)
        return

    # delete the user
    ret = cppm.delete_guest_account(argv[1])
    if ret['status'] == 0: # 204 means user deleted
        str = "User {} deleted".format(argv[1])
        logger.debug(f'{str}')
    else:
        str = "Problem while deleting user, error: {}".format(ret['result'])
        logger.error(f'{str}')

    print(str)
    bot.send_message(chat_id, str)

# ------------------------ AOS SWITCH ------------------------

def switch_list(argv, chat_id):
    ''' Print the AOS switch list '''

    logger.debug('switch_list()')

    # argv[0] = "/switchlist"
    if len(argv) != 1:
        invalid_command(argv, chat_id)
        return

    str = "[CONTROLLED SWITCHES]\n"
    for s in switches:
        str += "IP: " + s['ip'] + "\n"

    print(str)
    bot.send_message(chat_id, str)

def show_running_config(argv, chat_id):
    ''' Print the result of show running config '''

    logger.debug('show_running_config()')

    # argv[0] = "/showrun"
    # argv[1] = "<ip address>"
    if len(argv) != 2:
        invalid_command(argv, chat_id)
        return

    aos = None
    for s in switches:
        if s['ip'] == argv[1]:
            aos = s
            break

    # checks if the IP belongs to switch list
    if (aos == None):
        logger.debug('Invalid IP address')
        bot.send_message(chat_id, "Invalid IP address")
        return

    # switch login
    ret = aos['obj'].login()
    if (ret['status'] != 0): # 0 means login ok
        msg = "Problem while login to switch, error: {}".format(ret['result'])
        logger.error(f'{msg}')
        bot.send_message(chat_id, msg)
        return

    # show running config
    ret = aos['obj'].show_running_config() # return <int> if there were error
    # switch logout
    aos['obj'].logout()
    if (ret['status'] != 0):
        msg = "Problem while retriving running config, \
              error: {}".format(ret['result'])
        logger.error(f'{msg}')
        bot.send_message(chat_id, msg)
        return

    # print running config
    print(ret['result'])
    bot.send_message(chat_id, ret['result'])

def show_vlan(argv, chat_id):
    ''' Print the result of show vlan '''

    logger.debug('show_vlan()')

    # argv[0] = "/showrun"
    # argv[1] = "<ip address>"
    if len(argv) != 2:
        invalid_command(argv, chat_id)
        return

    aos = None
    for s in switches:
        if s['ip'] == argv[1]:
            aos = s
            break

    # checks if the IP belongs to switch list
    if (aos == None):
        logger.debug('Invalid IP address')
        bot.send_message(chat_id, "Invalid IP address")
        return

    # switch login
    ret = aos['obj'].login()
    if (ret['status'] != 0): # 0 means login ok
        msg = "Problem while login to switch, error: {}".format(ret['result'])
        logger.error(f'{msg}')
        bot.send_message(chat_id, msg)
        return

    # show running config
    ret = aos['obj'].show_vlans() # return <int> if there were error
    # switch logout
    aos['obj'].logout()
    if (ret['status'] != 0):
        msg = "Problem while retriving vlan database, \
              error: {}".format(ret['result'])
        logger.error(f'{msg}')
        bot.send_message(chat_id, msg)
        return

    # print running config
    print(ret['result'])
    bot.send_message(chat_id, ret['result'])

def show_clients(argv, chat_id):
    ''' Print the result of show client '''

    logger.debug('show_vlan()')

    # argv[0] = "/showrun"
    # argv[1] = "<ip address>"
    if len(argv) != 2:
        invalid_command(argv, chat_id)
        return

    aos = None
    for s in switches:
        if s['ip'] == argv[1]:
            aos = s
            break

    # checks if the IP belongs to switch list
    if (aos == None):
        logger.debug('Invalid IP address')
        bot.send_message(chat_id, "Invalid IP address")
        return

    # switch login
    ret = aos['obj'].login()
    if (ret['status'] != 0): # 0 means login ok
        msg = "Problem while login to switch, error: {}".format(ret['result'])
        logger.error(f'{msg}')
        bot.send_message(chat_id, msg)
        return

    # show running config
    ret = aos['obj'].show_port_access() # return <int> if there were error
    # switch logout
    aos['obj'].logout()
    if (ret['status'] != 0):
        msg = "Problem while retriving vlan database, \
              error: {}".format(ret['result'])
        logger.error(f'{msg}')
        bot.send_message(chat_id, msg)
        return

    # print running config
    print(ret['result'])
    bot.send_message(chat_id, ret['result'])

# ------------------------ AOS MOBILITY MASTER ------------------------

def show_ap(text, chat_id):
    ''' Print the access point database '''

    logger.debug('show_ap')

    # argv[0] = "/showap"
    if len(text) != 1:
        invalid_command(text, chat_id)
        return

    # mobility master login
    ret = mobility_master.login()
    if (ret['status'] != 0): # 0 means login ok
        msg = "Problem while login to mobility master, \
              error: {}".format(ret['result'])
        logger.error(msg)
        bot.send_message(chat_id, msg)
        return

    ret = mobility_master.ap_database()

    # mobility master logout
    mobility_master.logout()

    if (ret['status'] != 0):
        msg = "Problem while retreiving AP database, \
              error {}".format(ret['result'])
        print(msg)
        logger.error(msg)
        bot.send_message(chat_id, msg)
        return

    str = "[AP Database]\n"
    for ap in ret['result']['AP Database']:
        str += "AP Type: {}\nGroup: {}\nIP Address: {}\nName: {}\n\n".format(
            ap['AP Type'], ap['Group'], ap['IP Address'], ap['Name'])

    print(str)
    bot.send_message(chat_id, str)

# ------------------------ HANDLER ------------------------

def functions_handler(argument, chat_id):

    switcher = {
        "/date": get_timestamp,
        "/help": help,
        "/guest": get_guest,
        "/newguest": new_guest,
        "/deleteguest": delete_guest,
        "/switchlist": switch_list,
	    "/showrun": show_running_config,
        "/showvlan": show_vlan,
        "/showclients": show_clients,
        "/showap": show_ap,
    }
    # Get the function from switcher dictionary
    func = switcher.get(argument[0], invalid_command)

    # Execute the function
    func(argument, chat_id)

def main():
    path = os.path.dirname(os.path.abspath(__file__))
    # Create a custom logger
    global logger
    logger = logging.getLogger(__name__)

    # Create handlers
    logfile = "{}/logfile.log".format(path)
    f_handler = logging.FileHandler(logfile, mode = 'a')
    f_handler.setLevel(logging.DEBUG)

    # Create formatters and add it to handlers
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    datefmt = '%Y-%m-%d %H:%M:%S'
    f_format = logging.Formatter(format, datefmt = datefmt)
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    logger.setLevel(logging.DEBUG)
    logger.addHandler(f_handler)
    logger.debug('Start orchestrator.py')

    # Configuration file parameters
    file = path + '/config/params.cfg'
    config = ConfigParser()
    config.read(file)

    # create mobility master objects
    global mobility_master
    mobility_master = modules.arubaos_controller.ArubaOS_Controller(
        config.get('MobilityMaster', 'mm_fqdn'),
        config.get('MobilityMaster', 'username'),
        config.get('MobilityMaster', 'password')
    )

    # create switch objects
    global switches
    switches = json.loads(config.get("Switches","switches"))
    for s in switches:
        s['obj'] = modules.arubaos_switch.ArubaOS_Switch(
            s['ip'], s['username'], s['password']
        )
    # at this point switches is a list of object type ArubaOS

    # create ClearPass object
    global cppm
    cppm = modules.clearpass.ClearPass(
            config.get('ClearPass', 'clearpass_fqdn'),
            config.get('OAuth2', 'grant_type'),
            config.get('OAuth2', 'client_id'),
            config.get('OAuth2', 'client_secret'),
            config.get('OAuth2', 'username'),
            config.get('OAuth2', 'password')
    )
    ret = cppm.get_access_token()
    if (ret['status'] != 0):
        msg = "Error in creating ClearPass access \
              token: {}".format(ret['result'])
        logger.error(f'{msg}')
        print(msg)
        exit(1)

    # create Telegram bot object
    global bot
    bot = modules.telegram.Telegram(
            config.get("Telegram","token"),
            json.loads(config.get("Telegram","whitelist"))
    )

    update_id = None
    try:
        while True:
            print("{} - Waiting for updates".format(
                    datetime.fromtimestamp(
                    time.time()).strftime('%Y-%m-%d %H:%M:%S')))

            # get updates from Telegram
            updates = bot.get_updates(update_id)

            # in case of error continue
            if (updates['status'] != 0):
                msg = "Problem in retriving updates from\
                 Telegram, error: {}".format(updates['result'])
                logger.error(f'{updates}')
                print(updates)
                continue

            for update in updates['result']:
                update_id = update['update_id'] + 1

                # save telegram update to file
                with open (path + "/telegram_updates.json", "a") as f:
                    f.write(pformat(update) + "\n\n")
                #pprint(update)

                if 'message' not in update.keys():
                    msg = "Update does not contain 'message', continue"
                    logger.debug(f'{msg}')
                    print(msg)
                    continue

                chat_id = update['message']['chat']['id']
                sender_id = update['message']['from']['id']

                if 'forward_from' in update['message'].keys():
                    msg = "Forwarded message, continue"
                    logger.debug(f'{msg}')
                    print(msg)
                    bot.send_message(chat_id,
                        "This Bot don't accept forwarded message")
                    continue
                if 'text' not in update['message'].keys():
                    msg = "Update['message'] does not contain 'text', continue"
                    logger.debug(f'{msg}')
                    print(msg)
                    continue

                text = update['message']['text'].split(sep=' ')

                if bot.is_whitelisted(sender_id):
                    msg = "Handling request: {} from ID: {}".format(
                        update['message']['text'],
                        chat_id
                    )
                    logger.debug(f'{msg}')
                    print(msg)
                    functions_handler(text, chat_id)
                else:
                    msg = "Unauthorized request"
                    logger.debug(f'{msg}')
                    print(msg)
                    bot.send_message(chat_id,
                        "You are not allowed to use this Bot")

    except KeyboardInterrupt:
        logger.debug('Application closed by user')
        print('\nBye!')

if __name__ == '__main__':
    main()
