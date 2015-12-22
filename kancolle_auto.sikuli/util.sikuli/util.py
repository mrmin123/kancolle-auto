import ConfigParser, datetime
from sikuli import *
from random import uniform, randint, choice
from time import sleep as tsleep, strftime
from re import match

Settings.OcrTextRead = True
util_settings = {}

def get_util_config():
    """Load the settings related to the util module"""
    global util_settings
    log_msg("Reading config file")
    # Change paths and read config.ini
    os.chdir(getBundlePath())
    os.chdir('..')
    config = ConfigParser.ConfigParser()
    config.read('config.ini')
    # Set user settings
    # 'General'/misc settings
    util_settings['paranoia'] = 0 if config.getint('General', 'Paranoia') < 0 else config.getint('General', 'Paranoia')
    util_settings['sleep_mod'] = 0 if config.getint('General', 'SleepModifier') < 0 else config.getint('General', 'SleepModifier')
    util_settings['jst_offset'] = config.getint('General', 'JSTOffset')

def sleep(base, flex=-1):
    """
    Function for setting a random sleep time. Sleep length set by this function
    can vary from base to base * 2, or base to base + flex if flex is provided.

    base - positive int
    flex - positive int; defaults to -1 to disable
    """
    global util_settings
    if flex == -1:
        tsleep(uniform(base, base * 2) + util_settings['sleep_mod'])
    else:
        tsleep(uniform(base, flex) + util_settings['sleep_mod'])

def check_timer(kc_window, timer_ref, dir, width, attempt_limit=0):
    """
    Function for grabbing valid Kancolle timer readings (##:##:## format).
    Attempts to fix erroneous OCR reads and repeats readings until a valid
    timer value is returned. Returns timer string in ##:##:## format.

    kc_window - Sikuli window
    timer_ref - image name (str) or reference Match object (returned by findAll, for example)
    dir - 'l' or 'r'; direction to search for text
    width - positive int; width (in pixels) of area where the timer text should be
    attempt_limit = how many times the OCR reads should repeat before returning
        95:00:00 as an arbitrary high timer
    """
    ocr_matching = True
    attempt = 0
    while ocr_matching:
        attempt += 1
        if isinstance(timer_ref, str):
            if dir == 'r':
                timer = find(timer_ref).right(width).text().encode('utf-8')
            elif dir == 'l':
                timer = find(timer_ref).left(width).text().encode('utf-8')
        elif isinstance(timer_ref, Match):
            if dir == 'r':
                timer = timer_ref.right(width).text().encode('utf-8')
            elif dir == 'l':
                timer = timer_ref.left(width).text().encode('utf-8')
        # Replace characters
        timer = (
            timer.replace('O', '0').replace('o', '0').replace('D', '0')
            .replace('Q', '0').replace('@', '0').replace('l', '1').replace('I', '1')
            .replace('[', '1').replace(']', '1').replace('|', '1').replace('!', '1')
            .replace('Z', '2').replace('S', '5').replace('s', '5').replace('$', '5')
            .replace('B', '8').replace(':', '8').replace(' ', '').replace('-', '')
        )
        if len(timer) == 8:
            # Length checks out...
            timer = list(timer)
            timer[2] = ':'
            timer[5] = ':'
            timer = ''.join(timer)
            m = match(r'^\d{2}:\d{2}:\d{2}$', timer)
            if m:
                # OCR reading checks out; return timer reading
                ocr_matching = False
                log_msg("Got valid timer (%s)!" % timer)
                return timer
        # If we got this far, the timer reading is invalid.
        # If an attempt_limit is set and met, return 95:00:00
        if attempt_limit != 0 and attempt == attempt_limit:
            log_warning("Got invalid timer and met attempt threshold. Returning 95:00:00!")
            return '95:00:00'
        # Otherwise, try again!
        log_warning("Got invalid timer (%s)... trying again!" % timer)
        sleep(1)

def rclick(kc_window, pic, expand=[]):
    """
    Function for randomizing click location. If expand is not provided the
    click location will be within the image/Pattern's area. If expand is provided,
    the click location will be in the area expanded relative to the center of
    the image/Pattern.

    kc_window - Sikuli window
    pic - image name (str) or Pattern object to match/click
    expand - list containing custom click boundaries in [left, right, top, bottom]
        directions. Values should all be (int)s, and relative to the center of
        the matched Pattern. Defaults to [] to default to Pattern area.
    """
    reset_mouse = False
    if len(expand) == 0:
        # This slows down the click actions, but it looks for the pattern and
        # finds the size of the image from the resulting Pattern object.
        m = match(r'M\[\d+\,\d+ (\d+)x(\d+)\]', str(find(pic)))
        if m:
            # If a match is found and the x,y sizes can be ascertained, generate
            # the random offsets. Otherwise, just click the damn middle.
            x_width = int(m.group(1)) / 2
            y_height = int(m.group(2)) / 2
            expand = [-x_width, x_width, -y_height, y_height]
    else:
        reset_mouse = True
    if len(expand) == 4:
        if isinstance(pic, str):
            pic = Pattern(pic).targetOffset(int(uniform(expand[0], expand[1])), int(uniform(expand[2], expand[3])))
        elif isinstance(pic, Pattern):
            pic = pic.targetOffset(int(uniform(expand[0], expand[1])), int(uniform(expand[2], expand[3])))
    kc_window.click(pic)
    if reset_mouse:
        kc_window.mouseMove(Location(kc_window.x + 100, kc_window.y + 100))

