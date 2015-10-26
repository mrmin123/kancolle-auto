import datetime, os, sys, random, ConfigParser
sys.path.append(os.getcwd())
import expedition as expedition_module
import combat as combat_module
from util import (get_util_config, sleep, rclick, check_and_click, wait_and_click, rnavigation,
    check_timer, log_msg, log_success, log_warning, log_error)

# Sikuli settings
Settings.OcrTextRead = True
Settings.MinSimilarity = 0.8

# Declare globals
WAITLONG = 60
settings = {
    'expedition_id_fleet_map': {}
}
fleet_returned = [False, False, False, False]
expedition_item = None
combat_item = None
kc_window = None
next_action = ''
idle = False
last_refresh = ''

# Focus on the defined KanColle app
def focus_window():
    global kc_window, settings
    log_msg("Focus on KanColle!")
    myApp = App.focus(settings['program'])
    kc_window = myApp.focusedWindow()
    # Wake screen up in case machine has been idle
    # Would cause issues when (0,0) to (1,1) - windows focus issue??
    kc_window.mouseMove(Location(kc_window.x + 100, kc_window.y + 100))
    kc_window.mouseMove(Location(kc_window.x + 120,kc_window.y + 120))
    # Attempt to focus on window 10x until the Home (or catbomb) is found
    loop_count = 0
    while not (kc_window.exists(Pattern('menu_main_home.png').exact())
        or kc_window.exists('catbomb.png')) and loop_count < 10:
        myApp = App.focus(settings['program'])
        kc_window = myApp.focusedWindow()
        loop_count += 1
    # Check for catbomb
    if kc_window.exists('catbomb.png'):
        raise FindFailed('Catbombed :(')
    # Check loop count
    if loop_count == 10:
        log_error("Could not find Kancolle homepage after 10 attempts. Exiting script.")
        exit()
    sleep(2)

# Switch to KanColle app, navigate to Home screen, and receive+resupply any
# returning expeditions
def go_home(refresh=False):
    global kc_window
    # Focus on KanColle
    focus_window()
    # Check if we're already at home screen
    if kc_window.exists('menu_main_sortie.png') and check_expedition():
        # We are, so check for expeditions
        log_success("At Home!")
        # If there are returning expeditions, there's no need to refresh
        # the Home screen. Go straight to resupplying fleets
        log_msg("Checking for returning expeditions!")
        resupply()
    else:
        if refresh:
            rnavigation(kc_window, 'refresh_home')
        else:
            rnavigation(kc_window, 'home')
        log_success("At Home!")
        # Check for completed expeditions. Resupply them if there are.
        if check_expedition():
            resupply()

# Check expedition arrival flag on home screen; ultimately return True if there
# was at least one expedition received.
def check_expedition():
    global kc_window, expedition_item, fleet_returned, settings
    log_msg("Are there returning expeditions to receive?")
    if check_and_click(kc_window, 'expedition_finish.png'):
        sleep(3)
        wait_and_click(kc_window, 'next.png', WAITLONG, [-700, 30, -400, 30])
        # Identify which fleet came back
        if kc_window.exists(Pattern('returned_fleet2.png').exact()): fleet_id = 2
        elif kc_window.exists(Pattern('returned_fleet3.png').exact()): fleet_id = 3
        elif kc_window.exists(Pattern('returned_fleet4.png').exact()): fleet_id = 4
        log_success("Yes, fleet %s has returned!" % fleet_id)
        fleet_returned[fleet_id - 1] = True
        # Check if the returned fleet is one defined by the user
        if settings['expeditions_enabled'] == True and expedition_item is not None:
            if fleet_id in expedition_item.expedition_id_fleet_map:
                for expedition in expedition_item.running_expedition_list:
                    if fleet_id == expedition.fleet_id:
                        # Remove the associated expedition from running_expedition_list
                        expedition_item.running_expedition_list.remove(expedition)
        wait_and_click(kc_window, 'next.png', WAITLONG, [-700, 30, -400, 30])
        kc_window.wait('menu_main_sortie.png', WAITLONG)
        check_expedition()
        return True
    else:
        log_msg("No, no fleets to receive!")
        return False

