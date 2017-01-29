import ConfigParser, datetime
from sikuli import *
from org.sikuli.script import *
from random import uniform, randint, choice
from time import sleep as tsleep, strftime
from re import match

Settings.OcrTextRead = True
util_settings = {}
global_regions = {}

def get_util_config():
    """Load the settings related to the util module"""
    global util_settings
    log_msg("Reading util config file!")
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

def sleep_fast():
    """
    Function for sleeping for a very short period of time. For use mainly between
    a succession of mouseclick events.
    """
    tsleep(uniform(0.2, 0.5))

def sleep(base, flex=-1):
    """
    Function for setting a random sleep time. Sleep length set by this function
    can vary from base to base * 2, or base to base + flex if flex is provided.

    base - positive int
    flex - positive int; defaults to -1 to disable
    """
    global util_settings
    if flex == -1:
        tsleep(randint(base, base * 2) + util_settings['sleep_mod'])
    else:
        tsleep(randint(base, base + flex) + util_settings['sleep_mod'])

def check_ocr(kc_region, text_ref, dir, width):
    """
    Helper function for doing the actual OCR in check_timer and check_number.
    Returns the text it's found, after some basic character fixes/replacements.

    kc_region - Sikuli region
    text_ref - image name (str) or reference Match object (returned by findAll, for example)
    dir - 'l' or 'r'; direction to search for text
    width - positive int; width (in pixels) of area where the timer text should be
    """
    if isinstance(text_ref, str):
        if dir == 'r':
            text = kc_region.find(text_ref).right(width).text().encode('utf-8')
        elif dir == 'l':
            text = kc_region.find(text_ref).left(width).text().encode('utf-8')
    elif isinstance(text_ref, Match):
        if dir == 'r':
            text = text_ref.right(width).text().encode('utf-8')
        elif dir == 'l':
            text = text_ref.left(width).text().encode('utf-8')
    # Replace characters
    text = (
        text.replace('O', '0').replace('o', '0').replace('D', '0')
        .replace('Q', '0').replace('@', '0').replace('l', '1').replace('I', '1')
        .replace('[', '1').replace(']', '1').replace('|', '1').replace('!', '1')
        .replace('Z', '2').replace('S', '5').replace('s', '5').replace('$', '5')
        .replace('B', '8').replace(':', '8').replace(' ', '').replace('-', '')
    )
    return text