def expand_areas(target):
    """
    Function to return pre-defined click expand areas. Returns list of 4 ints
    (see rclick function for more details).

    target - str; which list to return
    """
    if target == 'expedition_finish':
        return [-350, 200, 0, 400]
    elif target == 'next':
        return [-600, 0, -400, 0]
    elif target == 'compass':
        return [-250, 400, -200, 200]
    elif target == 'quests_screen_check':
        return [-40, 700, -50, 300]
    elif target == 'quest_bar':
        return [-170, 350, -40, -5]
    elif target == 'quests_navigation':
        return [-10, 10, -5, 5]
    elif target == 'quest_completed':
        return [-580, 25, 25, -25]
    elif target == 'pvp_row':
        return [-500, 80, -35, 45]

def rnavigation(kc_window, destination, max=0):
    """
    Random navigation function. Randomly wanders through menu items a number
    of times before reaching its destination.

    kc_window - Sikuli window
    destination - 'home', 'refresh_home', 'fleetcomp', 'resupply', 'equip',
        'repair', 'development'; valid final destinations
    max - custom # of side-steps. Defaults to 0 to default to Paranoia setting
    """
    global util_settings
    # Look at all the things we can click!
    menu_main_options = ['menu_main_sortie.png', 'menu_main_fleetcomp.png', 'menu_main_resupply.png',
        'menu_main_equip.png', 'menu_main_repair.png', 'menu_main_development.png']
    menu_top_options = ['menu_top_encyclopedia.png', 'menu_top_inventory.png',
        'menu_top_furniture.png', 'menu_top_shop.png', 'menu_top_quests.png']
    menu_side_options = ['menu_side_fleetcomp.png', 'menu_side_resupply.png', 'menu_side_equip.png',
        'menu_side_repair.png', 'menu_side_development.png']
    menu_sortie_options = ['sortie_combat.png', 'sortie_expedition.png', 'sortie_pvp.png']
    menu_sortie_top_options = ['sortie_top_combat.png', 'sortie_top_expedition.png', 'sortie_top_pvp.png']
    final_target = ''
    # Set max evasion steps
    if max == 0:
        # If max evasion was not defined by the function call, use paranoia
        # setting from config
        max = util_settings['paranoia']
    else:
        if util_settings['paranoia'] < max:
            # If max evasion was defined by the function call, but the paranoia
            # setting from config is shorter, use the paranoia setting
            max = util_settings['paranoia']
    evade_count = randint(0, max)
    # Figure out where we are
    current_location = ''
    if kc_window.exists('menu_main_sortie.png'):
        current_location = 'home'
    elif kc_window.exists('menu_side_home.png'):
        current_location = 'sidemenu'
    elif kc_window.exists('menu_top_home.png'):
        current_location = 'topmenu'
    else:
        current_location = 'other'
    # Random navigations, depending on where we are, and where we want to go
    kc_window.mouseMove(Location(kc_window.x + 100, kc_window.y + 100))
    if current_location == 'home':
        # Starting from home screen
        if destination == 'home':
            # Already at home
            pass
        elif destination == 'refresh_home':
            # Refresh home
            log_msg("Refreshing home with %d or less sidestep(s)!" % (evade_count))
            rchoice = rnavigation_chooser(menu_top_options + menu_main_options, [])
            wait_and_click(kc_window, rchoice)
            sleep(2)
            evade_count -= 1
            if rchoice.startswith('menu_top'):
                # At top menu item; hit the home button until we get home (Akashi/Ooyodo, go away)
                final_target = 'menu_top_home.png'
            elif rchoice.startswith('menu_main'):
                if evade_count == 0:
                    final_target = 'menu_side_home.png'
                else:
                    rchoice = rnavigation_chooser(menu_side_options, ['menu_side_' + rchoice[10:]])
                    while evade_count > 0:
                        rchoice = rnavigation_chooser(menu_side_options, [rchoice])
                        wait_and_click(kc_window, rchoice)
                        sleep(2)
                        evade_count -= 1
                    final_target = 'menu_side_home.png'
        elif destination in ['combat', 'expedition', 'pvp']:
            # Go to a sortie menu screen
            log_msg("Navigating to %s menu with %d sidestep(s)!" % (destination, evade_count))
            wait_and_click(kc_window, 'menu_main_sortie.png')
            kc_window.mouseMove(Location(kc_window.x + 100, kc_window.y + 100))
            sleep(2)
            if evade_count == 0:
                final_target = 'sortie_' + destination + '.png'
            else:
                rchoice = rnavigation_chooser(menu_sortie_options, ['sortie_' + destination + '.png'])
                wait_and_click(kc_window, rchoice)
                kc_window.mouseMove(Location(kc_window.x + 100, kc_window.y + 100))
                evade_count -= 1
                while evade_count > 0:
                    if rchoice.startswith('sortie_top'):
                        rchoice = rnavigation_chooser(menu_sortie_top_options, [rchoice, 'sortie_top_' + destination + '.png'])
                    else:
                        rchoice = rnavigation_chooser(menu_sortie_top_options, ['sortie_top_' + rchoice[7:], 'sortie_top_' + destination + '.png'])
                    wait_and_click(kc_window, rchoice)
                    sleep(2)
                    evade_count -= 1
                final_target = 'sortie_top_' + destination + '.png'
        elif destination in ['quests']:
            # Go to quests screen
            log_msg("Navigating to %s menu with %d sidestep(s)!" % (destination, evade_count))
            if evade_count == 0:
                final_target = 'menu_top_quests.png'
            else:
                rchoice = rnavigation_chooser(menu_main_options + ['menu_top_profile.png', 'menu_top_inventory.png'], [])
                wait_and_click(kc_window, rchoice)
                sleep(2)
                evade_count -= 1
                while evade_count > 0:
                    if rchoice.startswith('menu_top'):
                        # Went to another top menu item. Go straight to target to make things simple
                        final_target = 'menu_top_quests.png'
                        evade_count = 0
                    else:
                        rchoice = rnavigation_chooser(menu_side_options, [])
                        wait_and_click(kc_window, rchoice)
                        sleep(2)
                        evade_count -= 1
                final_target = 'menu_top_quests.png'
        else:
            # Go to and side menu sub screen
            log_msg("Navigating to %s screen with %d sidestep(s)!" % (destination, evade_count))
            if evade_count == 0:
                final_target = 'menu_main_' + destination + '.png'
            else:
                rchoice = rnavigation_chooser(menu_main_options, ['menu_main_' + destination + '.png'])
                wait_and_click(kc_window, rchoice)
                evade_count -= 1
                while evade_count > 0:
                    if rchoice.startswith('menu_main'):
                        rchoice = rnavigation_chooser(menu_side_options, ['menu_side_' + rchoice[10:], 'sortie_top_' + destination + '.png'])
                    else:
                        rchoice = rnavigation_chooser(menu_side_options, [rchoice, 'sortie_top_' + destination + '.png'])
                    wait_and_click(kc_window, rchoice)
                    sleep(2)
                    evade_count -= 1
                final_target = 'menu_side_' + destination + '.png'
    if current_location == 'sidemenu':
        # Starting from a main menu item screen
        if destination == 'home' or destination == 'refresh_home':
            # Go or refresh home
            log_msg("Going home with %d or less sidestep(s)!" % (evade_count))
            if evade_count == 0:
                final_target = 'menu_side_home.png'
            else:
                rchoice = rnavigation_chooser(menu_top_options + menu_side_options, [])
                while evade_count > 0:
                    rchoice = rnavigation_chooser(menu_top_options + menu_side_options, [rchoice])
                    wait_and_click(kc_window, rchoice)
                    sleep(2)
                    evade_count -= 1
                    if rchoice.startswith('menu_top'):
                        # At top menu item; hit the home button until we get home (Akashi/Ooyodo, go away)
                        final_target = 'menu_top_home.png'
                        # This takes us back to home immediately, so no more random menus
                        evade_count = 0
                    else:
                        # Still at side menu item, so continue as normal
                        if evade_count == 0:
                            # Unless that was the last random menu item; then go home
                            final_target = 'menu_side_home.png'
        elif destination in ['quests']:
            # Go to quests screen
            log_msg("Navigating to %s menu with %d sidestep(s)!" % (destination, evade_count))
            if evade_count == 0:
                final_target = 'menu_top_quests.png'
            else:
                rchoice = rnavigation_chooser(menu_top_options + menu_side_options, ['menu_top_quests.png', 'menu_top_shop.png'])
                wait_and_click(kc_window, rchoice)
                sleep(2)
                evade_count -= 1
                while evade_count > 0:
                    if rchoice.startswith('menu_top'):
                        # Went to another top menu item. Go straight to target to make things simple
                        final_target = 'menu_top_quests.png'
                        evade_count = 0
                    else:
                        rchoice = rnavigation_chooser(menu_side_options + ['menu_top_profile.png', 'menu_top_inventory.png'], [])
                        wait_and_click(kc_window, rchoice)
                        sleep(2)
                        evade_count -= 1
                final_target = 'menu_top_quests.png'
        else:
            # Go to another main menu item screen
            log_msg("Navigating to %s screen with %d sidestep(s)!" % (destination, evade_count))
            if evade_count == 0:
                final_target = 'menu_side_' + destination + '.png'
            else:
                rchoice = rnavigation_chooser(menu_side_options, ['menu_side_' + destination + '.png'])
                while evade_count > 0:
                    rchoice = rnavigation_chooser(menu_side_options, [rchoice, 'menu_side_' + destination + '.png'])
                    wait_and_click(kc_window, rchoice)
                    evade_count -= 1
                    sleep(2)
                final_target = 'menu_side_' + destination + '.png'
    if current_location == 'topmenu':
        # Starting from top menu item. Theoretically, the script should never
        # attempt to go anywhere but home from here
        if destination in ['home', 'refresh_home']:
            log_msg("Going home!")
            # At top menu item; hit the home button until we get home (Akashi/Ooyodo, go away)
            final_target = 'menu_top_home.png'
    while final_target != '':
        # In while loop so that if the button has to be pressed again for some
        # reason, it'll do it. Only works for certain destinations.
        wait_and_click(kc_window, final_target)
        sleep(2)
        # Always reset mouse after reaching destination
        kc_window.mouseMove(Location(kc_window.x + 100, kc_window.y + 100))
        # If one of these targets, check to see if we're actually there.
        if final_target in ['menu_top_home.png', 'menu_side_home.png']:
            if kc_window.exists('menu_main_sortie.png'):
                final_target = ''
        elif final_target in ['sortie_expedition.png', 'sortie_top_expedition.png']:
            if kc_window.exists('expedition_screen_ready.png'):
                final_target = ''
        elif final_target in ['menu_main_resupply.png', 'menu_side_resupply.png']:
            if kc_window.exists('resupply_screen.png'):
                final_target = ''
        elif final_target in ['menu_main_repair.png', 'menu_side_repair.png']:
            if kc_window.exists('repair_screen_check.png'):
                final_target = ''
        elif final_target in ['menu_top_quests.png']:
            if kc_window.exists('quests_screen_check.png'):
                wait_and_click(kc_window, 'quests_screen_check.png', expand=expand_areas('quests_screen_check')) # Go away Ooyodo
                sleep(1)
                final_target = ''
        else:
            final_target = ''

