import time
import datetime

import expedition as ensei_module


# mapping from expedition id to suitable fleet id for the expedition.
ensei_id_fleet_map = {3: 2,
                      5: 3}
running_expedition_list = []


def check_and_click(pic):
    if exists(pic):
        click(pic)
        return True
    return False


def wait_and_click(pic, time=0):
    if time:
        wait(pic, time)
    else:
        wait(pic)
    click(pic)


def go_home():
    check_window()

    check_and_click("home.png")
    hover("senseki.png")
    check_expedition()


def check_window():
    switchApp("KanColleTool Viewer")
    switchApp("KanColleViewer")

    wait("senseki.png", 30)


def expedition():
    hover("senseki.png")
    wait_and_click("sortie.png")
    wait_and_click("expedition.png")
    wait("expedition_screen_ready.png", 10)


def run_expedition(expedition):
    global running_expedition_list
    click(expedition.area_pict)
    time.sleep(2)
    click(expedition.name_pict)
    time.sleep(1)
    if not exists("decision.png"):
        return
    click("decision.png")
    if exists("ensei_enable.png"):
        print "try", expedition
        success_ensei = None
        print 'suitable fleets:', ensei_id_fleet_map[expedition.id]
        fleet_id = ensei_id_fleet_map[expedition.id]
        print 'try to use fleet', fleet_id
        if fleet_id != 2:
            fleet_name = "fleet_%d.png" % fleet_id
            click(fleet_name)
            time.sleep(2)
        click("ensei_start.png")
        if exists("exp_started.png"):
            expedition.start()
            print expedition, "successfully started"
            running_expedition_list.append(expedition)
            time.sleep(4)
        else:
            print "no fleets were aveilable for this expedition."
            click("ensei_area_01.png")
    else:
        print expedition, "is already running. skipped."


def check_expedition():
    if check_and_click("ensei_finish.png"):
        wait_and_click("next.png", 15)
        wait_and_click("next.png")
        check_expedition()


def supply(fleet_id=0):
    hover("senseki.png")
    if not check_and_click("supply.png"):
        check_and_click("supply2.png")
    wait("supply_not_available.png", 10)
    if fleet_id == 0:
        for fleet_id in ensei_id_fleet_map.values():
            fleet_name = "fleet_%d.png" % fleet_id
            click(fleet_name)
            wait_and_click("supply_all.png")
            if check_and_click("supply_available.png"):
                wait("supply_not_available.png", 10)
                time.sleep(1)
    else:
        fleet_name = "fleet_%d.png" % fleet_id
        click(fleet_name)
        wait_and_click("supply_all.png")
        if check_and_click("supply_available.png"):
            wait("supply_not_available.png", 10)
            time.sleep(1)
    go_home()


def init():
    ensei_list = map(ensei_module.ensei_factory, ensei_id_fleet_map.keys())

    go_home()
    supply()
    expedition()
    for exp in ensei_list:
        run_expedition(exp)


init()
while True:
    for item in running_expedition_list:
        now_time = datetime.datetime.now()
        if now_time > item.end_time:
            print "Restart expedition"
            running_expedition_list.remove(item)
            go_home()
            supply(ensei_id_fleet_map[item.id])
            expedition()
            run_expedition(item)
    time.sleep(10)
