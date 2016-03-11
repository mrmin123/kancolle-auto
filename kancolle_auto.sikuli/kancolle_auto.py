import datetime, os, sys, ConfigParser
sys.path.append(os.getcwd())
import expedition as expedition_module
import combat as combat_module
import quests as quest_module
from util import *

# Sikuli settings
Settings.OcrTextRead = True
Settings.MinSimilarity = 0.8

# Declare globals
WAITLONG = 60
sleep_cycle = 20
settings = {
    'expedition_id_fleet_map': {}
}
fleet_needs_resupply = [False, False, False, False]
current_fleetcomp = 0
quest_item = None
expedition_item = None
combat_item = None
pvp_item = None
fleetcomp_switcher = None
quest_reset_skip = False
default_quest_mode = 'pvp'
kc_window = None
next_sleep_time = None
next_pvp_time = None
pvp_timer_skip = False
idle = False
last_refresh = ''

# Focus on the defined KanColle app
def focus_window():
    global kc_window, settings
    log_msg("Focus on KanColle!")
    myApp = App.focus(settings['program'])
    kc_window = myApp.focusedWindow()
    # Wake screen up in case machine has been idle
    rejigger_mouse(kc_window, 370, 770, 100, 400)
    rejigger_mouse(kc_window, 370, 770, 100, 400)
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
    # One more rejigger once the game has been found, to store game window coordinates
    rejigger_mouse(kc_window, 370, 770, 100, 400, True)
    sleep(2)

# Switch to KanColle app, navigate to Home screen, and receive+resupply any
# returning expeditions
def go_home(refresh=False):
    global kc_window
    # Focus on KanColle
    focus_window()
    # Check if we're already at home screen
    if kc_window.exists('menu_main_sortie.png'):
        log_success("At Home!")
        log_msg("Checking for returning expeditions!")
        # We are, so check for expeditions
        if check_expedition():
            # If there are returning expeditions, there's no need to refresh
            # the Home screen. Go straight to resupplying fleets
            resupply()
        elif refresh:
            # We're at home, but if we're due for a refresh, refresh
            rnavigation(kc_window, 'refresh_home')
            # Check for completed expeditions. Resupply them if there are.
            if check_expedition():
                resupply()
    else:
        rnavigation(kc_window, 'home')
        log_success("At Home!")
        # Check for completed expeditions. Resupply them if there are.
        if check_expedition():
            resupply()

# Check expedition arrival flag on home screen; ultimately return True if there
# was at least one expedition received.
def check_expedition():
    global kc_window, expedition_item, quest_item, fleet_needs_resupply, settings
    log_msg("Are there returning expeditions to receive?")
    if check_and_click(global_regions['expedition_flag'], 'expedition_finish.png', expand_areas('expedition_finish')):
        sleep(3)
        wait_and_click(global_regions['next'], 'next.png', WAITLONG, expand_areas('next'))
        log_success("Yes, an expedition has returned!")
        # Guesstimate which expedition came back
        if settings['expeditions_enabled'] == True and expedition_item is not None:
            for expedition in expedition_item.expedition_list:
                now_time = datetime.datetime.now()
                if now_time > expedition.end_time and not expedition.returned:
                    fleet_needs_resupply[expedition.fleet_id - 1] = True
                    expedition.returned = True
                    log_msg("It's probably fleet %d that returned!" % expedition.fleet_id)
                    break
        # Let the Quests module know, if it's enabled
        if settings['quests_enabled'] == True:
            quest_item.done_expeditions += 1
        while not kc_window.exists('menu_main_sortie.png'):
            check_and_click(global_regions['next'], 'next.png', expand_areas('next'))
            rejigger_mouse(kc_window, 370, 770, 100, 400)
            sleep(2)
        check_expedition()
        return True
    else:
        log_msg("No, no fleets to receive!")
        return False

# Resupply all or a specific fleet
def resupply():
    global fleet_needs_resupply
    log_msg("Lets resupply fleets!")
    if True in fleet_needs_resupply:
        # Check if we're already at resupply screen
        if not kc_window.exists('resupply_screen.png'):
            rnavigation(kc_window, 'resupply')
        for fleet_id, returned in enumerate(fleet_needs_resupply):
            if returned:
                # If not resupplying the first fleet, navigate to correct fleet
                if fleet_id != 0:
                    fleet_name = 'fleet_%d.png' % (fleet_id + 1)
                    sleep(1)
                    global_regions['fleet_flags_main'].click(pattern_generator(global_regions['fleet_flags_main'], fleet_name))
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
    if global_regions['fleet_flags_main'].exists(pattern_generator(global_regions['fleet_flags_main'], Pattern('resupply_all.png').exact())):
        # Rework for new resupply screen
        global_regions['fleet_flags_main'].click(global_regions['fleet_flags_main'].getLastMatch())
        sleep(2)
    else:
        log_msg("Fleet is already resupplied!")

