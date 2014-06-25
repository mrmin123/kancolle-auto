import time
import random
import datetime
import threading

import expedition as ensei_module


# mapping from expedition id to suitable fleet id for the expedition.
ensei_id_fleet_map = {3: 2,
                      5: 3}
running_expedition_list = []
kc_region = None

def check_and_click(pic):
    if kc_region.exists(pic):
        kc_region.click(pic)
        return True
    return False

def wait_and_click(pic):
    kc_region.wait(pic)
    kc_region.click(pic)

def go_home():
    check_and_click("home.png")
    kc_region.hover("senseki.png")
    check_expedition()

def check_window():
    switchApp("KanColleTool Viewer")
    kct_viewer = App("KanColleTool Viewer")
    global kc_region
    kc_region = kct_viewer.focusedWindow()

def expedition():
    kc_region.hover("senseki.png")
    wait_and_click("sortie.png")
    wait_and_click("expedition.png")
    kc_region.wait("expedition_screen_ready.png")

def run_expedition(expedition):
    global running_expedition_list
    kc_region.click(expedition.area_pict)
    time.sleep(2)
    kc_region.click(expedition.name_pict)
    time.sleep(1)
    if not kc_region.exists("decision.png"):
        return
    kc_region.click("decision.png")
    if kc_region.exists("ensei_enable.png"):
        print "try", expedition
        success_ensei = None
        print 'suitable fleets:', ensei_id_fleet_map[expedition.id]
        fleet_id = ensei_id_fleet_map[expedition.id]
        print 'try to use fleet', fleet_id
        if fleet_id != 2:
            fleet_name = "fleet_%d.png" % fleet_id
            kc_region.click(fleet_name)
            time.sleep(2)
        kc_region.click("ensei_start.png")
        time.sleep(5)
        if not kc_region.exists("ensei_enable.png"):
            expedition.start()
            success_ensei = expedition
            #time.sleep(10)
        if success_ensei != None:
            print expedition, "successfully started"
            running_expedition_list.append(success_ensei)
        else:
            print "no fleets were aveilable for this expedition."
            kc_region.click("ensei_area_01.png")
    else:
        print expedition, "is already running. skipped."

def check_expedition():
    if check_and_click("ensei_finish.png"):
        time.sleep(10)
        wait_and_click("next.png")
        wait_and_click("next.png")
        check_expedition()
        #supply()

def supply():
    kc_region.hover("senseki.png")
    if not check_and_click("supply.png"): check_and_click("supply2.png")
    kc_region.wait("supply_not_available.png")
    for fleet_id in ensei_id_fleet_map.values():
        fleet_name = "fleet_%d.png" % fleet_id
        kc_region.click(fleet_name)
        time.sleep(1)
        kc_region.click("supply_all.png")
        if check_and_click("supply_available.png"):
            #kc_region.hover("senseki.png")
            kc_region.wait("supply_not_available.png")
        time.sleep(1)
    go_home()

def init():
    ensei_list = map(ensei_module.ensei_factory, ensei_id_fleet_map.keys())
    random.shuffle(ensei_list)

    check_window()
    go_home()
    supply()
    expedition()
    for exp in ensei_list:
        run_expedition(exp)


init()
while True:
    for item in running_expedition_list:
        now_time = datetime.datetime.now()
        if now_time > item.ends_time:
            print "Restart expedition"
            running_expedition_list.remove(item)
            init()
    time.sleep(10)
