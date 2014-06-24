myScriptPath = "C:\\Users\\yukarin\\Documents\\GitHub\\kancolle-auto\\kancolle_auto.sikuli"
if not myScriptPath in sys.path: sys.path.append(myScriptPath)

import time
import random
import datetime

import expedition as ensei_module


# mapping from expedition id to suitable fleet id for the expedition. 
ensei_id_fleet_map = {2: [2], 
                      6: [3]}
running_ensei_list = []

def check_and_click(pic):
    if exists(pic):
        click(pic)
        return True 
    return False

def wait_and_click(pic):
    wait(pic)
    click(pic)

def go_home():
    check_and_click("home.png")
    hover("senseki.png")
    check_expedition()

def expedition():
    hover("senseki.png")
    wait_and_click("sortie.png")
    wait_and_click("expedition.png")

    ensei_list = map(ensei_module.ensei_factory, ensei_id_fleet_map.keys())
    random.shuffle(ensei_list)
    success_ensei_list = []
    for expedition in ensei_list:
        click(expedition.area_pict)
        sleep(2)
        click(expedition.name_pict)
        if not exists("decision.png"):
            continue
        click("decision.png")
        if exists("ensei_enable.png"):
            print "try", expedition
            success_ensei = None
            print 'suitable fleets:', ensei_id_fleet_map[expedition.id]
            for fleet_id in ensei_id_fleet_map[expedition.id]:
                print 'try to use fleet', fleet_id
                if fleet_id != 2:
                    fleet_name = "fleet_%d.png" % fleet_id
                    click(fleet_name)
                    sleep(2)
                click("ensei_start.png")
                sleep(5)
                if not exists("ensei_enable.png"):
                    expedition.start()
                    success_ensei = expedition
                    time.sleep(10)
                    break
            if success_ensei != None:
                print expedition, "successfully started"
                success_ensei_list.append(success_ensei)
            else:
                print "no fleets were aveilable for this expedition."
                click("ensei_area_01.png")
        else:
            print expedition, "is already running. skipped."
    go_home()
    return success_ensei_list

def check_expedition():
    if exists("ensei_finish.png"):
        reward()

def reward():
    click("ensei_finish.png")
    time.sleep(10)
    wait_and_click("next.png")
    wait_and_click("next.png")
    reward()
    return True

def supply():
    hover("senseki.png")
    wait_and_click("supply.png")
    for fleet_id in [2, 3]:
        fleet_name = "fleet_%d.png" % fleet_id
        click(fleet_name)
        click("supply_all.png")
        if check_and_click("matomete_hokyu.png"): time.sleep(5)
    time.sleep(3)
    click("home.png")
    return

def init():
    go_home()
    supply()
    while not running_ensei_list:
        main()
        time.sleep(120)

def main():
    if check_expedition():
        supply()
    global running_ensei_list
    running_ensei_list += expedition()

def refresh():
    hover("senseki.png")
    click("home.png")
    time.sleep(3)
    go_home()


init()
while True: 
    if any(running_ensei_list):
        running_ensei_list = filter(lambda e: not e.is_end, running_ensei_list)
        refresh()
        main()
    elif not running_ensei_list:
        init()
    else:
        end_time = min(map(lambda e: e.end_time(), running_ensei_list))
        print "next expedition end time:", end_time
    time.sleep(10)
