from time import sleep
import datetime
import os
import sys
sys.path.append(os.getcwd())#get current script working directory inside the .sikuli folder and append as sys path
import expedition as expedition_module #fixed ImportError: No module named expedition


# mapping from expedition id to suitable fleet id for the expedition.
expedition_id_fleet_map = {38: 2,
                            2: 3,
                            5: 4}
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

    kc_window_region.wait("senseki.png", 300)
    check_and_click("home.png")
    kc_window_region.hover("senseki.png")
    #kc_window_region.mouseMove(0, 0)
    kc_window_region.wait("sortie.png", 300)
    #kc_window_region.wait("sortie.png", 10)
    
    check_expedition()


def check_window():
    global kc_window_region

    switchApp("KanColleTool Viewer")
    switchApp("KanColleViewer!")
    
    kc_window_region = App.focusedWindow()
    sleep(5)


def go_expedition():
    kc_window_region.hover("senseki.png")
    wait_and_click("sortie.png", 300)
    wait_and_click("expedition.png", 300)
    kc_window_region.wait("expedition_screen_ready.png", 300)


def run_expedition(expedition):
    global running_expedition_list

    kc_window_region.click(expedition.area_pict)
    sleep(1)
    kc_window_region.click(expedition.name_pict)
    sleep(1)
    if kc_window_region.exists("exp_started.png"):
        print expedition, "is already running. Skipped."
        expedition.start()
        running_expedition_list.append(expedition)
        return
    kc_window_region.hover("senseki.png")
    kc_window_region.click("decision.png")
    kc_window_region.hover("senseki.png")
    sleep(1)
    print "Try", expedition
    fleet_id = expedition_id_fleet_map[expedition.id]
    print 'Try to use fleet', fleet_id
    if fleet_id != 2:
        fleet_name = "fleet_%d.png" % fleet_id
        kc_window_region.click(fleet_name)
        sleep(1)
    if not kc_window_region.exists("fleet_busy.png"):
        if (kc_window_region.exists("supply_alert.png") or kc_window_region.exists("supply_red_alert.png")):
            print "Fleet %d not supplied!" % fleet_id
            supply(fleet_id)
            go_expedition()
            run_expedition(expedition)
            return
        kc_window_region.click("ensei_start.png")
        kc_window_region.hover("senseki.png")
        kc_window_region.wait("exp_started.png", 300)
        expedition.start()
        print expedition, "successfully started"
        running_expedition_list.append(expedition)
        sleep(4)
    else:
        print "No fleets were available for this expedition."
        kc_window_region.click("ensei_area_01.png")


def check_expedition():
    sleep(1)
    kc_window_region.hover("senseki.png")
    if check_and_click("expedition_finish.png"):
        wait_and_click("next.png", 300)
        wait_and_click("next.png")
        kc_window_region.wait("sortie.png", 300)

        check_expedition()


def supply(fleet_id=0):
    kc_window_region.hover("senseki.png")
    if not check_and_click("supply.png"):
        check_and_click("supply2.png")
    kc_window_region.wait("supply_screen.png", 300)
    if fleet_id == 0:
        for fleet_id in expedition_id_fleet_map.values():
            fleet_name = "fleet_%d.png" % fleet_id
            wait_and_click(fleet_name)
            sleep(1)
            if kc_window_region.exists(Pattern("supply_all.png").exact()):
                while not kc_window_region.exists("checked.png"):
                    kc_window_region.click("supply_all.png")
                    sleep(0.1)
                wait_and_click("supply_available.png")
                kc_window_region.wait("supply_not_available.png", 300)
                kc_window_region.hover("senseki.png")
                kc_window_region.wait("supply_not_available.png", 300)
                sleep(1)
    else:
        fleet_name = "fleet_%d.png" % fleet_id
        kc_window_region.click(fleet_name)
        sleep(1)
        if kc_window_region.exists(Pattern("supply_all.png").exact()):
            while not kc_window_region.exists("checked.png"):
                kc_window_region.click("supply_all.png")
                sleep(0.1)
            wait_and_click("supply_available.png")
            kc_window_region.wait("supply_not_available.png", 300)
            kc_window_region.wait("supply_not_available.png", 300)
            sleep(1)
    go_home()


def init():
    expedition_list = map(expedition_module.ensei_factory, expedition_id_fleet_map.keys())

    go_home()
    supply()
    go_expedition()
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
            go_expedition()
            run_expedition(item)
    sleep(10)