# Resupply all or a specific fleet
def resupply():
    global fleet_returned
    log_msg("Lets resupply fleets!")
    if True in fleet_returned:
        # Check if we're already at resupply screen
        if not kc_window.exists('resupply_screen.png'):
            rnavigation(kc_window, 'resupply')
            kc_window.wait('resupply_screen.png', WAITLONG)
        for fleet_id, returned in enumerate(fleet_returned):
            if returned:
                # If not resupplying the first fleet, navigate to correct fleet
                if fleet_id != 0:
                    fleet_name = 'fleet_%d.png' % (fleet_id + 1)
                    sleep(1)
                    rclick(kc_window, fleet_name)
                    sleep(1)
                resupply_action()
        log_success("Done resupplying!")
    else:
        log_msg("No fleets need resupplying!")
    # Always go back home after resupplying
    go_home()

# Actions involved in resupplying a fleet
def resupply_action():
    global kc_window
    if kc_window.exists(Pattern('resupply_all.png').exact()):
        # Rework for new resupply screen
        rclick(kc_window, 'resupply_all.png')
        sleep(2)
    else:
        log_msg("Fleet is already resupplied!")

# Navigate to and send expeditions
def expedition_action(fleet_id):
    global kc_window, fleet_returned, expedition_item, settings
    for expedition in expedition_item.expedition_list:
        if fleet_id == 'all':
            pass
        else:
            if fleet_id != expedition.fleet_id:
                continue
        while expedition_item.run_expedition(expedition):
            fleet_returned[expedition.fleet_id - 1] = True
            check_and_click(kc_window, 'menu_side_resupply.png')
            resupply()
            expedition_item.go_expedition()
        fleet_returned[expedition.fleet_id - 1] = False

# Navigate to and conduct sorties
def sortie_action():
    global kc_window, fleet_returned, combat_item, settings
    go_home(True)
    combat_item.go_sortie()
    fleet_returned[0] = True
    # Check home, repair if needed, and resupply
    go_home()
    if combat_item.count_damage_above_limit('repair') > 0:
        combat_item.go_repair()
    resupply()
    fleet_returned[0] = False
    log_success("Next sortie!: %s" % combat_item)

# Determine when the next automated action will be, whether it's a sortie or
# expedition action
def check_soonest():
    global expedition_item, combat_item, next_action, settings
    next_action = combat_item.next_sortie_time if settings['combat_enabled'] == True else ''
    if settings['expeditions_enabled']:
        for expedition in expedition_item.running_expedition_list:
            if next_action == '':
                next_action = expedition.end_time
            else:
                if expedition.end_time < next_action:
                    next_action = expedition.end_time

# Load the config.ini file
def get_config():
    global settings
    log_msg("Reading config file")
    # Change paths and read config.ini
    os.chdir(getBundlePath())
    os.chdir('..')
    config = ConfigParser.ConfigParser()
    config.read('config.ini')
    # Set user settings
    # 'General' section
    settings['program'] = config.get('General', 'Program')
    settings['recovery_method'] = config.get('General', 'RecoveryMethod')
    # 'Expeditions' section
    if config.getboolean('Expeditions', 'Enabled'):
        settings['expeditions_enabled'] = True
        if config.get('Expeditions', 'Fleet2'):
            settings['expedition_id_fleet_map'][2] = config.getint('Expeditions', 'Fleet2')
        if config.get('Expeditions', 'Fleet3'):
            settings['expedition_id_fleet_map'][3] = config.getint('Expeditions', 'Fleet3')
        if config.get('Expeditions', 'Fleet4'):
            settings['expedition_id_fleet_map'][4] = config.getint('Expeditions', 'Fleet4')
        log_success("Expeditions enabled!")
    else:
        settings['expeditions_enabled'] = False
    # 'Combat' section
    if config.getboolean('Combat', 'Enabled'):
        settings['combat_enabled'] = True
        settings['combat_area'] = config.getint('Combat', 'Area')
        settings['combat_subarea'] = config.getint('Combat', 'Subarea')
        settings['nodes'] = config.getint('Combat', 'Nodes')
        settings['formations'] = config.get('Combat', 'Formations').replace(' ', '').split(',')
        if len(settings['formations']) < settings['nodes']:
            settings['formations'].extend(['line_ahead'] * (settings['nodes'] - len(settings['formations'])))
        settings['night_battles'] = config.get('Combat', 'NightBattles').replace(' ', '').split(',')
        if len(settings['night_battles']) < settings['nodes']:
            settings['night_battles'].extend(['True'] * (settings['nodes'] - len(settings['night_battles'])))
        settings['retreat_limit'] = config.getint('Combat', 'RetreatLimit')
        settings['repair_limit'] = config.getint('Combat', 'RepairLimit')
        settings['repair_time_limit'] = config.getint('Combat', 'RepairTimeLimit')
        settings['check_fatigue'] = config.getboolean('Combat', 'CheckFatigue')
        settings['port_check'] = config.getboolean('Combat', 'PortCheck')
        log_success("Combat enabled!")
    else:
        settings['combat_enabled'] = False
    log_success("Config loaded!")

