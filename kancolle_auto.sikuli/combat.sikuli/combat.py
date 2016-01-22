# Combat list.
from sikuli import *
import datetime
from random import randint, choice
from util import *

Settings.OcrTextRead = True
Settings.MinSimilarity = 0.8

class Combat:
    def __init__(self, kc_window, settings):
        self.next_sortie_time = datetime.datetime.now()
        self.kc_window = kc_window
        self.area_num = settings['combat_area']
        self.subarea_num = settings['combat_subarea']
        self.area_pict = 'combat_area_%d.png' % settings['combat_area']
        self.subarea_pict = 'combat_panel_%d-%d.png' % (settings['combat_area'], settings['combat_subarea'])
        self.nodes = settings['nodes']
        self.formations = settings['formations']
        self.night_battles = settings['night_battles']
        self.retreat_limit = settings['retreat_limit']
        self.repair_limit = settings['repair_limit']
        self.repair_time_limit = settings['repair_time_limit']
        self.repair_timers = []
        self.check_fatigue = settings['check_fatigue']
        self.port_check = settings['port_check']
        self.damage_counts = [0, 0, 0]

    def tally_damages(self):
        dmg_similarity = 0.75
        log_msg("Checking fleet condition...")
        self.damage_counts = [0, 0, 0]
        # Tally light damages (in different fatigue states, as well)
        if self.kc_window.exists(Pattern('dmg_light.png').similar(dmg_similarity)):
            for i in self.kc_window.findAll(Pattern('dmg_light.png').similar(dmg_similarity)):
                self.damage_counts[0] += 1
        # Tally moderate damages (in different fatigue states, as well)
        if self.kc_window.exists(Pattern('dmg_moderate.png').similar(dmg_similarity)):
            for i in self.kc_window.findAll(Pattern('dmg_moderate.png').similar(dmg_similarity)):
                self.damage_counts[1] += 1
        # Tally critical damages (in different fatigue states, as well)
        if self.kc_window.exists(Pattern('dmg_critical.png').similar(dmg_similarity)):
            for i in self.kc_window.findAll(Pattern('dmg_critical.png').similar(dmg_similarity)):
                self.damage_counts[2] += 1
        log_msg("Light damage: %d; moderate damage: %d; critical damage: %d" % (self.damage_counts[0], self.damage_counts[1], self.damage_counts[2]))
        return self.damage_counts

    # Return number of ships damaged above threshold; relies on tally_damages()
    # for a reliable count
    def count_damage_above_limit(self, limit_type):
        if limit_type == 'retreat':
            limit = self.retreat_limit
        elif limit_type == 'repair':
            limit = self.repair_limit
        count = 0
        for i, dmg_count in enumerate(self.damage_counts):
            if i >= limit:
                count += dmg_count
        return count

    def fatigue_check(self):
        log_msg("Checking fleet morale!")
        if self.kc_window.exists(Pattern('fatigue_high.png').similar(0.98)):
            log_warning("Ship(s) with high fatigue found!")
            return 24
        elif self.kc_window.exists(Pattern('fatigue_med.png').similar(0.98)):
            log_warning("Ship(s) with medium fatigue found!")
            return 12
        else:
            log_success("Ships have good morale!")
            return None

    # Navigate to Sortie menu and click through sortie!
    def go_sortie(self):
        rnavigation(self.kc_window, 'combat', 2)
        wait_and_click(self.kc_window, self.area_pict)
        # If an EO is specified, press the red EO arrow on the right
        if self.subarea_num > 4:
            wait_and_click(self.kc_window, 'combat_panel_eo.png')
            rejigger_mouse(self.kc_window, 50, 750, 0, 100)
        wait_and_click(self.kc_window, self.subarea_pict)
        sleep(2)
        # Check if port is filled, if necessary
        if self.port_check:
            if self.kc_window.exists('combat_start_warning_shipsfull.png'):
                log_warning("Port is full! Please make some room for new ships! Sortie cancelled!")
                self.next_sortie_time_set(0, 15)
                return self.damage_counts
        wait_and_click(self.kc_window, 'decision.png')
        sleep(1)
        rejigger_mouse(self.kc_window, 50, 750, 0, 400)
        # Taly damages
        self.tally_damages()
        # Check for resupply needs
        if (self.kc_window.exists('resupply_alert.png') or self.kc_window.exists('resupply_red_alert.png')):
            log_warning("Fleet 1 needs resupply!")
            return self.damage_counts
        # Check fleet damage state
        if self.damage_counts[2] > 0:
            log_warning("Ship(s) in critical condition! Sortie cancelled!")
            return self.damage_counts
        if self.count_damage_above_limit('repair') > 0:
            log_warning("Ships (%d) in condition below repair threshold! Sortie cancelled!" % self.count_damage_above_limit('repair'))
            return self.damage_counts
        # Check fleet morale, if necessary
        if self.check_fatigue:
            fatigue_timer = self.fatigue_check()
            if fatigue_timer:
                log_warning("Fleet is fatigued! Sortie cancelled!")
                self.next_sortie_time_set(0, fatigue_timer)
                return self.damage_counts
        if not self.kc_window.exists(Pattern('combat_start_disabled.png').exact()):
            log_success("Commencing sortie!")
            wait_and_click(self.kc_window, 'combat_start.png')
            sortie_underway = True
            nodes_run = 0
            while sortie_underway:
                # Begin loop that checks for combat, formation select, night
                # battle prompt, or post-battle report screen
                self.loop_pre_combat(nodes_run)
                # Ended on resource nodes. Leave sortie.
                if self.kc_window.exists('next_alt.png'):
                    log_success("Sortie complete!")
                    check_and_click(self.kc_window, 'next_alt.png', expand_areas('next'))
                    sortie_underway = False
                    return self.damage_counts
                # If night battle prompt, proceed based on node and user config
                if self.kc_window.exists('combat_nb_retreat.png'):
                    if self.night_battles[nodes_run] == 'True':
                        # Commence and sleep through night battle
                        log_success("Commencing night battle!")
                        check_and_click(self.kc_window, 'combat_nb_fight.png')
                        while not self.kc_window.exists('next.png'):
                            sleep(10)
                    else:
                        # Decline night battle
                        log_msg("Declining night battle!")
                        check_and_click(self.kc_window, 'combat_nb_retreat.png')
                # Click through post-battle report
                wait_and_click(self.kc_window, 'next.png', 30, expand_areas('next'))
                sleep(3)
                # Tally damages at post-battle report screen
                self.tally_damages()
                wait_and_click(self.kc_window, 'next.png', 30, expand_areas('next'))
                sleep(3)
                # Check to see if we're at combat retreat/continue screen or
                # item/ship reward screen(s)
                if not self.kc_window.exists('combat_retreat.png'):
                    sleep(3)
                    if not (self.kc_window.exists('menu_main_sortie.png') or self.kc_window.exists('combat_flagship_dmg.png')):
                        wait_and_click(self.kc_window, 'next_alt.png', 20, expand_areas('next'))
                        sleep(5)
                        if check_and_click(self.kc_window, 'next_alt.png', expand_areas('next')):
                            sleep(3)
                if self.kc_window.exists('combat_flagship_dmg.png'):
                    wait_and_click(self.kc_window, 'combat_flagship_dmg.png')
                    sleep(3)
                rejigger_mouse(self.kc_window, 370, 770, 100, 400)
                # Check to see if we're back at Home screen
                if self.kc_window.exists('menu_main_sortie.png'):
                    log_success("Sortie complete!")
                    sortie_underway = False
                    return self.damage_counts
                # We ran a node, so increase the counter
                nodes_run += 1
                # Set next sortie time to soon in case we have no failures or
                # additional nodes
                self.next_sortie_time_set(0, randint(1, 4))
                # If required number of nodes have been run, fall back
                if nodes_run >= self.nodes:
                    log_msg("Ran the required number of nodes. Falling back!")
                    wait_and_click(self.kc_window, 'combat_retreat.png', 30)
                    sortie_underway = False
                    return self.damage_counts
                # If fleet is damaged, fall back
                if self.count_damage_above_limit('retreat') > 0 or self.damage_counts[2] > 0:
                    log_warning("Ship(s) in condition at or below retreat threshold! Ceasing sortie!")
                    wait_and_click(self.kc_window, 'combat_retreat.png', 30)
                    sortie_underway = False
                    return self.damage_counts
                sleep(3)
                wait_and_click(self.kc_window, 'combat_nextnode.png', 30)
        else:
            if self.kc_window.exists('combat_nogo_repair.png'):
                log_warning("Cannot sortie due to ships under repair!")
                self.next_sortie_time_set(0, randint(5, 10))
                # Expand on this so it goes to repair menu and recheck?
            elif self.kc_window.exists('combat_nogo_resupply.png'):
                log_warning("Cannot sortie due to ships needing resupply!")
        return self.damage_counts

    def loop_pre_combat(self, nodes_run):
        # Check for compass, formation select, night battle prompt, or
        # post-battle report
        while not (self.kc_window.exists('compass.png')
            or self.kc_window.exists(Pattern('formation_%s.png' % self.formations[nodes_run]).similar(0.95))
            or self.kc_window.exists('combat_nb_retreat.png')
            or self.kc_window.exists('next.png')
            or self.kc_window.exists('next_alt.png')
            or self.kc_window.exists('catbomb.png')):
            sleep(2)
        # If compass, press it
        if check_and_click(self.kc_window, 'compass.png', expand_areas('compass')):
            # Now check for formation select, night battle prompt, or
            # post-battle report
            log_msg("Spinning compass!")
            rejigger_mouse(self.kc_window, 50, 350, 0, 150)
            # Restart this loop in case there's another compass coming up
            sleep(6)
            self.loop_pre_combat(nodes_run)
        # If formation select, select formation based on user config
        elif check_and_click(self.kc_window, Pattern('formation_%s.png' % self.formations[nodes_run]).similar(0.95)):
            # Now check for night battle prompt or post-battle report
            log_msg("Selecting fleet formation!")
            rejigger_mouse(self.kc_window, 50, 750, 0, 150)
            sleep(10)
            self.loop_post_formation()
        # Check for catbomb
        if self.kc_window.exists('catbomb.png'):
            raise FindFailed('Catbombed during sortie :(')

    def loop_post_formation(self):
        while not (self.kc_window.exists('combat_nb_retreat.png')
            or self.kc_window.exists('next.png')
            or self.kc_window.exists('next_alt.png')
            or self.kc_window.exists('catbomb.png')):
            sleep(2)
        # Check for catbomb
        if self.kc_window.exists('catbomb.png'):
            raise FindFailed('Catbombed during sortie :(')

    # Navigate to repair menu and repair any ship above damage threshold. Sets
    # next sortie time accordingly
    def go_repair(self):
        empty_docks = 0
        self.repair_timers = []
        rnavigation(self.kc_window, 'repair')
        # Are there any pre-existing repairs happening?
        if self.kc_window.exists(Pattern('repair_timer_alt.png').similar(0.5)):
            for i in self.kc_window.findAll(Pattern('repair_timer_alt.png').similar(0.5)):
                repair_timer = check_timer(self.kc_window, i, 'l', 100)
                timer = self.timer_end(int(repair_timer[0:2]), int(repair_timer[3:5]) - 1)
                self.repair_timers.append(timer)
            self.repair_timers.sort()
        if self.kc_window.exists('repair_empty.png'):
            for i in self.kc_window.findAll('repair_empty.png'):
                empty_docks += 1
        else:
            self.next_sortie_time_set()
            log_warning("Cannot repair; docks are full. Checking back at %s!" % self.next_sortie_time.strftime("%Y-%m-%d %H:%M:%S"))
        if empty_docks != 0:
            repair_queue = empty_docks if self.count_damage_above_limit('repair') > empty_docks else self.count_damage_above_limit('repair')
            while empty_docks > 0 and repair_queue > 0:
                repair_start = False
                wait_and_click(self.kc_window, 'repair_empty.png', 30)
                sleep(2)
                log_msg("Check for critically damaged ships.")
                if check_and_click(self.kc_window, Pattern('repair_dmg_critical.png').similar(0.95)):
                    log_success("Starting repair on critically damaged ship!")
                    self.damage_counts[2] -= 1
                    repair_start = True
                if repair_start == False and self.repair_limit <= 1:
                    log_msg("Check for moderately-damaged ships.")
                    if check_and_click(self.kc_window, Pattern('repair_dmg_moderate.png').similar(0.95)):
                        log_success("Starting repair on moderately damaged ship!")
                        self.damage_counts[1] -= 1
                        repair_start = True
                if repair_start == False and self.repair_limit == 0:
                    log_msg("Check for lightly-damaged ships.")
                    if check_and_click(self.kc_window, Pattern('repair_dmg_light.png').similar(0.95)):
                        log_success("Starting repair on lightly damaged ship!")
                        self.damage_counts[0] -= 1
                        repair_start = True
                if repair_start == True:
                    repair_queue = empty_docks if self.count_damage_above_limit('repair') > empty_docks else self.count_damage_above_limit('repair')
                    sleep(2)
                    if self.repair_time_limit == 0:
                        # If set to use buckets for all repairs, no need to check timer
                        log_success("Using bucket for all repairs!")
                        self.kc_window.click('repair_bucket_switch.png')
                        self.next_sortie_time_set(0, 0)
                        if self.count_damage_above_limit('repair') > 0:
                            sleep(10)
                    else:
                        # Otherwise, act accordingly to timer and repair timer limit
                        repair_timer = check_timer(self.kc_window, 'repair_timer.png', 'r', 80, 5)
                        if int(repair_timer[0:2]) >= self.repair_time_limit:
                            # Use bucket if the repair time is longer than desired
                            log_success("Repair time too long... using bucket!")
                            self.kc_window.click('repair_bucket_switch.png')
                            self.next_sortie_time_set(0, 0)
                            if self.count_damage_above_limit('repair') > 0:
                                sleep(10)
                        else:
                            # Try setting next sortie time according to repair timer
                            timer = self.timer_end(int(repair_timer[0:2]), int(repair_timer[3:5]) - 1)
                            log_success("Repair should be done at %s" % timer.strftime("%Y-%m-%d %H:%M:%S"))
                            self.next_sortie_time_set(int(repair_timer[0:2]), int(repair_timer[3:5]) - 1)
                            self.repair_timers.append(timer)
                            self.repair_timers.sort()
                            empty_docks -= 1
                    wait_and_click(self.kc_window, 'repair_start.png', 10)
                    wait_and_click(self.kc_window, 'repair_start_confirm.png', 10)
                    sleep(2)

    def __str__(self):
        return '%s' % self.next_sortie_time.strftime("%Y-%m-%d %H:%M:%S")

    # Set next sortie time; if the proposed time is longer than the previously
    # stored time, replace. Otherwise, keep the older (longer) one
    def next_sortie_time_set(self, hours=-1, minutes=-1):
        if hours == -1 and minutes == -1:
            self.next_sortie_time = self.repair_timers[0]
        else:
            proposed_time = datetime.datetime.now() + datetime.timedelta(hours=hours, minutes=minutes)
            if proposed_time > self.next_sortie_time:
                self.next_sortie_time = proposed_time

    def timer_end(self, hours, minutes):
        return datetime.datetime.now() + datetime.timedelta(hours=hours, minutes=minutes)

