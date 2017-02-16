# Expedition module
from sikuli import *
import datetime
from util import *

Settings.OcrTextRead = True
Settings.MinSimilarity = 0.8

class Expedition:
    def __init__(self, kc_region, settings):
        self.kc_region = kc_region
        self.settings = settings
        # self.running_expedition_list = {}
        self.expedition_id_fleet_map = settings['expedition_id_fleet_map']
        # Populate expedition_list with Ensei objects on init
        self.expedition_list = []
        for fleet_id in sorted(self.expedition_id_fleet_map.keys()):
            self.expedition_list.append(ensei_factory(self.expedition_id_fleet_map[fleet_id], fleet_id))

    def go_expedition(self):
        # Navigate to Expedition menu
        rnavigation(self.kc_region, 'expedition', 2, self.settings)

    def run_expedition(self, expedition):
        # Run expedition
        log_msg("Let's send fleet %d out for expedition %d!" % (expedition.fleet_id, expedition.id))
        sleep(1)
        while_count = 0
        if expedition.id in [9998, 9999] and self.kc_region.exists('ensei_name_33.png'):
            wait_and_click(self.kc_region, expedition.area_pict, 10)
        while not check_and_click(self.kc_region, expedition.name_pict):
            wait_and_click(self.kc_region, expedition.area_pict, 10)
            sleep_fast()
            while_count += 1
            while_count_checker(self.kc_region, self.settings, while_count)
        sleep_fast()
        # If the expedition can't be selected, it's either running or just returned
        if not check_and_click(self.kc_region, 'decision.png'):
            if self.kc_region.exists('expedition_time_complete.png'):
                # Expedition just returned
                expedition.check_later(0, -1)  # set the check_later time to now
                expedition.returned = False
                log_warning("Expedition just returned:  %s" % expedition)
            else:
                # Expedition is already running
                expedition_timer = check_timer(self.kc_region, 'expedition_timer.png', 'r', 80)
                # Set expedition's end time as determined via OCR
                expedition.check_later(int(expedition_timer[0:2]), int(expedition_timer[3:5]) - 1)
                expedition.returned = False
                log_warning("Expedition is already running: %s" % expedition)
            return False
        sleep(1)
        rejigger_mouse(self.kc_region, 100, 750, 0, 300)
        log_msg("Trying to send out fleet %s for expedition %s" % (expedition.fleet_id, expedition.id))
        # Select fleet (no need if fleet is 2 as it's selected by default)
        if expedition.fleet_id != 2:
            fleet_name = 'fleet_%s.png' % expedition.fleet_id
            wait_and_click(global_regions['fleet_flags_sec'], fleet_name, expand=expand_areas('fleet_id'))
            sleep_fast()
        # Make sure that the fleet is ready to go
        if not self.kc_region.exists('fleet_busy.png'):
            log_msg("Checking expedition fleet status!")
            if global_regions['check_resupply'].exists('resupply_alert.png') or global_regions['check_resupply'].exists('resupply_red_alert.png'):
                log_warning("Fleet %s needs resupply!" % expedition.fleet_id)
                return True
            wait_and_click(self.kc_region, 'ensei_start.png')
            expedition.start()
            expedition.returned = False
            log_success("Expedition sent!: %s" % expedition)
            sleep(3)
            return False
        else:
            # Fleet's being used for some reason... check back later
            log_error("Fleet not available. Check back later!")
            expedition.check_later(0, 10)
            check_and_click(self.kc_region, 'ensei_area_01.png')
            return False

class Ensei:
    def __init__(self, ensei_id, name_pict, area_pict, duration, fleet_id):
        self.id = ensei_id
        self.name_pict = name_pict
        self.area_pict = area_pict
        self.duration = duration
        self.fleet_id = fleet_id
        self.returned = False
        self.end_time = datetime.datetime.now()

    def __str__(self):
        return "Expedition %d (ETA %s)" % (self.id, self.end_time.strftime("%Y-%m-%d %H:%M:%S"))

    def start(self):
        self.begin_time = datetime.datetime.now()
        self.end_time = self.begin_time + self.duration

    def check_later(self, hours, minutes):
        self.begin_time = datetime.datetime.now()
        self.end_time = self.begin_time + datetime.timedelta(hours=hours, minutes=minutes + 1)