# Actions involved in checking quests
def quest_action(mode, first_run=False):
    global kc_window, quest_item
    go_home()
    quest_item.go_quests(mode, first_run)
    quest_item.schedule_loop = 0 # Always reset schedule loop after running through quests

# Identify which expeditions need to be sent to expedition_action. Used for
# sending out singular expeditions
def expedition_action_wrapper():
    global expedition_item
    for expedition in expedition_item.expedition_list:
        if expedition.returned:
            expedition_action(expedition.fleet_id)

# Navigate to and send expeditions
def expedition_action(fleet_id):
    global kc_window, fleet_needs_resupply, expedition_item, settings
    go_home()
    expedition_item.go_expedition()
    for expedition in expedition_item.expedition_list:
        if fleet_id == 'all':
            pass
        else:
            if fleet_id != expedition.fleet_id:
                continue
        while expedition_item.run_expedition(expedition):
            fleet_needs_resupply[expedition.fleet_id - 1] = True
            check_and_click(kc_window, 'menu_side_resupply.png')
            resupply()
            expedition_item.go_expedition()
        fleet_needs_resupply[expedition.fleet_id - 1] = False

# Actions involved in conducting PvPs
def pvp_action():
    global kc_window, pvp_item, settings
    # Switch fleet comp, if necessary
    fleetcomp_switch_action(settings['pvp_fleetcomp'])
    if settings['quests_enabled']:
        quest_action('pvp')
    go_home()
    while pvp_item.go_pvp():
        fleet_needs_resupply[0] = True
        go_home()
        resupply()
        if settings['expeditions_enabled']:
            expedition_action_wrapper()
        if settings['quests_enabled']:
            quest_action('pvp')
        go_home()
    fleet_needs_resupply[0] = False

# Actions involved in conducting sorties
def sortie_action():
    global kc_window, fleet_needs_resupply, combat_item, settings
    fleetcomp_switch_action(settings['combat_fleetcomp'])
    go_home()
    combat_item.go_sortie()
    fleet_needs_resupply[0] = True
    if settings['combined_fleet']:
        fleet_needs_resupply[1] = True
    # Check home, repair if needed, and resupply
    go_home()
    if combat_item.count_damage_above_limit('repair') > 0:
        combat_item.go_repair()
    resupply()
    fleet_needs_resupply[0] = False
    if settings['combined_fleet']:
        fleet_needs_resupply[1] = False
    log_success("Next sortie!: %s" % combat_item)

# Actions that check and switch fleet comps
def fleetcomp_switch_action(fleetcomp):
    global kc_window, current_fleetcomp, fleetcomp_switcher, settings
    if fleetcomp_switcher and fleetcomp != current_fleetcomp:
        # fleetcomp_switcher is defined (aka necessary) AND the needed fleetcomp
        # is different from the current fleetcomp, go home then switch fleets
        go_home()
        fleetcomp_switcher.switch_fleetcomp(fleetcomp)
        current_fleetcomp = fleetcomp

# Display upcoming timers
def display_timers():
    global expedition_item, combat_item, next_pvp_time, next_sleep_time, settings
    log_success("-----")
    if settings['expeditions_enabled']:
        temp_time = ''
        for expedition in expedition_item.expedition_list:
            if temp_time == '':
                temp_time = expedition.end_time
            else:
                if expedition.end_time < temp_time:
                    temp_time = expedition.end_time
        log_success("Next expedition action at %s" % temp_time.strftime("%Y-%m-%d %H:%M:%S"))
    if settings['combat_enabled']:
        log_success("Next combat action at %s" % combat_item.next_sortie_time.strftime("%Y-%m-%d %H:%M:%S"))
    if settings['pvp_enabled']:
        log_success("Next PvP action at %s" % next_pvp_time.strftime("%Y-%m-%d %H:%M:%S"))
    if settings['scheduled_sleep_enabled']:
        log_success("Next scheduled sleep at %s" % next_sleep_time.strftime("%Y-%m-%d %H:%M:%S"))
    log_success("-----")

# Function to set the next sleep time
def reset_next_sleep_time(next_day = False):
    global next_sleep_time, settings
    next_sleep_time = datetime.datetime.now().replace(hour=int(settings['scheduled_sleep_start'][0:2]), minute=int(settings['scheduled_sleep_start'][2:4]), second=0, microsecond=0)
    next_sleep_time = next_sleep_time + datetime.timedelta(minutes=randint(1,30))
    if next_day:
        next_sleep_time = next_sleep_time + datetime.timedelta(days=1)