class PvP:
    def __init__(self, kc_window, settings):
        self.kc_window = kc_window

    def go_pvp(self):
        rnavigation(self.kc_window, 'pvp', 2)
        # Select random pvp opponent
        random_choices = ['pvp_row_1.png', 'pvp_row_2.png']
        random_choice_one = choice(random_choices)
        random_choices.remove(random_choice_one)
        random_choice_two = random_choices[0]
        if not check_and_click(self.kc_window, random_choice_one, expand_areas('pvp_row')):
            if not check_and_click(self.kc_window, random_choice_two, expand_areas('pvp_row')):
                log_warning("No available PvP opponents!")
                return False
        # An opponent was chosen
        rejigger_mouse(self.kc_window, 50, 750, 50, 350)
        wait_and_click(self.kc_window, 'pvp_start_1.png', 30)
        wait_and_click(self.kc_window, 'pvp_start_2.png', 30)
        log_msg("Sortieing against PvP opponent!")
        rejigger_mouse(self.kc_window, 50, 350, 0, 180)
        wait_and_click(self.kc_window, 'formation_line_ahead.png', 30)
        rejigger_mouse(self.kc_window, 50, 750, 0, 180)
        while not (self.kc_window.exists('next.png')
            or self.kc_window.exists('combat_nb_fight.png')):
            sleep(10)
        check_and_click(self.kc_window, 'combat_nb_fight.png')
        sleep(3)
        while not self.kc_window.exists('next.png'):
            sleep(10)
        wait_and_click(self.kc_window, 'next.png', 30, expand_areas('next'))
        sleep(3)
        wait_and_click(self.kc_window, 'next.png', 30, expand_areas('next'))
        log_msg("PvP complete!")
        return True

class FleetcompSwitcher:
    def __init__(self, kc_window, settings):
        self.kc_window = kc_window

    def switch_fleetcomp(self, fleetcomp):
        # Navigate to the fleetcomp page, then enter the fleetcomp screen
        rnavigation(self.kc_window, 'fleetcomp')
        wait_and_click(self.kc_window, 'fleetcomp_screen.png', 30)
        self.kc_window.wait('fleetcomp_button_offset.png', 30)
        # the button_offset image is located 50 pixels above the first button,
        # and each subsequent buttons are situated 52 pixels apart vertically
        target_button = Pattern('fleetcomp_button_offset.png').targetOffset(randint(-15, 15), 50 + (52 * (fleetcomp - 1)) + randint(-8, 8))
        self.kc_window.click(target_button)