# Refresh kancolle. Only supports catbomb situations and browers at the moment
def refresh_kancolle(e):
    global kc_window, last_refresh, settings
    if kc_window.exists('catbomb.png') and settings['recovery_method'] != 'None':
        if last_refresh != '':
            if last_refresh + datetime.timedelta(minutes=20) > datetime.datetime.now():
                log_error("Last catbomb and refresh was a very short time ago! Exiting script to not spam!")
                print e
                raise
        if settings['recovery_method'] == 'Browser':
            # Recovery steps if using a webbrowser with no other plugins
            # Assumes that 'F5' is a valid keyboard shortcut for refreshing
            type(Key.F5)
        elif settings['recovery_method'] == 'KC3':
            # Recovery steps if using KC3 in Chrome
            type(Key.F5)
            sleep(1)
            type(Key.SPACE) # In case Exit Confirmation is checked in KC3 Settings
            sleep(1)
            kc_window.click('recovery_kc3_startanyway.png')
        elif settings['recovery_method'] == 'KCV':
            # Recovery steps if using KanColleViewer
            type(Key.F5)
        elif settings['recovery_method'] == 'KCT':
            # Recovery steps if using KanColleTool; refreshes via 'Get API Link' option
            type(Key.ALT)
            sleep(1)
            type(Key.DOWN)
            sleep(1)
            type(Key.DOWN)
            sleep(1)
            type(Key.ENTER)
        elif settings['recovery_method'] == 'EO':
            # Recovery steps if using Electronic Observer
            type(Key.F5)
            sleep(1)
            type(Key.TAB) # In case Exit Confirmation is checked in EO Settings
            sleep(1)
            type(Key.SPACE)
        # The Game Start button is there and active, so click it to restart
        wait_and_click(kc_window, Pattern('game_start.png').exact(), WAITLONG)
        last_refresh = datetime.datetime.now()
    else:
        log_error("Non-catbomb script crash, or catbomb script crash w/ unsupported Viewer!")
        print e
        raise

def init():
    global kc_window, fleet_returned, expedition_item, combat_item, settings
    get_config()
    get_util_config()
    log_success("Starting kancolle_auto")
    try:
        # Go home
        go_home(True)
        # Define expedition list if expeditions module is enabled
        if settings['expeditions_enabled'] == True:
            expedition_item = expedition_module.Expedition(kc_window, settings)
            # Run expeditions defined in expedition item
            expedition_item.go_expedition()
            expedition_action('all')
        # Define combat item if combat module is enabled
        if settings['combat_enabled'] == True:
            combat_item = combat_module.Combat(kc_window, settings)
            # Run sortie defined in combat item
            sortie_action()
    except FindFailed, e:
        refresh_kancolle(e)

# initialize kancolle_auto
init()
log_msg("Initial checks and commands complete. Starting loop.")
while True:
    try:
        if settings['expeditions_enabled'] == True:
            # If expedition timers are up, check for their arrival
            for expedition in expedition_item.running_expedition_list:
                now_time = datetime.datetime.now()
                if now_time > expedition.end_time:
                    idle = False
                    log_msg("Checking for return of expedition %s" % expedition.id)
                    go_home(True)
            # If there are fleets ready to go, go start their assigned expeditions
            if True in fleet_returned:
                go_home()
                expedition_item.go_expedition()
                for fleet_id, fleet_status in enumerate(fleet_returned):
                    if fleet_status == True and fleet_id != 0:
                        expedition_action(fleet_id + 1)
        # If combat timer is up, go sortie
        if settings['combat_enabled'] == True:
            if datetime.datetime.now() > combat_item.next_sortie_time:
                idle = False
                sortie_action()
        # If fleets have been sent out and idle period is beginning, let the user
        # know when the next scripted action will occur
        if idle == False:
            check_soonest()
            log_msg("Next action at %s" % next_action.strftime("%Y-%m-%d %H:%M:%S"))
            idle = True
        sleep(20)
    except FindFailed, e:
        refresh_kancolle(e)
