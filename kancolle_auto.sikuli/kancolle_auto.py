import datetime, os, sys, random, ConfigParser
sys.path.append(os.getcwd())
import expedition as expedition_module
import combat as combat_module
from util import (sleep, get_rand, check_and_click, wait_and_click, check_timer,
    log_msg, log_success, log_warning, log_error)

# Sikuli settings
Settings.OcrTextRead = True
Settings.MinSimilarity = 0.8

# Declare globals
WAITLONG = 60
settings = {
    'expedition_id_fleet_map': {}
}
expedition_list = None
running_expedition_list = []
fleet_returned = [False, False, False, False]
combat_item = None
kc_window = None
next_action = ''
idle = False

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
    loop_count = 0
    while not kc_window.exists(Pattern('home_main.png').exact()) and loop_count < 10:
        myApp = App.focus(settings['program'])
        kc_window = myApp.focusedWindow()
        loop_count += 1
    if loop_count == 10:
        log_error("Could not find Kancolle homepage after 10 attempts. Exiting script.")
        exit()
    sleep(2)

# Switch to KanColle app, navigate to Home screen, and receive+resupply any
# returning expeditions
def go_home():
    global kc_window
    random_menu = ['supply_main.png', 'repair_main.png', 'sortie.png',
        'senseki_off.png', 'quests_main.png']
    # Focus on KanColle
    focus_window()
    kc_window.wait('senseki_off.png', WAITLONG)
    # Check if we're already at home screen
    if kc_window.exists('sortie.png'):
        # We are, so check for expeditions
        log_success("At Home!")
        if check_expedition():
            # If there are returning expeditions, there's no need to refresh
            # the Home screen. Go straight to resupplying fleets
            log_msg("Checking for returning expeditions!")
            resupply()
        else:
            # We're already at home, but no expedition flags found. Refresh
            # the Home page just in case we haven't been at Home for a while
            log_success("Refreshing Home!")
            # Click a random menu item
            kc_window.click(random.choice(random_menu))
            sleep(3)
            # A little bit of code reuse here...
            if not check_and_click(kc_window, 'home_side.png'):
                # If the side Home button doesn't exist, we're probably in a
                # top-menu item...
                while not kc_window.exists('sortie.png'):
                    # ... so hit the return button that exists in the top-menu item
                    # pages until we get home
                    wait_and_click(kc_window, 'top_menu_return.png', 10)
                    sleep(2)
            log_success("At Home!")
            # Check for completed expeditions. Resupply them if there are.
            if check_expedition():
                resupply()
    else:
        # We're not, so check for expeditions by getting to the Home screen
        log_msg("Going Home!")
        if not check_and_click(kc_window, 'home_side.png'):
            # If the side Home button doesn't exist, we're probably in a
            # top-menu item...
            while not kc_window.exists('sortie.png'):
                # ... so hit the return button that exists in the top-menu item
                # pages until we get home
                wait_and_click(kc_window, 'top_menu_return.png', 10)
                sleep(2)
        # Back at home
        kc_window.hover('senseki_off.png')
        kc_window.wait('sortie.png', WAITLONG)
        log_success("At Home!")
        # Check for completed expeditions. Resupply them if there are.
        if check_expedition():
            resupply()

# Check expedition arrival flag on home screen; ultimately return True if there
# was at least one expedition received.
def check_expedition():
    global kc_window, expedition_list, fleet_returned, settings
    log_msg("Are there returning expeditions to receive?")
    kc_window.hover('senseki_off.png')
    if check_and_click(kc_window, 'expedition_finish.png'):
        sleep(3)
        wait_and_click(kc_window, 'next.png', WAITLONG)
        # Identify which fleet came back
        if kc_window.exists(Pattern('returned_fleet2.png').exact()): fleet_id = 2
        elif kc_window.exists(Pattern('returned_fleet3.png').exact()): fleet_id = 3
        elif kc_window.exists(Pattern('returned_fleet4.png').exact()): fleet_id = 4
        # Make sure the returned fleet is a defined one by the user
        if settings['expeditions_enabled'] == True:
            if fleet_id in settings['expedition_id_fleet_map']:
                for expedition in running_expedition_list:
                    if expedition.id == settings['expedition_id_fleet_map'][fleet_id]:
                        # Remove the associated expedition from running_expedition_list
                        running_expedition_list.remove(expedition)
                        # If fleet has an assigned expedition, set its return status to True.
                        # Otherwise leave it False, since the user might be using it
                        fleet_returned[fleet_id - 1] = True
                log_success("Yes, fleet %s has returned!" % fleet_id)
        wait_and_click(kc_window, 'next.png')
        kc_window.wait('sortie.png', WAITLONG)
        check_expedition()
        return True
    else:
        log_msg("No, no fleets to receive!")
        return False

# Resupply all or a specific fleet
def resupply():
    global fleet_returned
    log_msg("Lets resupply fleets!")
    if (True in fleet_returned):
        kc_window.hover('senseki_off.png')
        # Check if we're already at resupply screen
        if not kc_window.exists('supply_screen.png'):
            if not check_and_click(kc_window, 'supply_main.png'):
                check_and_click(kc_window, 'supply_side.png')
            kc_window.wait('supply_screen.png', WAITLONG)
        for fleet_id, returned in enumerate(fleet_returned):
            if returned:
                # If not resupplying the first fleet, navigate to correct fleet
                if fleet_id != 0:
                    fleet_name = 'fleet_%d.png' % (fleet_id + 1)
                    sleep(1)
                    kc_window.click(fleet_name)
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
    if kc_window.exists(Pattern('supply_all.png').exact()):
        # Rework for new supply screen
        kc_window.click('supply_all.png')
        sleep(2)
    else:
        log_msg("Fleet is already resupplied!")

