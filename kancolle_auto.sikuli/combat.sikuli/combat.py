# Combat list.
from sikuli import *
from time import sleep
import datetime
from util import check_and_click, wait_and_click, check_timer, log_msg, log_success, log_warning, log_error

Settings.OcrTextRead = True
class Combat:
    def __init__(self, kc_window, combat_id, area_pict, panel_pict, combat_fleet_dmg_limit):
        self.kc_window = kc_window
        self.id = combat_id
        self.area_pict = area_pict
        self.panel_pict = panel_pict
        self.combat_fleet_dmg_limit = combat_fleet_dmg_limit
        self.dmg_counts = [0, 0, 0]

    def tally_damages(self):
        log_msg("Checking fleet condition...")
        self.dmg_counts = [0, 0, 0]
        if self.kc_window.exists("dmg_light.png"):
            for i in self.kc_window.findAll("dmg_light.png"):
                self.dmg_counts[0] += 1
        if self.kc_window.exists("dmg_medium.png"):
            for i in self.kc_window.findAll("dmg_medium.png"):
                self.dmg_counts[1] += 1
        if self.kc_window.exists("dmg_critical.png"):
            for i in self.kc_window.findAll("dmg_critical.png"):
                self.dmg_counts[2] += 1
        return self.dmg_counts

    def count_dmg_above_limit(self):
        count = 0
        for i, dmg_count in enumerate(self.dmg_counts):
            if i >= self.combat_fleet_dmg_limit:
                count += dmg_count
        return count

    def go_sortie(self):
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
            log_warning("Ship(s) in condition below threshold! Sortie cancelled!")
            return self.dmg_counts
        if self.kc_window.exists("combat_start.png"): # should be check for combat_start_disabled.png
            log_msg("starting sortie!")
            wait_and_click(self.kc_window, "combat_start.png")
            wait_and_click(self.kc_window, "compass.png", 10)
            wait_and_click(self.kc_window, "formation_01.png", 10)
            while not (self.kc_window.exists("combat_nb_retreat.png") or self.kc_window.exists("next.png")):
                sleep(15)
            check_and_click(self.kc_window, "combat_nb_retreat.png")
            wait_and_click(self.kc_window, "next.png", 10)
            sleep(4)
            dmg_counts = self.tally_damages()
            wait_and_click(self.kc_window, "next.png", 10)
            sleep(2)
            if not self.kc_window.exists("combat_retreat.png"):
                wait_and_click(self.kc_window, "next_alt.png", 10)
            wait_and_click(self.kc_window, "combat_retreat.png", 10)
        else:
            if self.kc_window.exists("combat_nogo_repair.png"):
                log_warning("Cannot sortie due to ships under repair!")
            elif self.kc_window.exists("combat_nogo_supply.png"):
                log_warning("Cannot sortie due to ships needing supply!")
        return dmg_counts

    def go_repair(self):
        sleep(1)
        self.kc_window.click("repair_main.png")
        wait_and_click(self.kc_window, "repair_empty.png", 10)
        wait_and_click(self.kc_window, "repair_dmg_critical.png", 10)
        repair_timer = check_timer(self.kc_window, "repair_timer.png", 80)
        print repair_timer
        wait_and_click(self.kc_window, "repair_start.png", 10)
        wait_and_click(self.kc_window, "repair_start_confirm.png", 10)


    def __str__(self):
        return 'Combat (ETA %s)' % (self.id, self.end_time.strftime("%Y-%m-%d %H:%M:%S"))

    def start(self):
        self.begin_time = datetime.datetime.now()
        self.end_time = self.begin_time + self.duration

    def check_later(self, hours, minutes):
        self.begin_time = datetime.datetime.now()
        self.end_time = self.begin_time + datetime.timedelta(hours=hours, minutes=minutes + 1)

def combat_factory(kc_window, combat_id, combat_fleet_dmg_limit):
    if combat_id == 0:
        return Combat(kc_window, 0, 'combat_area_02.png', 'combat_panel_2-3.png', combat_fleet_dmg_limit)
    elif combat_id == 1:
        return Combat(kc_window, 1, 'combat_area_03.png', 'combat_panel_3-2.png', combat_fleet_dmg_limit)
    return False