def ensei_factory(ensei_id, fleet_id):
    if ensei_id == 1:
        return Ensei(1, 'ensei_name_01.png', 'ensei_area_01.png', datetime.timedelta(minutes=14, seconds=15), fleet_id)
    elif ensei_id == 2:
        return Ensei(2, 'ensei_name_02.png', 'ensei_area_01.png', datetime.timedelta(minutes=29, seconds=15), fleet_id)
    elif ensei_id == 3:
        return Ensei(3, 'ensei_name_03.png', 'ensei_area_01.png', datetime.timedelta(minutes=19, seconds=15), fleet_id)
    elif ensei_id == 4:
        return Ensei(4, 'ensei_name_04.png', 'ensei_area_01.png', datetime.timedelta(minutes=49, seconds=15), fleet_id)
    elif ensei_id == 5:
        return Ensei(5, 'ensei_name_05.png', 'ensei_area_01.png', datetime.timedelta(minutes=89, seconds=15), fleet_id)
    elif ensei_id == 6:
        return Ensei(6, 'ensei_name_06.png', 'ensei_area_01.png', datetime.timedelta(minutes=39, seconds=15), fleet_id)
    elif ensei_id == 7:
        return Ensei(7, 'ensei_name_07.png', 'ensei_area_01.png', datetime.timedelta(minutes=59, seconds=15), fleet_id)
    elif ensei_id == 8:
        return Ensei(8, 'ensei_name_08.png', 'ensei_area_01.png', datetime.timedelta(hours=2, minutes=59, seconds=15), fleet_id)
    elif ensei_id == 9:
        return Ensei(9, 'ensei_name_09.png', 'ensei_area_02.png', datetime.timedelta(hours=3, minutes=59, seconds=15), fleet_id)
    elif ensei_id == 10:
        return Ensei(10, 'ensei_name_10.png', 'ensei_area_02.png', datetime.timedelta(hours=1, minutes=29, seconds=15), fleet_id)
    elif ensei_id == 11:
        return Ensei(11, 'ensei_name_11.png', 'ensei_area_02.png', datetime.timedelta(hours=4, minutes=59, seconds=15), fleet_id)
    elif ensei_id == 12:
        return Ensei(12, 'ensei_name_12.png', 'ensei_area_02.png', datetime.timedelta(hours=7, minutes=59, seconds=15), fleet_id)
    elif ensei_id == 13:
        return Ensei(13, 'ensei_name_13.png', 'ensei_area_02.png', datetime.timedelta(hours=3, minutes=59, seconds=15), fleet_id)
    elif ensei_id == 14:
        return Ensei(14, 'ensei_name_14.png', 'ensei_area_02.png', datetime.timedelta(hours=5, minutes=59, seconds=15), fleet_id)
    elif ensei_id == 15:
        return Ensei(15, 'ensei_name_15.png', 'ensei_area_02.png', datetime.timedelta(hours=11, minutes=59, seconds=15), fleet_id)
    elif ensei_id == 16:
        return Ensei(16, 'ensei_name_16.png', 'ensei_area_02.png', datetime.timedelta(hours=14, minutes=59, seconds=15), fleet_id)
    elif ensei_id == 17:
        return Ensei(17, 'ensei_name_17.png', 'ensei_area_03.png', datetime.timedelta(minutes=44, seconds=15), fleet_id)
    elif ensei_id == 18:
        return Ensei(18, 'ensei_name_18.png', 'ensei_area_03.png', datetime.timedelta(hours=4, minutes=59, seconds=15), fleet_id)
    elif ensei_id == 19:
        return Ensei(19, 'ensei_name_19.png', 'ensei_area_03.png', datetime.timedelta(hours=5, minutes=59, seconds=15), fleet_id)
    elif ensei_id == 20:
        return Ensei(20, 'ensei_name_20.png', 'ensei_area_03.png', datetime.timedelta(hours=1, minutes=59, seconds=15), fleet_id)
    elif ensei_id == 21:
        return Ensei(21, 'ensei_name_21.png', 'ensei_area_03.png', datetime.timedelta(hours=2, minutes=19, seconds=15), fleet_id)
    elif ensei_id == 22:
        return Ensei(22, 'ensei_name_22.png', 'ensei_area_03.png', datetime.timedelta(hours=2, minutes=59, seconds=15), fleet_id)
    elif ensei_id == 23:
        return Ensei(23, 'ensei_name_23.png', 'ensei_area_03.png', datetime.timedelta(hours=3, minutes=59, seconds=15), fleet_id)
    elif ensei_id == 24:
        return Ensei(24, 'ensei_name_24.png', 'ensei_area_03.png', datetime.timedelta(hours=8, minutes=19, seconds=15), fleet_id)
    elif ensei_id == 25:
        return Ensei(25, 'ensei_name_25.png', 'ensei_area_04.png', datetime.timedelta(hours=39, minutes=59, seconds=15), fleet_id)
    elif ensei_id == 26:
        return Ensei(26, 'ensei_name_26.png', 'ensei_area_04.png', datetime.timedelta(hours=79, minutes=59, seconds=15), fleet_id)
    elif ensei_id == 27:
        return Ensei(27, 'ensei_name_27.png', 'ensei_area_04.png', datetime.timedelta(hours=19, minutes=59, seconds=15), fleet_id)
    elif ensei_id == 28:
        return Ensei(28, 'ensei_name_28.png', 'ensei_area_04.png', datetime.timedelta(hours=24, minutes=59, seconds=15), fleet_id)
    elif ensei_id == 29:
        return Ensei(29, 'ensei_name_29.png', 'ensei_area_04.png', datetime.timedelta(hours=23, minutes=59, seconds=15), fleet_id)
    elif ensei_id == 30:
        return Ensei(30, 'ensei_name_30.png', 'ensei_area_04.png', datetime.timedelta(hours=47, minutes=59, seconds=15), fleet_id)
    elif ensei_id == 31:
        return Ensei(31, 'ensei_name_31.png', 'ensei_area_04.png', datetime.timedelta(hours=1, minutes=59, seconds=15), fleet_id)
    elif ensei_id == 32:
        return Ensei(32, 'ensei_name_32.png', 'ensei_area_04.png', datetime.timedelta(hours=23, minutes=59, seconds=15), fleet_id)
    elif ensei_id == 35:
        return Ensei(35, 'ensei_name_35.png', 'ensei_area_05.png', datetime.timedelta(hours=6, minutes=59, seconds=15), fleet_id)
    elif ensei_id == 36:
        return Ensei(36, 'ensei_name_36.png', 'ensei_area_05.png', datetime.timedelta(hours=8, minutes=59, seconds=15), fleet_id)
    elif ensei_id == 37:
        return Ensei(37, 'ensei_name_37.png', 'ensei_area_05.png', datetime.timedelta(hours=2, minutes=44, seconds=15), fleet_id)
    elif ensei_id == 38:
        return Ensei(38, 'ensei_name_38.png', 'ensei_area_05.png', datetime.timedelta(hours=2, minutes=54, seconds=15), fleet_id)
    elif ensei_id == 39:
        return Ensei(39, 'ensei_name_39.png', 'ensei_area_05.png', datetime.timedelta(hours=29, minutes=59, seconds=15), fleet_id)
    elif ensei_id == 40:
        return Ensei(40, 'ensei_name_40.png', 'ensei_area_05.png', datetime.timedelta(hours=6, minutes=49, seconds=15), fleet_id)
    elif ensei_id == 9998:
        return Ensei(9998, 'ensei_name_preboss.png', 'ensei_area_e.png', datetime.timedelta(hours=0, minutes=15, seconds=0), fleet_id)
    elif ensei_id == 9999:
        return Ensei(9999, 'ensei_name_boss.png', 'ensei_area_e.png', datetime.timedelta(hours=0, minutes=30, seconds=0), fleet_id)
    else:
        log_warning("%s is an invalid/unsupported expedition! Defaulting to expedition 2!" % ensei_id)
        return ensei_factory(2, fleet_id)