# Navigate to Expedition menu
def go_expedition():
    global kc_window
    log_msg("Navigating to Expedition menu!")
    kc_window.hover('senseki_off.png')
    wait_and_click(kc_window, 'sortie.png', WAITLONG)
    wait_and_click(kc_window, 'expedition.png', WAITLONG)
    kc_window.wait('expedition_screen_ready.png', WAITLONG)

# Run expedition
def run_expedition(expedition):
    global kc_window, running_expedition_list, fleet_returned, settings
    log_msg("Let's send an expedition out!")
    sleep(2)
    wait_and_click(kc_window, expedition.area_pict, 10)
    sleep(2)
    wait_and_click(kc_window, expedition.name_pict, 10)
    for fleet, exp in settings['expedition_id_fleet_map'].iteritems():
        if exp == expedition.id:
            fleet_id = fleet
    # If the expedition can't be selected, it's either running or just returned
    if not kc_window.exists('decision.png'):
        fleet_returned[fleet_id - 1] = False
        if kc_window.exists('expedition_time_complete.png'):
            # Expedition just returned
            expedition.check_later(0, -1) # set the check_later time to now
            log_warning("Expedition just returned:  %s" % expedition)
        else:
            # Expedition is already running
            expedition_timer = check_timer(kc_window, 'expedition_timer.png', 80)
            # Set expedition's end time as determined via OCR and add it to
            # running_expedition_list
            expedition.check_later(int(expedition_timer[0:2]), int(expedition_timer[3:5]))
            running_expedition_list.append(expedition)
            log_warning("Expedition is already running: %s" % expedition)
        return
    wait_and_click(kc_window, 'decision.png')
    kc_window.mouseMove(Location(kc_window.x + 100, kc_window.y + 100))
    log_msg("Trying to send out fleet %s for expedition %s" % (fleet_id, expedition.id))
    # Select fleet (no need if fleet is 2 as it's selected by default)
    if fleet_id != 2:
        fleet_name = 'fleet_%s.png' % fleet_id
        wait_and_click(kc_window, fleet_name)
    sleep(1)
    # Make sure that the fleet is ready to go
    if not kc_window.exists('fleet_busy.png'):
        log_msg("Checking expedition fleet status!")
        if (kc_window.exists('supply_alert.png') or kc_window.exists('supply_red_alert.png')):
            log_warning("Fleet %s needs resupply!" % fleet_id)
            fleet_returned[fleet_id - 1] = True
            check_and_click(kc_window, 'supply_side.png')
            resupply()
            go_expedition()
            run_expedition(expedition)
            return
        kc_window.hover('senseki_off.png')
        sleep(1)
        wait_and_click(kc_window, 'ensei_start.png')
        kc_window.wait('exp_started.png', 30)
        expedition.start()
        running_expedition_list.append(expedition)
        fleet_returned[fleet_id - 1] = False
        log_success("Expedition sent!: %s" % expedition)
        sleep(1)
    else:
        # Fleet's being used for some reason... check back later
        log_error("Fleet not available. Check back later!")
        expedition.check_later(0, 10)
        check_and_click(kc_window, 'ensei_area_01.png')

# Navigate to and conduct sorties
def sortie_action():
    global kc_window, fleet_returned, combat_item, settings
    go_home()
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
    global running_expedition_list, combat_item, next_action, settings
    next_action = combat_item.next_sortie_time if settings['combat_enabled'] == True else ''
    if settings['expeditions_enabled']:
        for expedition in running_expedition_list:
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
    global kc_window, settings
    if kc_window.exists('catbomb.png') and settings['recovery_method'] != 'None':
        if settings['recovery_method'] == 'Browser':
            # Recovery steps if using a webbrowser with no other plugins
            # Assumes that 'Ctrl + R' is a valid keyboard shortcut for refreshing
            type('r', KeyModifier.CTRL)
        elif settings['recovery_method'] == 'KC3':
            # Recovery steps if using KC3 in Chrome
            type('r', KeyModifier.CTRL)
            sleep(1)
            type(Key.SPACE) # In case Exit Confirmation is checked in KC3 Settings
            sleep(1)
            kc_window.click('recovery_kc3_startanyway.png')
        # The Game Start button is there and active, so click it to restart
        wait_and_click(kc_window, Pattern('game_start.png').exact(), WAITLONG)
    else:
        log_error("Non-catbomb script crash, or catbomb script crash w/ unsupported Viewer!")
        print e
        raise

def init():
    global kc_window, expedition_list, fleet_returned, combat_item, settings
    get_config()
    log_success("Starting kancolle_auto")
    try:
        # Go home, then run expeditions
        go_home()
        if settings['expeditions_enabled'] == True:
            # Define expedition list
            expedition_list = map(expedition_module.ensei_factory, settings['expedition_id_fleet_map'].values())
            go_expedition()
            for expedition in expedition_list:
                run_expedition(expedition)
        # Define combat item if combat is enabled
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
            for expedition in running_expedition_list:
                now_time = datetime.datetime.now()
                if now_time > expedition.end_time:
                    idle = False
                    log_msg("Checking for return of expedition %s" % expedition.id)
                    go_home()
            # If there are fleets ready to go, go start their assigned expeditions
            if True in fleet_returned:
                go_home()
                go_expedition()
                for fleet_id, fleet_status in enumerate(fleet_returned):
                    if fleet_status == True:
                        for expedition in expedition_list:
                            if expedition.id == settings['expedition_id_fleet_map'][fleet_id + 1]:
                                idle = False
                                run_expedition(expedition)
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
