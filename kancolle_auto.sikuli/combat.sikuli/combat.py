# Combat list.
from sikuli import *
import datetime
from util import (sleep, get_rand, check_and_click, wait_and_click, check_timer,
    log_msg, log_success, log_warning, log_error)

Settings.OcrTextRead = True
Settings.MinSimilarity = 0.8

class Combat:
    def __init__(self, kc_window, area_pict, subarea_pict, damage_limit, repair_time_limit):
        self.next_sortie_time = datetime.datetime.now()
        self.kc_window = kc_window
        self.area_pict = area_pict
        self.subarea_pict = subarea_pict
        self.damage_limit = damage_limit
        self.repair_time_limit = repair_time_limit
        self.damage_counts = [0, 0, 0]

    # Tally damage state of fleet
    def tally_damages(self):
        log_msg("Checking fleet condition...")
        self.damage_counts = [0, 0, 0]
        if self.kc_window.exists(Pattern('dmg_light.png').similar(0.95)):
            for i in self.kc_window.findAll(Pattern('dmg_light.png').similar(0.95)):
                self.damage_counts[0] += 1
        if self.kc_window.exists(Pattern('dmg_moderate.png').similar(0.95)):
            for i in self.kc_window.findAll(Pattern('dmg_moderate.png').similar(0.95)):
                self.damage_counts[1] += 1
        if self.kc_window.exists(Pattern('dmg_critical.png').similar(0.95)):
            for i in self.kc_window.findAll(Pattern('dmg_critical.png').similar(0.95)):
                self.damage_counts[2] += 1
        log_msg("Light damage: %d; moderate damage: %d; critical damage: %d" % (self.damage_counts[0], self.damage_counts[1], self.damage_counts[2]))
        return self.damage_counts

    # Return number of ships damaged above threshold; relies on tally_damages()
    # for a reliable count
    def count_damage_above_limit(self):
        count = 0
        for i, dmg_count in enumerate(self.damage_counts):
            if i >= self.damage_limit:
                count += dmg_count
        return count

    # Navigate to Sortie menu and click through sortie!
    def go_sortie(self):
        log_msg("Navigating to Sortie menu!")
        self.kc_window.click('sortie.png')
        wait_and_click(self.kc_window, 'combat.png')
        wait_and_click(self.kc_window, self.area_pict)
        wait_and_click(self.kc_window, self.subarea_pict)
        wait_and_click(self.kc_window, 'decision.png')
        self.kc_window.hover('senseki_off.png')
        sleep(2)
        self.tally_damages()
        if self.damage_counts[2] > 0:
            log_warning("Ship(s) in critical condition! Sortie cancelled!")
            return self.damage_counts
        if self.count_damage_above_limit() > 0:
            log_warning("Ships (%d) in condition below threshold! Sortie cancelled!" % self.count_damage_above_limit())
            return self.damage_counts
        if not self.kc_window.exists(Pattern('combat_start_disabled.png').exact()):
            log_success("Commencing sortie!")
            wait_and_click(self.kc_window, 'combat_start.png')
            sortie_underway = True
            while sortie_underway == True:
                # Compass and/or formation selection
                while not (self.kc_window.exists('compass.png') or self.kc_window.exists('formation_line_ahead.png')):
                    sleep(5)
                check_and_click(self.kc_window, 'compass.png')
                wait_and_click(self.kc_window, Pattern('formation_line_ahead.png').exact(), 30)
                # Decline night battle and/or click through post-battle screens
                while not (self.kc_window.exists('combat_nb_retreat.png') or self.kc_window.exists('next.png')):
                    sleep(15)
                check_and_click(self.kc_window, 'combat_nb_retreat.png')
                wait_and_click(self.kc_window, 'next.png', 30)
                sleep(4)
                # Tally damages at EXP screen
                self.tally_damages()
                wait_and_click(self.kc_window, 'next.png', 30)
                sleep(2)
                # Receive ship reward and/or retreat from sortie
                if not self.kc_window.exists('combat_retreat.png'):
                    wait_and_click(self.kc_window, 'next_alt.png', 30)
                wait_and_click(self.kc_window, 'combat_retreat.png', 30)
                if self.count_damage_above_limit() > 0 or self.damage_counts[2] > 0:
                    # If fleet is damaged, do not run any more sorties
                    sortie_underway = False
                else:
                    # Otherwise, set a low next sortie time
                    self.next_sortie_time_set(0, get_rand(1, 3))
        else:
            if self.kc_window.exists('combat_nogo_repair.png'):
                log_warning("Cannot sortie due to ships under repair!")
                self.next_sortie_time_set(0, get_rand(5, 5))
                # Expand on this so it goes to repair menu and recheck?
            elif self.kc_window.exists('combat_nogo_supply.png'):
                log_warning("Cannot sortie due to ships needing supply!")
        return self.damage_counts

    # Navigate to repair menu and repair any ship above damage threshold. Sets
    # next sortie time accordingly
    def go_repair(self):
        log_msg("Navigating to Repair menu!")
        repair_start = False
        empty_docks = 0
        sleep(1)
        self.kc_window.click('repair_main.png')
        sleep(2)
        for i in self.kc_window.findAll('repair_empty.png'):
            empty_docks += 1
        if empty_docks != 0:
            repair_queue = empty_docks if self.count_damage_above_limit() > empty_docks else self.count_damage_above_limit()
            while repair_queue > 0:
                repair_queue -= 1
                wait_and_click(self.kc_window, 'repair_empty.png', 30)
                sleep(2)
                log_msg("Check for critically damaged ships.")
                if check_and_click(self.kc_window, Pattern('repair_dmg_critical.png').similar(0.95)):
                    log_success("Starting repair on critically damaged ship!")
                    self.damage_counts[2] -= 1
                    repair_start = True
                if repair_start == False and self.damage_limit >= 1:
                    log_msg("Check for moderately-damaged ships.")
                    if check_and_click(self.kc_window, Pattern('repair_dmg_moderate.png').similar(0.95)):
                        log_success("Starting repair on moderately damaged ship!")
                        self.damage_counts[1] -= 1
                        repair_start = True
                if repair_start == False and self.damage_limit >= 0:
                    log_msg("Check for lightly-damaged ships.")
                    if check_and_click(self.kc_window, Pattern('repair_dmg_light.png').similar(0.95)):
                        log_success("Starting repair on lightly damaged ship!")
                        self.damage_counts[0] -= 1
                        repair_start = True
                if repair_start == True:
                    repair_timer = check_timer(self.kc_window, 'repair_timer.png', 80)
                    if int(repair_timer[0:2]) >= self.repair_time_limit:
                        # Use bucket if the repair time is longer than desired
                        log_success("Repair time too long... using bucket!")
                        self.kc_window.click('repair_bucket_switch.png')
                        self.next_sortie_time_set(0, 0)
                        if self.count_damage_above_limit() > 0:
                            repair_queue += 1
                            sleep(10)
                    else:
                        # Try setting next sortie time according to repair timer
                        log_success("Repair should be done at %s" % (datetime.datetime.now()
                            + datetime.timedelta(hours=int(repair_timer[0:2]), minutes=int(repair_timer[3:5]))).strftime("%Y-%m-%d %H:%M:%S"))
                        self.next_sortie_time_set(int(repair_timer[0:2]), int(repair_timer[3:5]))
                    wait_and_click(self.kc_window, 'repair_start.png', 10)
                    wait_and_click(self.kc_window, 'repair_start_confirm.png', 10)
        else:
            log_warning("Cannot repair; docks are full.")

    def __str__(self):
        return '%s' % self.next_sortie_time.strftime("%Y-%m-%d %H:%M:%S")

    # Set next sortie time; if the proposed time is longer than the previously
    # stored time, replace. Otherwise, keep the older (longer) one
    def next_sortie_time_set(self, hours, minutes):
        proposed_time = datetime.datetime.now() + datetime.timedelta(hours=hours, minutes=minutes)
        if proposed_time > self.next_sortie_time:
            self.next_sortie_time = proposed_time

def combat_factory(kc_window, settings):
    combat_area = settings['combat_area']
    combat_subarea = settings['combat_subarea']
    damage_limit = settings['damage_limit']
    repair_time_limit = settings['repair_time_limit']
    return Combat(kc_window, 'combat_area_%d.png' % combat_area,
        'combat_panel_%d-%d.png' % (combat_area, combat_subarea), damage_limit,
        repair_time_limit)
