import datetime, os, sys, random
sys.path.append(os.getcwd())
import expedition as expedition_module
import combat as combat_module
from util import (sleep, get_rand, check_and_click, wait_and_click, check_timer,
    log_msg, log_success, log_warning, log_error)

Settings.OcrTextRead = True
Settings.MinSimilarity = 0.8
WAITLONG = 60

# START USER VARIABLES

#PROGRAM = "KanColleTool Viewer"
#PROGRAM = "KanColleViewer!""
PROGRAM = "Google Chrome"

# mapping fleet id to expedition id
expedition_id_fleet_map = {
    2: 2,
    3: 38
}

# turn combat on?
combat = True
#combat_fleet_mode = 0 # 2-3 (Orel cruising) NOT YET SUPPORTED
combat_fleet_mode = 1 # 3-2-A (leveling)

# stop at 0 = light damage, 1 = medium damage, 2 = critical damage
combat_fleet_dmg_limit = 1

repair_time_limit = 3

# END USER VARIABLES

expedition_list = None
running_expedition_list = []
fleet_returned = [False, False, False, False]
combat_item = None
kc_window = None
next_action = ''
idle = False

# Focus on the defined KanColle app
def focus_window():
    global kc_window
    log_msg("Focus on KanColle!")
    myApp = App.focus(PROGRAM)
    kc_window = myApp.focusedWindow()
    # Wake screen up in case machine has been idle
    # Would cause issues when (0,0) to (1,1) - windows focus issue??
    kc_window.mouseMove(Location(kc_window.x + 100, kc_window.y + 100))
    kc_window.mouseMove(Location(kc_window.x + 120,kc_window.y + 120))
    while not kc_window.exists(Pattern("home_main.png").exact()):
        myApp = App.focus(PROGRAM)
        kc_window = myApp.focusedWindow()
    sleep(2)

# Switch to KanColle app, navigate to Home screen, and receive+resupply any
# returning expeditions
def go_home():
    global kc_window
    random_menu = ["supply_main.png", "repair_main.png", "sortie.png",
        "senseki_off.png", "quests_main.png"]
    # Focus on KanColle
    focus_window()
    kc_window.wait("senseki_off.png", WAITLONG)
    # Check if we're already at home screen
    if kc_window.exists("sortie.png"):
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
            if not check_and_click(kc_window, "home_side.png"):
                # If the side Home button doesn't exist, we're probably in a
                # top-menu item...
                while not kc_window.exists("sortie.png"):
                    # ... so hit the return button that exists in the top-menu item
                    # pages until we get home
                    wait_and_click(kc_window, "top_menu_return.png", 10)
                    sleep(2)
            log_success("At Home!")
            # Check for completed expeditions. Resupply them if there are.
            if check_expedition():
                resupply()
    else:
        # We're not, so check for expeditions by getting to the Home screen
        log_msg("Going Home!")
        if not check_and_click(kc_window, "home_side.png"):
            # If the side Home button doesn't exist, we're probably in a
            # top-menu item...
            while not kc_window.exists("sortie.png"):
                # ... so hit the return button that exists in the top-menu item
                # pages until we get home
                wait_and_click(kc_window, "top_menu_return.png", 10)
                sleep(2)
        # Back at home
        kc_window.hover("senseki_off.png")
        kc_window.wait("sortie.png", WAITLONG)
        log_success("At Home!")
        # Check for completed expeditions. Resupply them if there are.
        if check_expedition():
            resupply()

# Check expedition arrival flag on home screen; ultimately return True if there
# was at least one expedition received.
def check_expedition():
    global kc_window, expedition_id_fleet_map, expedition_list, fleet_returned
    log_msg("Are there returning expeditions to receive?")
    kc_window.hover("senseki_off.png")
    if check_and_click(kc_window, "expedition_finish.png"):
        sleep(3)
        wait_and_click(kc_window, "next.png", WAITLONG)
        # Identify which fleet came back
        if kc_window.exists(Pattern("returned_fleet2.png").exact()): fleet_id = 2
        elif kc_window.exists(Pattern("returned_fleet3.png").exact()): fleet_id = 3
        elif kc_window.exists(Pattern("returned_fleet4.png").exact()): fleet_id = 4
        # If fleet has an assigned expedition, set its return status to True.
        # Otherwise leave it False, since the user might be using it
        if fleet_id in expedition_id_fleet_map:
            fleet_returned[fleet_id - 1] = True
        # Remove the associated expedition from running_expedition_list
        for expedition in running_expedition_list:
            if expedition.id == expedition_id_fleet_map[fleet_id]:
                running_expedition_list.remove(expedition)
        log_success("Yes, fleet %s has returned!" % fleet_id)
        wait_and_click(kc_window, "next.png")
        kc_window.wait("sortie.png", WAITLONG)
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
        kc_window.hover("senseki_off.png")
        if not check_and_click(kc_window, "supply_main.png"):
            check_and_click(kc_window, "supply_side.png")
        kc_window.wait("supply_screen.png", WAITLONG)
        for fleet_id, returned in enumerate(fleet_returned):
            if returned:
                # If not resupplying the first fleet, navigate to correct fleet
                if fleet_id != 0:
                    fleet_name = "fleet_%d.png" % (fleet_id + 1)
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
    if kc_window.exists(Pattern("supply_all.png").exact()):
        # Common point of script failure. Make robust as possible
        while not kc_window.exists(Pattern("checked.png").exact()):
            kc_window.hover("senseki_off.png")
            kc_window.hover("supply_all.png")
            kc_window.click("supply_all.png")
        wait_and_click(kc_window, "supply_available.png", 10)
        kc_window.wait("supply_not_available.png", WAITLONG)
        sleep(1)
    else:
        log_msg("Fleet is already resupplied!")

