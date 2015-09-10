from time import sleep
import datetime
import os
import sys
sys.path.append(os.getcwd())#get current script working directory inside the .sikuli folder and append as sys path
import expedition as expedition_module
from util import log_msg, log_success, log_warning, log_error

Settings.OcrTextRead = True
WAITLONG = 60

# START USER VARIABLES

#PROGRAM = "KanColleTool Viewer"
#PROGRAM = "KanColleViewer!""
PROGRAM = "Google Chrome"

# mapping fleet id to expedition id
expedition_id_fleet_map = {
    2: 2,
    3: 5,
    4: 21
}

#combat_fleet_mode = 0 # 2-3 (Orel cruising)
combat_fleet_mode = 1 # 3-2-A (leveling)

# END USER VARIABLES

expedition_list = None
running_expedition_list = []
fleet_returned = [False, False, False, False]
kc_window = None
next_action = ''
idle = False

def check_and_click(pic):
    if kc_window.exists(pic):
        kc_window.click(pic)
        return True
    return False

def wait_and_click(pic, time=0):
    if time:
        kc_window.wait(pic, time)
    else:
        kc_window.wait(pic)
    kc_window.click(pic)

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
    # Focus on KanColle
    focus_window()
    kc_window.wait("senseki_off.png", WAITLONG)
    # Check for expeditions in case starting at Home screen
    if check_expedition():
        # If there are returning expeditions, there's no need to refresh the
        # Home screen. Go straight to resupplying fleets
        log_success("At home!")
        resupply()
    else:
        # Check for expeditions by refreshing/getting to Home screen
        if not check_and_click("home_side.png"):
            if check_and_click("supply_main.png"):
                # If the sidebar Home button doesn't exist, we might already be
                # at the Home screen. Enter Supply screen and back to Home
                kc_window.hover("senseki_off.png")
                sleep(2)
                check_and_click("home_side.png")
            else:
                # If both sidebar Home and main Supply button doesn't exist,
                # we might be in a top menu screen (profile/library/etc). Hit
                # the upper left orb until we're out
                while not kc_window.exists(Pattern("supply_main.png")):
                    check_and_click("home_main.png")
        # Back at home
        kc_window.hover("senseki_off.png")
        kc_window.wait("sortie.png", WAITLONG)
        log_success("At home!")
        # Check for completed expeditions. Resupply them if there are.
        if check_expedition():
            resupply()

# Check expedition arrival flag on home screen; ultimately return True if there
# was at least one expedition received.
def check_expedition():
    global kc_window, expedition_id_fleet_map, expedition_list, fleet_returned
    log_msg("Are there returning expeditions to receive?")
    kc_window.hover("senseki_off.png")
    if check_and_click("expedition_finish.png"):
        wait_and_click("next.png", WAITLONG)
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
        wait_and_click("next.png")
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
        if not check_and_click("supply_main.png"):
            check_and_click("supply_side.png")
        kc_window.wait("supply_screen.png", WAITLONG)
        for fleet_id, returned in enumerate(fleet_returned):
            if returned:
                # If not resupplying the first fleet, navigate to correct fleet
                if fleet_id != 0:
                    fleet_name = "fleet_%d.png" % (fleet_id + 1)
                    wait_and_click(fleet_name)
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
        while not kc_window.exists("checked.png"):
            kc_window.hover("senseki_off.png")
            kc_window.hover("supply_all.png")
            kc_window.click("supply_all.png")
            sleep(1)
        kc_window.click("supply_available.png")
        kc_window.wait("supply_not_available.png", WAITLONG)
        sleep(1)

# Navigate to Expedition menu
def go_expedition():
    global kc_window
    log_msg("Navigating to Expedition menu!")
    kc_window.hover("senseki_off.png")
    wait_and_click("sortie.png", WAITLONG)
    wait_and_click("expedition.png", WAITLONG)
    kc_window.wait("expedition_screen_ready.png", WAITLONG)

# Run expedition
def run_expedition(expedition):
    global kc_window, running_expedition_list, fleet_returned
    log_msg("Let's send an expedition out!")
    kc_window.click(expedition.area_pict)
    sleep(1)
    kc_window.click(expedition.name_pict)
    sleep(1)
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
            expedition_timer_raw = find("expedition_timer.png").right(80).text()
            # In case OCR grabs the wrong characters...
            expedition_timer = list(expedition_timer_raw)
            expedition_timer[2] = ":"
            expedition_timer[5] = ":"
            expedition_timer = "".join(expedition_timer)
            expedition_timer = expedition_timer.replace('l', '1').replace('I', '1').replace('O', '0')
            # Set expedition's end time as determined via OCR and add it to
            # running_expedition_list
            expedition.check_later(int(expedition_timer[0:2]), int(expedition_timer[3:5]))
            running_expedition_list.append(expedition)
            log_warning("Expedition is already running:  %s" % expedition)
        return
    kc_window.click("decision.png")
    sleep(3)
    log_msg("Trying to send out fleet %s for expedition %s" % (fleet_id, expedition.id))
    # Select fleet (no need if fleet is 2 as it's selected by default)
    if fleet_id != 2:
        fleet_name = "fleet_%s.png" % fleet_id
        kc_window.click(fleet_name)
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
        sleep(1)
        kc_window.click("ensei_start.png")
        sleep(3)
        kc_window.wait("exp_started.png", 300)
        expedition.start()
        running_expedition_list.append(expedition)
        fleet_returned[fleet_id - 1] = False
        log_success("Expedition sent!: %s" % expedition)
        sleep(3)
    else:
        # Fleet's being used for some reason... check back later
        log_error("Fleet not available. Check back later!")
        expedition.check_later(0, 10)
        kc_window.click("ensei_area_01.png")

def check_soonest():
    global running_expedition_list, next_action
    next_action = '' # reset
    for expedition in running_expedition_list:
        if next_action == '':
            next_action = expedition.end_time
        else:
            if expedition.end_time < next_action:
                next_action = expedition.end_time

def init():
    global expedition_list
    log_success("Starting kancolle_auto")
    # define expedition list
    expedition_list = map(expedition_module.ensei_factory, expedition_id_fleet_map.values())
    combat_item = combat_module.combat_factory(combat_fleet_mode)
    go_home()
    go_expedition()
    for expedition in expedition_list:
        run_expedition(expedition)

# initialize kancolle_auto
init()
log_msg("Initial checks and commands complete. Starting loop.")
while True:
    for expedition in running_expedition_list:
        now_time = datetime.datetime.now()
        # Check for returning fleets based on stored end time of expeditions
        if now_time > expedition.end_time:
            idle = False
            log_msg("Checking for return of expedition %s" % expedition.id)
            go_home()
    # If there are fleets ready to go, go start their assigned expeditions
    if True in fleet_returned:
        go_expedition()
        for fleet_id, fleet_status in enumerate(fleet_returned):
            if fleet_status == True:
                for expedition in expedition_list:
                    if expedition.id == expedition_id_fleet_map[fleet_id + 1]:
                        run_expedition(expedition)
    # If fleets have been sent out and idle period is beginning, let the user
    # know when the next scripted action will occur
    if idle == False:
        check_soonest()
        log_msg("Next action at %s" % next_action.strftime("%Y-%m-%d %H:%M:%S"))
        idle = True
    sleep(10)