# Load the config.ini file
def get_config():
    global settings, sleep_cycle
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
    settings['jst_offset'] = config.getint('General', 'JSTOffset')
    sleep_cycle = config.getint('General', 'SleepCycle')
    # 'Scheduled Sleep' section
    if config.getboolean('ScheduledSleep', 'Enabled'):
        settings['scheduled_sleep_enabled'] = True
        settings['scheduled_sleep_start'] = "%04d"%config.getint('ScheduledSleep', 'StartTime')
        settings['scheduled_sleep_length'] = config.getfloat('ScheduledSleep', 'SleepLength')
    else:
        settings['scheduled_sleep_enabled'] = False
    # 'Expeditions' section
    if config.getboolean('Expeditions', 'Enabled'):
        settings['expeditions_enabled'] = True
        if config.get('Expeditions', 'Fleet2'):
            settings['expedition_id_fleet_map'][2] = config.getint('Expeditions', 'Fleet2')
        if config.get('Expeditions', 'Fleet3'):
            settings['expedition_id_fleet_map'][3] = config.getint('Expeditions', 'Fleet3')
        if config.get('Expeditions', 'Fleet4'):
            settings['expedition_id_fleet_map'][4] = config.getint('Expeditions', 'Fleet4')
        log_success("Expeditions (%s) enabled!" % (', '.join('fleet %s: %s' % (key, settings['expedition_id_fleet_map'][key]) for key in sorted(settings['expedition_id_fleet_map'].keys()))))
    else:
        settings['expeditions_enabled'] = False
    # 'PvP' section
    if config.getboolean('PvP', 'Enabled'):
        settings['pvp_enabled'] = True
        settings['pvp_fleetcomp'] = config.getint('PvP', 'FleetComp')
    else:
        settings['pvp_enabled'] = False
    # 'Combat' section
    if config.getboolean('Combat', 'Enabled'):
        settings['combat_enabled'] = True
        settings['combat_fleetcomp'] = config.getint('Combat', 'FleetComp')
        settings['submarine_switch'] = config.getboolean('Combat', 'SubmarineSwitch')
        settings['combat_area'] = config.get('Combat', 'Area')
        settings['combat_subarea'] = config.get('Combat', 'Subarea')
        settings['combined_fleet'] = config.getboolean('Combat', 'CombinedFleet')
        if settings['combined_fleet']:
            # Remove fleet 2 from expedition list if combined fleet is enabled
            settings['expedition_id_fleet_map'].pop(2, None)
            # Disable PvP if combined fleet is enabled
            settings['pvp_enabled'] = False
        settings['nodes'] = config.getint('Combat', 'Nodes')
        settings['node_selects'] = config.get('Combat', 'NodeSelects').replace(' ', '').split(',')
        if '' in settings['node_selects']:
            settings['node_selects'].remove('')
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
    # 'Quests' section
    settings['active_quests'] = config.get('Quests', 'Quests').replace(' ', '').split(',')
    settings['active_quests'].sort()
    if config.getboolean('Quests', 'Enabled') and len(settings['active_quests']) > 0:
        settings['quests_enabled'] = True
        settings['quests_check_schedule'] = config.getint('Quests', 'CheckSchedule')
    else:
        settings['quests_enabled'] = False
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
            type(Key.TAB) # Tab over to 'Start Anyway' button
            sleep(1)
            type(Key.SPACE)
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
    global kc_window, fleet_needs_resupply, current_fleetcomp, quest_item, expedition_item, combat_item, pvp_item, fleetcomp_switcher, default_quest_mode, settings
    get_config()
    get_util_config()
    log_success("Starting kancolle_auto")
    try:
        log_msg("Finding window!")
        focus_window()
        log_msg("Defining module items!")
        if settings['quests_enabled']:
            # Define quest item if quest module is enabled
            quest_item = quest_module.Quests(kc_window, settings)
        if settings['expeditions_enabled']:
            # Define expedition list if expeditions module is enabled
            expedition_item = expedition_module.Expedition(kc_window, settings)
        if settings['pvp_enabled']:
            # Define PvP item if pvp module is enabled
            pvp_item = combat_module.PvP(kc_window, settings)
        if settings['combat_enabled']:
            # Define combat item if combat module is enabled
            combat_item = combat_module.Combat(kc_window, settings)
            default_quest_mode = 'sortie'
        if settings['pvp_enabled'] and settings['combat_enabled']:
            if settings['pvp_fleetcomp'] == 0 or settings['combat_fleetcomp'] == 0:
                # If either of the fleetcomp values are set to 0, do not define the fleet comp
                # switcher module
                pass
            elif settings['pvp_fleetcomp'] != settings['combat_fleetcomp']:
                # Define fleet comp switcher module if both pvp and combat modules are enabled
                # and they have different fleet comps assigned
                fleetcomp_switcher = combat_module.FleetcompSwitcher(kc_window, settings)
        # Go home
        go_home(True)
        if settings['quests_enabled']:
            # Run through quests defined in quests item
            quest_action(default_quest_mode, True)
        if settings['expeditions_enabled']:
            # Run expeditions defined in expedition item
            expedition_action('all')
        if settings['pvp_enabled']:
            now_time = datetime.datetime.now()
            if not 3 <= jst_convert(now_time).hour < 5:
                # Run PvP, but not between the time when PvP resets but quests do not!
                pvp_action()
        if settings['combat_enabled']:
            # Run sortie defined in combat item
            sortie_action()
            # Let the Quests module know, if it's enabled
            if settings['quests_enabled']:
                quest_item.done_sorties += 1
    except FindFailed, e:
        refresh_kancolle(e)

