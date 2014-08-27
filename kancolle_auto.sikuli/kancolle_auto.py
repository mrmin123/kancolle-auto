import time
import datetime

import expedition as expedition_module


# mapping from expedition id to suitable fleet id for the expedition.
expedition_id_fleet_map = {3: 2,
                           5: 3}
running_expedition_list = []
kc_window_region = None


def check_and_click(pic):
    if kc_window_region.exists(pic):
        kc_window_region.click(pic)
        return True
    return False


def wait_and_click(pic, time=0):
    if time:
        kc_window_region.wait(pic, time)
    else:
        kc_window_region.wait(pic)
    kc_window_region.click(pic)


def go_home():
    check_window()

    check_and_click("home.png")
    kc_window_region.wait(Pattern("sortie.png").similar(1), 10)
    #kc_window_region.wait("sortie.png", 10)
    kc_window_region.hover("senseki.png")
    
    check_expedition()


def check_window():
    global kc_window_region

    switchApp("KanColleTool Viewer")
    switchApp("KanColleViewer!")
    if not kc_window_region:
        kc_window_region = App.focusedWindow()

    kc_window_region.wait("senseki.png", 30)


def expedition():
    kc_window_region.hover("senseki.png")
    wait_and_click("sortie.png", 10)
    wait_and_click("expedition.png", 10)
    kc_window_region.wait("expedition_screen_ready.png", 10)


def run_expedition(expedition):
    global running_expedition_list

    kc_window_region.click(expedition.area_pict)
    time.sleep(1)
    kc_window_region.click(expedition.name_pict)
    time.sleep(1)
    if kc_window_region.exists("exp_started.png"):
        print expedition, "is already running. Skipped."
        return
    kc_window_region.click("decision.png")
    time.sleep(1)
    print "Try", expedition
    fleet_id = expedition_id_fleet_map[expedition.id]
    print 'Try to use fleet', fleet_id
    if fleet_id != 2:
        fleet_name = "fleet_%d.png" % fleet_id
        kc_window_region.click(fleet_name)
        time.sleep(1)
    if not kc_window_region.exists("fleet_busy.png"):
        kc_window_region.click("ensei_start.png")
        kc_window_region.wait("exp_started.png", 10)
        expedition.start()
        print expedition, "successfully started"
        running_expedition_list.append(expedition)
        time.sleep(4)
    else:
        print "No fleets were aveilable for this expedition."
        kc_window_region.click("ensei_area_01.png")


def check_expedition():
    if check_and_click("ensei_finish.png"):
        wait_and_click("next.png", 20)
        wait_and_click("next.png")
        kc_window_region.wait("sortie.png", 10)

        check_expedition()


def supply(fleet_id=0):
    kc_window_region.hover("senseki.png")
    if not check_and_click("supply.png"):
        check_and_click("supply2.png")
    kc_window_region.wait("supply_screen.png", 10)
    if fleet_id == 0:
        for fleet_id in expedition_id_fleet_map.values():
            fleet_name = "fleet_%d.png" % fleet_id
            wait_and_click(fleet_name)
            time.sleep(1)
            if kc_window_region.exists(Pattern("supply_all.png").similar(1)):
                while not kc_window_region.exists("checked.png"):
                    kc_window_region.click("supply_all.png")
                    time.sleep(0.1)
                wait_and_click("supply_available.png")
                kc_window_region.wait("supply_not_available.png", 10)
                time.sleep(1)
    else:
        fleet_name = "fleet_%d.png" % fleet_id
        kc_window_region.click(fleet_name)
        time.sleep(1)
        if kc_window_region.exists(Pattern("supply_all.png").similar(1)):
            while not kc_window_region.exists("checked.png"):
                kc_window_region.click("supply_all.png")
                time.sleep(0.1)
            wait_and_click("supply_available.png")
            kc_window_region.wait("supply_not_available.png", 10)
            time.sleep(1)
    go_home()


def init():
    expedition_list = map(expedition_module.ensei_factory, expedition_id_fleet_map.keys())

    go_home()
    supply()
    expedition()
    for exp in expedition_list:
        run_expedition(exp)


init()
while True:
    for item in running_expedition_list:
        now_time = datetime.datetime.now()
        if now_time > item.end_time:
            print "Expedition #%d ends, restarting" % item.id
            running_expedition_list.remove(item)
            go_home()
            supply(expedition_id_fleet_map[item.id])
            expedition()
            run_expedition(item)
    time.sleep(10)