def check_timer(kc_region, timer_ref, dir, width, attempt_limit=0):
    """
    Function for grabbing valid Kancolle timer readings (##:##:## format).
    Attempts to fix erroneous OCR reads and repeats readings until a valid
    timer value is returned. Returns timer string in ##:##:## format.

    kc_region - Sikuli region
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
        timer = check_ocr(kc_region, timer_ref, dir, width)
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

def check_number(kc_region, number_ref, dir, width, attempt_limit=0):
    """
    Function for grabbing numbers from the kancolle-auto screen.
    Attempts to fix erroneous OCR reads and repeats readings until a valid
    number is returned. Returns found number value.

    kc_region - Sikuli region
    number_ref - image name (str) or reference Match object (returned by findAll, for example)
    dir - 'l' or 'r'; direction to search for number
    width - positive int; width (in pixels) of area where the number should be
    attempt_limit = how many times the OCR reads should repeat before failing
    """
    ocr_matching = True
    attempt = 0
    while ocr_matching:
        attempt += 1
        number = check_ocr(kc_region, number_ref, dir, width)
        m = match(r'^\d+$', number)
        if m:
            # OCR reading checks out; return number
            ocr_matching = False
            return int(number)
        # If we got this far, the number reading is invalid.
        # If an attempt_limit is set and met, return 0
        if attempt_limit != 0 and attempt == attempt_limit:
            return 0
        # Otherwise, try again!
        log_warning("Got invalid number (%s)... trying again!" % number)
        sleep(1)

def rejigger_mouse(kc_region, x1, x2, y1, y2, find_position=False):
    """
    Function for rejiggering the mouse position when required, usually to wake
    the screen up or move the mouse out of the way of buttons. The function
    will throw the mouse to around where the kanmasu portrait would be on the
    main screen. Thanks to @minh6a for working on this!

    kc_region - Sikuli window
    x1, x2 - random value range for x-coord
    y1, y2 - random value range for y-coord
    """
    global util_settings

    # If the screen dimensions are not set, grab it using Sikuli's Screen class
    if 'screen_x' not in util_settings or 'screen_y' not in util_settings:
        temp_screen = Screen().getBounds()
        util_settings['screen_x'] = temp_screen.width
        util_settings['screen_y'] = temp_screen.height
    if find_position:
        temp_game = kc_region.getLastMatch()
        # Define upper-left corner of game screen
        util_settings['game_x'] = temp_game.x - 99
        util_settings['game_y'] = temp_game.y
        # Define global regions
        global_regions['game'] = Region(util_settings['game_x'], util_settings['game_y'], 800, 480)
        global_regions['next'] = Region(util_settings['game_x'] + 700, util_settings['game_y'] + 380, 100, 100)
        global_regions['expedition_flag'] = Region(util_settings['game_x'] + 490, util_settings['game_y'], 60, 55)
        global_regions['fleet_flags_main'] = Region(util_settings['game_x'] + 80, util_settings['game_y'] + 100, 200, 35)
        global_regions['fleet_flags_sec'] = Region(util_settings['game_x'] + 340, util_settings['game_y'] + 100, 140, 35)
        global_regions['check_resupply'] = Region(util_settings['game_x'] + 465, util_settings['game_y'] + 155, 65, 285)
        global_regions['check_morale'] = Region(util_settings['game_x'] + 500, util_settings['game_y'] + 135, 22, 290)
        global_regions['check_damage'] = Region(util_settings['game_x'] + 460, util_settings['game_y'] + 135, 48, 300)
        global_regions['check_damage_combat'] = Region(util_settings['game_x'] + 290, util_settings['game_y'] + 185, 70, 280)
        global_regions['formation_line_ahead'] = Region(util_settings['game_x'] + 390, util_settings['game_y'] + 160, 120, 50)
        global_regions['formation_double_line'] = Region(util_settings['game_x'] + 520, util_settings['game_y'] + 160, 120, 50)
        global_regions['formation_diamond'] = Region(util_settings['game_x'] + 650, util_settings['game_y'] + 160, 120, 50)
        global_regions['formation_echelon'] = Region(util_settings['game_x'] + 460, util_settings['game_y'] + 320, 120, 50)
        global_regions['formation_line_abreast'] = Region(util_settings['game_x'] + 590, util_settings['game_y'] + 320, 120, 50)
        global_regions['formation_combinedfleet_1'] = Region(util_settings['game_x'] + 420, util_settings['game_y'] + 150, 160, 50)
        global_regions['formation_combinedfleet_2'] = Region(util_settings['game_x'] + 580, util_settings['game_y'] + 150, 160, 50)
        global_regions['formation_combinedfleet_3'] = Region(util_settings['game_x'] + 420, util_settings['game_y'] + 280, 160, 50)
        global_regions['formation_combinedfleet_4'] = Region(util_settings['game_x'] + 580, util_settings['game_y'] + 280, 160, 50)
        # global_regions['quest_category'] = Region(util_settings['game_x'] + 140, util_settings['game_y'] + 110, 65, 340)
        global_regions['quest_status'] = Region(util_settings['game_x'] + 710, util_settings['game_y'] + 110, 65, 340)

    # Generate random coordinates
    if 'game_x' not in util_settings or 'game_y' not in util_settings:
        rand_x = kc_region.x + randint(x1, x2)
        rand_y = kc_region.y + randint(y1, y2)
    else:
        rand_x = util_settings['game_x'] + randint(x1, x2)
        rand_y = util_settings['game_y'] + randint(y1, y2)

    # Make sure that the randomly generated coordinates are not outside the
    # screen's boundaries
    if rand_x > util_settings['screen_x']:
        rand_x = util_settings['screen_x'] - 1
    if rand_y > util_settings['screen_y']:
        rand_y = util_settings['screen_y'] - 1

    # Rejigger mouse
    kc_region.mouseMove(Location(rand_x, rand_y))

def expand_areas(target):
    """
    Function to return pre-defined click expand areas. Returns list of 4 ints
    (see rclick function for more details).

    target - str; which list to return
    """
    if target == 'expedition_finish':
        return [-350, 200, 0, 400]
    elif target == 'fleet_id':
        return [-6, 6, -7, 7]
    elif target == 'next':
        return [-600, 0, -400, 0]
    elif target == 'compass':
        return [-250, 400, -200, 200]
    elif target == 'node_select':
        return[-5, 5, -5, 5]
    elif target == 'quests_screen_check':
        return [-40, 700, -50, 300]
    elif target == 'quest_bar':
        return [-160, 340, -40, 5]
    elif target == 'quests_navigation':
        return [-10, 10, -5, 5]
    elif target == 'quest_completed':
        return [-580, 25, -25, 25]
    elif target == 'pvp_row':
        return [-495, 45, -5, 35]
    elif target == 'repair_list':
        return [-325, 35, -10, 6]

def rnavigation(kc_region, destination, settings, max=0):
    """
    Random navigation function. Randomly wanders through menu items a number
    of times before reaching its destination.

    kc_region - Sikuli region
    destination - 'home', 'refresh_home', 'fleetcomp', 'resupply', 'equip',
        'repair', 'development'; valid final destinations
    max - custom # of side-steps. Defaults to 0 to default to Paranoia setting
    """
    global util_settings
    # Look at all the things we can click!
    menu_main_options = ['menu_main_sortie.png', 'menu_main_fleetcomp.png', 'menu_main_resupply.png',
                         'menu_main_equip.png', 'menu_main_repair.png', 'menu_main_development.png']
    menu_top_options = ['menu_top_inventory.png', 'menu_top_quests.png']
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
    if kc_region.exists('menu_main_sortie.png'):
        current_location = 'home'
    elif kc_region.exists('menu_side_home.png'):
        current_location = 'sidemenu'
    elif kc_region.exists('menu_top_home.png'):
        current_location = 'topmenu'
    else:
        current_location = 'other'
    # Random navigations, depending on where we are, and where we want to go
    rejigger_mouse(kc_region, 370, 770, 100, 400)
    if current_location == 'home':
        # Starting from home screen
        if destination == 'home':
            # Already at home
            pass
        elif destination == 'refresh_home':
            # Refresh home
            log_msg("Refreshing home with %d or less sidestep(s)!" % (evade_count))
            rchoice = rnavigation_chooser(menu_top_options + menu_main_options, [])
            wait_and_click(kc_region, rchoice)
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
                        wait_and_click(kc_region, rchoice)
                        sleep(2)
                        evade_count -= 1
                    final_target = 'menu_side_home.png'
        elif destination in ['combat', 'expedition', 'pvp']:
            # Go to a sortie menu screen
            log_msg("Navigating to %s menu with %d sidestep(s)!" % (destination, evade_count))
            wait_and_click(kc_region, 'menu_main_sortie.png')
            rejigger_mouse(kc_region, 50, 750, 0, 100)
            sleep(2)
            if evade_count == 0:
                final_target = 'sortie_' + destination + '.png'
            else:
                rchoice = rnavigation_chooser(menu_sortie_options, ['sortie_' + destination + '.png'])
                wait_and_click(kc_region, rchoice)
                sleep(2)
                rejigger_mouse(kc_region, 50, 750, 0, 100)
                evade_count -= 1
                while evade_count > 0:
                    if rchoice.startswith('sortie_top'):
                        rchoice = rnavigation_chooser(menu_sortie_top_options, [rchoice, 'sortie_top_' + destination + '.png'])
                    else:
                        rchoice = rnavigation_chooser(menu_sortie_top_options, ['sortie_top_' + rchoice[7:], 'sortie_top_' + destination + '.png'])
                    wait_and_click(kc_region, rchoice)
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
                wait_and_click(kc_region, rchoice)
                sleep(2)
                evade_count -= 1
                while evade_count > 0:
                    if rchoice.startswith('menu_top'):
                        # Went to another top menu item. Go straight to target to make things simple
                        final_target = 'menu_top_quests.png'
                        evade_count = 0
                    else:
                        rchoice = rnavigation_chooser(menu_side_options, [])
                        wait_and_click(kc_region, rchoice)
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
                wait_and_click(kc_region, rchoice)
                sleep(2)
                evade_count -= 1
                while evade_count > 0:
                    if rchoice.startswith('menu_main'):
                        rchoice = rnavigation_chooser(menu_side_options, ['menu_side_' + rchoice[10:], 'sortie_top_' + destination + '.png'])
                    else:
                        rchoice = rnavigation_chooser(menu_side_options, [rchoice, 'sortie_top_' + destination + '.png'])
                    wait_and_click(kc_region, rchoice)
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
                    wait_and_click(kc_region, rchoice)
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
                rchoice = rnavigation_chooser(menu_side_options + ['menu_top_inventory.png'], [])
                wait_and_click(kc_region, rchoice)
                sleep(2)
                evade_count -= 1
                while evade_count > 0:
                    if rchoice.startswith('menu_top'):
                        # Went to another top menu item. Go straight to target to make things simple
                        final_target = 'menu_top_quests.png'
                        evade_count = 0
                    else:
                        rchoice = rnavigation_chooser(menu_side_options + ['menu_top_inventory.png'], [])
                        wait_and_click(kc_region, rchoice)
                        sleep(2)
                        evade_count -= 1
                final_target = 'menu_top_quests.png'
        elif destination in ['combat', 'expedition', 'pvp']:
            # These are unreachable from here... unless we're already at sortie screen
            if kc_region.exists('sortie_top_combat.png') or kc_region.exists('sortie_top_pvp.png') or kc_region.exists('sortie_top_expedition.png'):
                # If we're already at sortie screen, ignore evades
                final_target = 'sortie_top_' + destination + '.png'
            else:
                log_error("Unreachable destination %s from current location!" % destination)
                raise
        else:
            # Go to another main menu item screen
            log_msg("Navigating to %s screen with %d sidestep(s)!" % (destination, evade_count))
            if evade_count == 0:
                final_target = 'menu_side_' + destination + '.png'
            else:
                rchoice = rnavigation_chooser(menu_side_options, ['menu_side_' + destination + '.png'])
                while evade_count > 0:
                    rchoice = rnavigation_chooser(menu_side_options, [rchoice, 'menu_side_' + destination + '.png'])
                    wait_and_click(kc_region, rchoice)
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
    while_count = 0
    while final_target != '':
        # In while loop so that if the button has to be pressed again for some
        # reason, it'll do it. Only works for certain destinations.
        wait_and_click(kc_region, final_target, 5)
        sleep(2)
        # Always reset mouse after reaching destination
        rejigger_mouse(kc_region, 50, 500, 0, 100)
        # If one of these targets, check to see if we're actually there.
        if final_target in ['menu_top_home.png', 'menu_side_home.png']:
            if kc_region.exists('menu_main_sortie.png'):
                final_target = ''
        elif final_target in ['sortie_expedition.png', 'sortie_top_expedition.png']:
            if kc_region.exists('expedition_screen_ready.png'):
                final_target = ''
        elif final_target in ['menu_main_resupply.png', 'menu_side_resupply.png']:
            if kc_region.exists('resupply_screen.png'):
                final_target = ''
        elif final_target in ['menu_main_repair.png', 'menu_side_repair.png']:
            if kc_region.exists('repair_screen_check.png'):
                final_target = ''
        elif final_target in ['menu_top_quests.png']:
            if kc_region.exists('quests_screen_check.png'):
                wait_and_click(kc_region, 'quests_screen_check.png', expand=expand_areas('quests_screen_check'))  # Go away Ooyodo
                sleep_fast()
                final_target = ''
        else:
            final_target = ''
        while_count += 1
        if while_count > 4:
            raise FindFailed("rnavigation looping too much!")

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

def check_and_click(kc_region, pic, expand=[]):
    """
    Common sikuli action to click a pattern if it exists.

    kc_region - Sikuli region
    pic - image name (str) or Pattern object; thing to match
    expand - expand parameter to pass to rclick (see rclick's expand parameter
        for more details). Defaults to [].
    """
    if kc_region.exists(pic):
        kc_region.click(pattern_generator(kc_region, pic, expand, 'prematched'))
        return True
    return False

def wait_and_click(kc_region, pic, time=5, expand=[]):
    """
    Common sikuli action to wait for a pattern until it exists, then click it.

    kc_region - Sikuli region
    pic - image name (str) or Pattern object; thing to match
    time - seconds (int); max time to wait for pic to show up. Defaults to 5.
    expand - expand parameter to pass to rclick (see rclick's expand parameter
        for more details). Defaults to [].
    """
    if time:
        kc_region.wait(pattern_generator(kc_region, pic, expand), time)
    else:
        kc_region.wait(pattern_generator(kc_region, pic, expand))
    kc_region.click(pattern_generator(kc_region, pic, expand))

def pattern_generator(kc_region, pic, expand=[], mod=''):
    """
    Function for generating Sikuli Pattern with randomized click locations.
    If expand is not provided the click location will be within the
    image/Pattern's area. If expand is provided, the click location will be in
    the area expanded relative to the center of the image/Pattern.

    pic - image name (str) or Pattern object to match/click
    expand - list containing custom click boundaries in [left, right, top, bottom]
        directions. Values should all be (int)s, and relative to the center of
        the matched Pattern. Defaults to [] to default to Pattern area.
    mod - currently only for dictating whether or not to use a previous match
        for dimension generation (speeds up check_and_click)
    """
    if len(expand) == 0:
        # This slows down the click actions, but it looks for the pattern and
        # finds the size of the image from the resulting Pattern object.
        if mod == 'prematched':
            m = match(r'M\[\d+\,\d+ (\d+)x(\d+)\]', str(kc_region.getLastMatch()))
        else:
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
            pic = Pattern(pic).targetOffset(randint(expand[0], expand[1]), randint(expand[2], expand[3]))
        elif isinstance(pic, Pattern):
            pic = pic.targetOffset(randint(expand[0], expand[1]), randint(expand[2], expand[3]))
    return pic

# Refresh kancolle
def refresh_kancolle(kc_region, settings, e):
    if settings['basic_recovery'] is True:
        if esc_recovery(kc_region, settings, "recovery"):
            return True
    if kc_region.exists('catbomb.png') and settings['recovery_method'] != 'None':
        if settings['recovery_method'] == 'Browser':
            # Recovery steps if using a webbrowser with no other plugins
            # Assumes that 'F5' is a valid keyboard shortcut for refreshing
            type(Key.F5)
        elif settings['recovery_method'] == 'KC3':
            # Recovery steps if using KC3 in Chrome
            type(Key.F5)
            sleep(1)
            type(Key.SPACE)  # In case Exit Confirmation is checked in KC3 Settings
            sleep(1)
            type(Key.TAB)  # Tab over to 'Start Anyway' button
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
            type(Key.TAB)  # In case Exit Confirmation is checked in EO Settings
            sleep(1)
            type(Key.SPACE)
        # The Game Start button is there and active, so click it to restart
        sleep(3)
        rejigger_mouse(kc_region, 370, 770, 10, 200)
        sleep(3)
        while not kc_region.exists(Pattern('game_start.png').similar(0.999)):
            sleep(1)
        check_and_click(kc_region, 'game_start.png')
        sleep(5)
        log_success("Catbomb recovery successful! Re-initializing kancolle-auto!")
        return True
    # If we get to this point, none of the above recovery attempts worked
    log_error("Non-catbomb script crash, or catbomb script crash w/ unsupported Viewer!")
    print e
    raise

def while_count_checker(kc_region, settings, while_count):
    if while_count > 10:
        raise FindFailed("Something is wrong... looping too much!")
    if while_count > 8:
        esc_recovery(kc_region, settings)

def esc_recovery(kc_region, settings, context="loop"):
    if settings['basic_recovery'] is True:
        type(Key.ESC)
        if context == "recovery":
            if kc_region.exists(Pattern('menu_main_home.png').exact()):
                sleep(1)
                log_success("Basic recovery successful! Re-initializing kancolle-auto!")
                return True
        else:
            return True

def debug_find(file, target_program, similarity=0.8):
    """
    Debug function. Uncomment the line in kancolle_auto.py referencing this function
    to use. Finds specified file in target_program window and prints the resulting
    Sikuli match file. Useful for checking to see if an image you've generated
    for matching works properly
    """
    myApp = App.focus(target_program)
    target_window = myApp.focusedWindow()
    match = target_window.find(Pattern(file).similar(similarity))
    print ""
    print ""
    print "+  Sikuli match object for '%s' in window '%s'" % (file, target_program)
    print "+    with minimum similarity of %s:" % similarity
    print match
    print ""
    print ""
    raise SystemExit


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