# initialize kancolle_auto
init()
log_msg("Initial checks and commands complete. Starting loop.")
while True:
    if settings['scheduled_sleep_enabled']:
        now_time = datetime.datetime.now()
        # If just starting script, set a sleep start time
        if next_sleep_time is None:
            if now_time.hour * 100 + now_time.minute > int(settings['scheduled_sleep_start']):
                # If the schedule sleep start time for the day has passed, set it for the next day
                reset_next_sleep_time(True)
            else:
                # Otherwise, set it for later in the day
                reset_next_sleep_time()
        if now_time > next_sleep_time:
            # If it's time to sleep, set the next sleep start time...
            reset_next_sleep_time(True)
            # ... and go to sleep
            log_msg("Schedule sleep begins! See you in around %s hours!" % settings['scheduled_sleep_length'])
            sleep(settings['scheduled_sleep_length'] * 3600, 600)
    try:
        if settings['expeditions_enabled']:
            # If expedition timers are up, check for their arrival
            for expedition in expedition_item.expedition_list:
                now_time = datetime.datetime.now()
                if now_time > expedition.end_time and not expedition.returned:
                    idle = False
                    log_msg("Checking for return of expedition %s" % expedition.id)
                    go_home(True)
                    # Set the fleet returned flag to True for the expected fleet to force
                    # a refresh on its status, even if it wasn't received by the script
                    fleet_needs_resupply[expedition.fleet_id - 1] = True
                    expedition.returned = True
            # If there are fleets ready to go, go start their assigned expeditions
            expedition_action_wrapper()
        if settings['quests_enabled']:
            # Reset and check quests at 0500 JST
            now_time = datetime.datetime.now()
            if jst_convert(now_time).hour == 5 and quest_reset_skip is False:
                idle = False
                go_home()
                quest_item.reset_quests()
                quest_action(default_quest_mode, True)
                quest_reset_skip = True # Let's not keep resetting the quests
            # Reset the quest_reset_skip variable in preparation for the next quest reset
            if jst_convert(now_time).hour == 6 and quest_reset_skip is True:
                quest_reset_skip = False
        if settings['pvp_enabled']:
            # Set the next PvP time at 0500 JST (after daily quest reset) and 1500 JST (second daily PvP reset)
            if ((jst_convert(now_time).hour == 5 and pvp_timer_skip is False)
                or (jst_convert(now_time).hour == 15 and pvp_timer_skip is False)):
                idle = False
                next_pvp_time = datetime.datetime.now() + datetime.timedelta(hours=randint(0,1), minutes=randint(0,60))
                pvp_timer_skip = True # Let's not keep reseting the next pvp time
            now_time = datetime.datetime.now()
            if now_time > next_pvp_time and pvp_timer_skip:
                idle = False
                pvp_action()
                pvp_timer_skip = False # Now that we've PvPed, reset the timer skip
        # If combat timer is up, go do sortie-related stuff
        if settings['combat_enabled']:
            # If there are ships that still need repair, go take care of them
            if combat_item.count_damage_above_limit('repair') > 0 and len(combat_item.repair_timers) > 0:
                if datetime.datetime.now() > combat_item.repair_timers[0]:
                    combat_item.go_repair()
            # If the fleet is ready, go sortie
            if datetime.datetime.now() > combat_item.next_sortie_time:
                idle = False
                sortie_action()
                # Let the Quests module know, if it's enabled
                if settings['quests_enabled']:
                    quest_item.done_sorties += 1
        if settings['quests_enabled']:
            if idle == False:
                # Expedition or Combat event occured. Loop 'increases'
                quest_item.schedule_loop += 1
                temp_need_to_check = quest_item.need_to_check()
                log_msg("Quest check loop count at %s; need to check is %s with ~%s quests being tracked" % (quest_item.schedule_loop, temp_need_to_check, quest_item.active_quests))
            if temp_need_to_check:
                go_home()
                quest_action(default_quest_mode)
                temp_need_to_check = False # Disable need to check after checking
        # If fleets have been sent out and idle period is beginning, let the user
        # know when the next scripted action will occur
        if not idle:
            display_timers()
            idle = True
        sleep(sleep_cycle)
    except FindFailed, e:
        refresh_kancolle(e)
