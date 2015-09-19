# Combat list.
from sikuli import *
import datetime
from util import (sleep, get_rand, check_and_click, wait_and_click, check_timer,
    log_msg, log_success, log_warning, log_error)

Settings.OcrTextRead = True
Settings.MinSimilarity = 0.8

class Combat:
    def __init__(self, kc_window, combat_id, area_pict, panel_pict, combat_fleet_dmg_limit):
        self.next_sortie_time = datetime.datetime.now()
        self.kc_window = kc_window
        self.id = combat_id
        self.area_pict = area_pict
        self.panel_pict = panel_pict
        self.combat_fleet_dmg_limit = combat_fleet_dmg_limit
        self.dmg_counts = [0, 0, 0]

    # Tally damage state of fleet
    def tally_damages(self):
        log_msg("Checking fleet condition...")
        self.dmg_counts = [0, 0, 0]
        if self.kc_window.exists(Pattern("dmg_light.png").similar(0.95)):
            for i in self.kc_window.findAll(Pattern("dmg_light.png").similar(0.95)):
                self.dmg_counts[0] += 1
        if self.kc_window.exists(Pattern("dmg_moderate.png").similar(0.95)):
            for i in self.kc_window.findAll(Pattern("dmg_moderate.png").similar(0.95)):
                self.dmg_counts[1] += 1
        if self.kc_window.exists(Pattern("dmg_critical.png").similar(0.95)):
            for i in self.kc_window.findAll(Pattern("dmg_critical.png").similar(0.95)):
                self.dmg_counts[2] += 1
        log_msg("Light damage: %d; moderate damage: %d; critical damage: %d" % (self.dmg_counts[0], self.dmg_counts[1], self.dmg_counts[2]))
        return self.dmg_counts

    # Return number of ships damaged above threshold; relies on tally_damages()
    # for a reliable count
    def count_dmg_above_limit(self):
        count = 0
        for i, dmg_count in enumerate(self.dmg_counts):
            if i >= self.combat_fleet_dmg_limit:
                count += dmg_count
        return count

    # Navigate to Sortie menu and click through sortie!
    def go_sortie(self):
        log_msg("Navigating to Sortie menu!")
        self.kc_window.click("sortie.png")
        wait_and_click(self.kc_window, "combat.png")
        wait_and_click(self.kc_window, self.area_pict)
        wait_and_click(self.kc_window, self.panel_pict)
        wait_and_click(self.kc_window, "decision.png")
        self.kc_window.hover("senseki_off.png")
        sleep(2)
        self.tally_damages()
        if self.dmg_counts[2] > 0:
            log_warning("Ship(s) in critical condition! Sortie cancelled!")
            return self.dmg_counts
        if self.count_dmg_above_limit() > 0:
            log_warning("Ships (%d) in condition below threshold! Sortie cancelled!" % self.count_dmg_above_limit())
            return self.dmg_counts
        if not self.kc_window.exists(Pattern("combat_start_disabled.png").exact()):
            log_success("Starting sortie!")
            wait_and_click(self.kc_window, "combat_start.png")
            wait_and_click(self.kc_window, "compass.png", 10)
            wait_and_click(self.kc_window, Pattern("formation_01.png").exact(), 10)
            while not (self.kc_window.exists("combat_nb_retreat.png") or self.kc_window.exists("next.png")):
                sleep(15)
            check_and_click(self.kc_window, "combat_nb_retreat.png")
            wait_and_click(self.kc_window, "next.png", 10)
            sleep(4)
            self.tally_damages()
            wait_and_click(self.kc_window, "next.png", 10)
            sleep(2)
            if not self.kc_window.exists("combat_retreat.png"):
                wait_and_click(self.kc_window, "next_alt.png", 10)
            wait_and_click(self.kc_window, "combat_retreat.png", 10)
            if self.count_dmg_above_limit() == 0:
                # If fleet damage is good to go for another deployment, set the
                # next sortie timer relatively low
                self.next_sortie_time_set(0, get_rand(1, 3))
        else:
            if self.kc_window.exists("combat_nogo_repair.png"):
                log_warning("Cannot sortie due to ships under repair!")
                self.next_sortie_time_set(0, get_rand(5, 5))
                # Expand on this so it goes to repair menu and recheck?
            elif self.kc_window.exists("combat_nogo_supply.png"):
                log_warning("Cannot sortie due to ships needing supply!")
        return self.dmg_counts

    # Navigate to repair menu and repair any ship above damage threshold. Sets
    # next sortie time accordingly
    def go_repair(self):
        log_msg("Navigating to Repair menu!")
        repair_time_limit = 3
        repair_start = False
        sleep(1)
        self.kc_window.click("repair_main.png")
        sleep(2)
        if check_and_click(self.kc_window, "repair_empty.png"):
            sleep(2)
            log_msg("Check for critically damaged ships.")
            if check_and_click(self.kc_window, Pattern("repair_dmg_critical.png").similar(0.95)):
                log_success("Starting repair on critically damaged ship!")
                self.dmg_counts[2] -= 1
                repair_start = True
            if repair_start == False and self.combat_fleet_dmg_limit >= 1:
                log_msg("Check for moderately-damaged ships.")
                if check_and_click(self.kc_window, Pattern("repair_dmg_moderate.png").similar(0.95)):
                    log_success("Starting repair on moderately damaged ship!")
                    self.dmg_counts[1] -= 1
                    repair_start = True
            if repair_start == False and self.combat_fleet_dmg_limit >= 0:
                log_msg("Check for lightly-damaged ships.")
                if check_and_click(self.kc_window, Pattern("repair_dmg_light.png").similar(0.95)):
                    log_success("Starting repair on lightly damaged ship!")
                    self.dmg_counts[0] -= 1
                    repair_start = True
            if repair_start == True:
                repair_timer = check_timer(self.kc_window, "repair_timer.png", 80)
                if int(repair_timer[0:2]) >= repair_time_limit:
                    # Use bucket if the repair time is longer than desired
                    log_success("Repair time too long... using bucket!")
                    self.kc_window.click("repair_bucket_switch.png")
                    self.next_sortie_time_set(0, 0)
                else:
                    # Try setting next sortie time according to repair timer
                    log_success("Repair should be done at %s" % (datetime.datetime.now()
                        + datetime.timedelta(hours=int(repair_timer[0:2]), minutes=int(repair_timer[3:5]))).strftime("%Y-%m-%d %H:%M:%S"))
                    self.next_sortie_time_set(int(repair_timer[0:2]), int(repair_timer[3:5]))
                wait_and_click(self.kc_window, "repair_start.png", 10)
                wait_and_click(self.kc_window, "repair_start_confirm.png", 10)
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

def combat_factory(kc_window, combat_id, combat_fleet_dmg_limit):
    if combat_id == 0:
        return Combat(kc_window, 0, 'combat_area_02.png', 'combat_panel_2-3.png', combat_fleet_dmg_limit)
    elif combat_id == 1:
        return Combat(kc_window, 1, 'combat_area_03.png', 'combat_panel_3-2.png', combat_fleet_dmg_limit)
    return False
