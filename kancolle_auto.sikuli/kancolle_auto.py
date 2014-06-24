import time
import random
import os
import datetime

script_path = os.path.dirname(getBundlePath())
if not script_path in sys.path: sys.path.append(script_path)

import expedition as ensei_module


# mapping from expedition id to suitable fleet id for the expedition.
ensei_id_fleet_map = {2: [2],
                      6: [3]}
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

    ensei_list = map(ensei_module.ensei_factory, ensei_id_fleet_map.keys())
    random.shuffle(ensei_list)
    success_ensei_list = []
    for expedition in ensei_list:
        kc_region.click(expedition.area_pict)
        time.sleep(2)
        kc_region.click(expedition.name_pict)
        time.sleep(1)
        if not kc_region.exists("decision.png"):
            continue
        kc_region.click("decision.png")
        if kc_region.exists("ensei_enable.png"):
            print "try", expedition
            success_ensei = None
            print 'suitable fleets:', ensei_id_fleet_map[expedition.id]
            for fleet_id in ensei_id_fleet_map[expedition.id]:
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
                    time.sleep(10)
                    break
            if success_ensei != None:
                print expedition, "successfully started"
                success_ensei_list.append(success_ensei)
            else:
                print "no fleets were aveilable for this expedition."
                kc_region.click("ensei_area_01.png")
        else:
            print expedition, "is already running. skipped."
    go_home()
    return success_ensei_list

def check_expedition():
    if kc_region.exists("ensei_finish.png"):
        reward()
        check_expedition()
        supply()

def reward():
    kc_region.click("ensei_finish.png")
    time.sleep(10)
    wait_and_click("next.png")
    wait_and_click("next.png")

def supply():
    kc_region.hover("senseki.png")
    wait_and_click("supply.png") or wait_and_click("supply2.png")
    for fleet_id in [2, 3]:
        fleet_name = "fleet_%d.png" % fleet_id
        kc_region.click(fleet_name)
        kc_region.click("supply_all.png")
        if check_and_click("supply_available.png"): time.sleep(3)
    time.sleep(2)
    kc_region.click("home.png")

def init():
    check_window()
    go_home()
    while not running_expedition_list:
        main()
        time.sleep(120)

def main():
    global running_expedition_list
    running_expedition_list += expedition()

def refresh():
    kc_region.hover("senseki.png")
    kc_region.click("home.png")
    time.sleep(3)
    go_home()


init()
while True:
    if any(running_expedition_list):
        check_window()
        running_expedition_list = filter(lambda e: not e.is_end, running_expedition_list)
        refresh()
        main()
    elif not running_expedition_list:
        init()
    else:
        end_time = min(map(lambda e: e.end_time(), running_expedition_list))
        print "next expedition end time:", end_time
    time.sleep(10)
