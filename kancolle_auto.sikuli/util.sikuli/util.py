from sikuli import *
from random import uniform, randint, choice
from time import sleep as tsleep, strftime
from re import match

Settings.OcrTextRead = True

# Custom sleep() function to make the sleep period more variable. Maximum
# sleep length is 2 * sec
def sleep(sec):
    tsleep(uniform(sec, sec * 2))

# Custom function to get some pseudo-random value. Here in case variability is
# needed in a non-sleep() function. Maximum return is base + flex.
# value is 2 * integer
def get_rand(base, flex):
    return randint(base, base + flex)

# Custom function to get timer value of Kancolle (in ##:##:## format). Attempts
# to fix values in case OCR grabs the wrong characters.
def check_timer(kc_window, timer_img, width):
    timer_raw = find(timer_img).right(width).text()
    timer = list(timer_raw)
    timer[2] = ':'
    timer[5] = ':'
    timer = ''.join(timer)
    timer = (
        timer.replace('l', '1').replace('I', '1').replace('[', '1').replace(']', '1')
        .replace('|', '1').replace('!', '1').replace('O', '0').replace('o', '0')
        .replace('D', '0').replace('Q', '0').replace('@', '0').replace('S', '5')
        .replace('s', '5').replace('$', '5').replace('B', '8')
    )
    return timer

# Random Click action. Offsets the mouse into a random point within the
# matching image/pattern before clicking.
def rclick(kc_window, pic):
    # This slows down the click actions, but it looks for the pattern and
    # finds the size of the image from the resulting Pattern object.
    m = match(r'M\[\d+\,\d+ (\d+)x(\d+)\]', str(find(pic)))
    if m:
        # If a match is found and the x,y sizes can be ascertained, generate
        # the random offsets. Otherwise, just click the damn middle.
        x_width = int(m.group(1)) / 2
        y_height = int(m.group(2)) / 2
        if isinstance(pic, str):
            pic = Pattern(pic).targetOffset(int(uniform(-x_width, x_width)), int(uniform(-y_height, y_height)))
        elif isinstance(pic, Pattern):
            pic = pic.targetOffset(int(uniform(-x_width, x_width)), int(uniform(-y_height, y_height)))
    kc_window.click(pic)