# Navigate to Expedition menu
def go_expedition():
    global kc_window
    log_msg("Navigating to Expedition menu!")
    kc_window.hover("senseki_off.png")
    wait_and_click(kc_window, "sortie.png", WAITLONG)
    wait_and_click(kc_window, "expedition.png", WAITLONG)
    kc_window.wait("expedition_screen_ready.png", WAITLONG)

# Run expedition
def run_expedition(expedition):
    global kc_window, running_expedition_list, fleet_returned
    log_msg("Let's send an expedition out!")
    sleep(2)
    wait_and_click(kc_window, expedition.area_pict, 10)
    sleep(2)
    wait_and_click(kc_window, expedition.name_pict, 10)
    for fleet, exp in expedition_id_fleet_map.iteritems():
        if exp == expedition.id:
            fleet_id = fleet
    # If the expedition can't be selected, it's either running or just returned
    if not kc_window.exists("decision.png"):
        fleet_returned[fleet_id - 1] = False
        if kc_window.exists("expedition_time_complete.png"):
            # Expedition just returned
            expedition.check_later(0, -1) # set the check_later time to now
            log_warning("Expedition just returned:  %s" % expedition)
        else:
            # Expedition is already running
            expedition_timer = check_timer(kc_window, "expedition_timer.png", 80)
            # Set expedition's end time as determined via OCR and add it to
            # running_expedition_list
            expedition.check_later(int(expedition_timer[0:2]), int(expedition_timer[3:5]))
            running_expedition_list.append(expedition)
            log_warning("Expedition is already running: %s" % expedition)
        return
    wait_and_click(kc_window, "decision.png")
    log_msg("Trying to send out fleet %s for expedition %s" % (fleet_id, expedition.id))
    # Select fleet (no need if fleet is 2 as it's selected by default)
    if fleet_id != 2:
        fleet_name = "fleet_%s.png" % fleet_id
        wait_and_click(kc_window, fleet_name)
    sleep(1)
    # Make sure that the fleet is ready to go
    if not kc_window.exists("fleet_busy.png"):
        if (kc_window.exists("supply_alert.png") or kc_window.exists("supply_red_alert.png")):
            log_warning("Fleet %s needs resupply!" % fleet_id)
            fleet_returned[fleet_id - 1] = True
            resupply()
            go_expedition()
            run_expedition(expedition)
            return
        kc_window.hover("senseki_off.png")
        wait_and_click(kc_window, "ensei_start.png")
        kc_window.wait("exp_started.png", 30)
        expedition.start()
        running_expedition_list.append(expedition)
        fleet_returned[fleet_id - 1] = False
        log_success("Expedition sent!: %s" % expedition)
        sleep(1)
    else:
        # Fleet's being used for some reason... check back later
        log_error("Fleet not available. Check back later!")
        expedition.check_later(0, 10)
        kc_window.click("ensei_area_01.png")

def check_soonest():
    global running_expedition_list, combat, combat_item, next_action
    next_action = combat_item.next_sortie_time if combat == True else ''
    for expedition in running_expedition_list:
        if next_action == '':
            next_action = expedition.end_time
        else:
            if expedition.end_time < next_action:
                next_action = expedition.end_time

def init():
    global kc_window, expedition_list, fleet_returned, combat, dmg_counts, combat_item
    log_success("Starting kancolle_auto")
    # Define expedition list
    expedition_list = map(expedition_module.ensei_factory, expedition_id_fleet_map.values())
    # Go home, then run expeditions
    go_home()
    go_expedition()
    for expedition in expedition_list:
        run_expedition(expedition)
    if combat == True:
        # Define combat item
        combat_item = combat_module.combat_factory(kc_window, combat_fleet_mode, combat_fleet_dmg_limit)
        # Go home, then sortie
        go_home()
        combat_item.go_sortie()
        fleet_returned[0] = True
        # Check home, resupply, then repair if needed
        go_home()
        resupply()
        fleet_returned[0] = False
        if combat_item.count_dmg_above_limit() > 0:
            combat_item.go_repair()
        log_success("Next sortie!: %s" % combat_item)

# initialize kancolle_auto
init()
log_msg("Initial checks and commands complete. Starting loop.")
while True:
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
                    if expedition.id == expedition_id_fleet_map[fleet_id + 1]:
                        idle = False
                        run_expedition(expedition)
    # If combat timer is up, go sortie
    if combat == True:
        if datetime.datetime.now() > combat_item.next_sortie_time:
            go_home()
            combat_item.go_sortie()
            fleet_returned[0] = True
            go_home()
            resupply()
            fleet_returned[0] = False
            if combat_item.count_dmg_above_limit() > 0:
                combat_item.go_repair()
            log_success("Next sortie!: %s" % combat_item)
            go_home()
            idle = False
    # If fleets have been sent out and idle period is beginning, let the user
    # know when the next scripted action will occur
    if idle == False:
        check_soonest()
        log_msg("Next action at %s" % next_action.strftime("%Y-%m-%d %H:%M:%S"))
        idle = True
    sleep(20)