def jst_convert(time):
    """
    Function for converting the input time to JST based on the JST Offset
    specified by the user in the config.

    time - datetime object
    """
    global util_settings
    return time + datetime.timedelta(hours=util_settings['jst_offset'])

def rnavigation_chooser(options, exclude):
    """
    Helper function for rnavigation() to help choose random menu item, while
    excluding certain options such as the destination and the just-selected
    item. Returns a random item from the list of options, excluding any items
    in exclude.

    options - list of available images to click
    exclude - list of images that should not be clicked
    """
    return choice([i for i in options if i not in exclude])

def check_and_click(kc_window, pic, expand=[]):
    """
    Common sikuli action to click a pattern if it exists.

    kc_window - Sikuli window
    pic - image name (str) or Pattern object; thing to match
    expand - expand parameter to pass to rclick (see rclick's expand parameter
        for more details). Defaults to [].
    """
    if kc_window.exists(pic):
        rclick(kc_window, pic, expand)
        return True
    return False

def wait_and_click(kc_window, pic, time=5, expand=[]):
    """
    Common sikuli action to wait for a pattern until it exists, then click it.

    kc_window - Sikuli window
    pic - image name (str) or Pattern object; thing to match
    time - seconds (int); max time to wait for pic to show up. Defaults to 5.
    expand - expand parameter to pass to rclick (see rclick's expand parameter
        for more details). Defaults to [].
    """
    if time:
        kc_window.wait(pic, time)
    else:
        kc_window.wait(pic)
    rclick(kc_window, pic, expand)

class color:
    """
    Log colors
    """
    MSG = '\033[94m'
    SUCCESS = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    END = '\033[0m'

def format(msg):
    now = strftime("%Y-%m-%d %H:%M:%S")
    return "[%s] %s" % (now, msg)

def log_msg(msg):
    print "%s%s%s" % (color.MSG, format(msg), color.END)

def log_success(msg):
    print "%s%s%s" % (color.SUCCESS, format(msg), color.END)

def log_warning(msg):
    print "%s%s%s" % (color.WARNING, format(msg), color.END)

def log_error(msg):
    print "%s%s%s" % (color.ERROR, format(msg), color.END)