# Random navigation actions.
def rnavigation(kc_window, destination, max=3):
    # Look at all the things we can click!
    menu_main_options = ['menu_main_sortie.png', 'menu_main_fleetcomp.png', 'menu_main_resupply.png',
        'menu_main_equip.png', 'menu_main_repair.png', 'menu_main_development.png']
    menu_top_options = ['menu_top_profile.png', 'menu_top_encyclopedia.png', 'menu_top_inventory.png',
        'menu_top_furniture.png', 'menu_top_shop.png', 'menu_top_quests.png']
    menu_side_options = ['menu_side_fleetcomp.png', 'menu_side_resupply.png', 'menu_side_equip.png',
        'menu_side_repair.png', 'menu_side_development.png']
    menu_sortie_options = ['sortie_combat.png', 'sortie_expedition.png', 'sortie_pvp.png']
    menu_sortie_top_options = ['sortie_top_combat.png', 'sortie_top_expedition.png', 'sortie_top_pvp.png']
    menu_loop_count = randint(0, max)
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
    if current_location == 'home':
        # Starting from home screen
        if destination == 'home':
            # Already at home
            pass
        elif destination == 'refresh_home':
            # Refresh home
            log_msg("Refreshing home with %d or less sidesteps!" % (menu_loop_count))
            rchoice = rnavigation_chooser(menu_top_options + menu_main_options, [])
            rclick(kc_window, rchoice)
            sleep(2)
            if rchoice.startswith('menu_top'):
                # At top menu item; hit the home button until we get home (Akashi/Ooyodo, go away)
                while not kc_window.exists('menu_main_sortie.png'):
                    wait_and_click(kc_window, 'menu_top_home.png', 10)
                    sleep(2)
            elif rchoice.startswith('menu_main'):
                if menu_loop_count == 0:
                    rclick(kc_window, 'menu_side_home.png')
                else:
                    rchoice = rnavigation_chooser(menu_side_options, ['menu_side' + rchoice[10:]])
                    while menu_loop_count > 0:
                        rchoice = rnavigation_chooser(menu_side_options, [rchoice])
                        rclick(kc_window, rchoice)
                        sleep(2)
                        menu_loop_count -= 1
                    rclick(kc_window, 'menu_side_home.png')
        elif destination in ['combat', 'expedition']:
            # Go to combat and expedition menu
            log_msg("Navigating to %s menu with %d sidesteps!" % (destination, menu_loop_count))
            rclick(kc_window, 'menu_main_sortie.png')
            sleep(2)
            if menu_loop_count == 0:
                wait_and_click(kc_window, 'sortie_' + destination + '.png')
            else:
                rchoice = rnavigation_chooser(menu_sortie_options, ['sortie_' + destination + '.png'])
                rclick(kc_window, rchoice)
                menu_loop_count -= 1
                while menu_loop_count > 0:
                    if rchoice.startswith('sortie_top'):
                        rchoice = rnavigation_chooser(menu_sortie_top_options, [rchoice, 'sortie_top_' + destination + '.png'])
                    else:
                        rchoice = rnavigation_chooser(menu_sortie_top_options, ['sortie_top_' + rchoice[7:], 'sortie_top_' + destination + '.png'])
                    rclick(kc_window, rchoice)
                    sleep(2)
                    menu_loop_count -= 1
                rclick(kc_window, 'sortie_top_' + destination + '.png')
        else:
            # Go to and side menu sub screen
            log_msg("Navigating to %s screen with %d sidesteps!" % (destination, menu_loop_count))
            if menu_loop_count == 0:
                rclick(kc_window, 'menu_main_' + destination + '.png')
            else:
                rchoice = rnavigation_chooser(menu_main_options, ['menu_main_' + destination + '.png'])
                rclick(kc_window, rchoice)
                menu_loop_count -= 1
                while menu_loop_count > 0:
                    if rchoice.startswith('menu_main_'):
                        rchoice = rnavigation_chooser(menu_side_options, ['menu_side' + rchoice[10:], 'sortie_top_' + destination + '.png'])
                    else:
                        rchoice = rnavigation_chooser(menu_side_options, [rchoice, 'sortie_top_' + destination + '.png'])
                    rclick(kc_window, rchoice)
                    sleep(2)
                    menu_loop_count -= 1
                rclick(kc_window, 'menu_side_' + destination + '.png')
        sleep(2)
    if current_location == 'sidemenu':
        # Starting from a main menu item screen
        if destination == 'home' or destination == 'refresh_home':
            # Go or refresh home
            log_msg("Going home with %d or less sidesteps!" % (menu_loop_count))
            if menu_loop_count == 0:
                rclick(kc_window, 'menu_side_home.png')
            else:
                rchoice = rnavigation_chooser(menu_top_options + menu_side_options, [])
                while menu_loop_count > 0:
                    rchoice = rnavigation_chooser(menu_top_options + menu_side_options, [rchoice])
                    rclick(kc_window, rchoice)
                    sleep(2)
                    menu_loop_count -= 1
                    if rchoice.startswith('menu_top'):
                        # At top menu item; hit the home button until we get home (Akashi/Ooyodo, go away)
                        while not kc_window.exists('menu_main_sortie.png'):
                            wait_and_click(kc_window, 'menu_top_home.png', 10)
                            sleep(2)
                        # This takes us back to home immediately, so no more random menus
                        menu_loop_count = 0
                    else:
                        # Still at side menu item, so continue as normal
                        if menu_loop_count == 0:
                            # Unless that was the last random menu item; then go home
                            rclick(kc_window, 'menu_side_home.png')
        else:
            # Go to another main menu item screen
            log_msg("Navigating to %s screen with %d sidesteps!" % (destination, menu_loop_count))
            if menu_loop_count == 0:
                rclick(kc_window, 'menu_side_' + destination + '.png')
            else:
                rchoice = rnavigation_chooser(menu_side_options, ['menu_side_' + destination + '.png'])
                while menu_loop_count > 0:
                    rchoice = rnavigation_chooser(menu_side_options, [rchoice, 'menu_side_' + destination + '.png'])
                    rclick(kc_window, rchoice)
                    menu_loop_count -= 1
                    sleep(2)
                rclick(kc_window, 'menu_side_' + destination + '.png')
        sleep(2)
    if current_location == 'topmenu':
        # Starting from top menu item. Theoretically, the script should never
        # attempt to go anywhere but home from here
        if destination in ['home', 'refresh_home']:
            log_msg("Going home!")
            # At top menu item; hit the home button until we get home (Akashi/Ooyodo, go away)
            while not kc_window.exists('menu_main_sortie.png'):
                wait_and_click(kc_window, 'menu_top_home.png', 10)
                sleep(2)

# Helper function for random navigator for choosing random items from an array
def rnavigation_chooser(options, exclude):
    return choice([i for i in options if i not in exclude])

# common Sikuli actions
def check_and_click(kc_window, pic):
    if kc_window.exists(pic):
        rclick(kc_window, pic)
        #kc_window.click(pic)
        return True
    return False

def wait_and_click(kc_window, pic, time=0):
    if time:
        kc_window.wait(pic, time)
    else:
        kc_window.wait(pic)
    rclick(kc_window, pic)
    #kc_window.click(pic)

# log colors
class color:
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
