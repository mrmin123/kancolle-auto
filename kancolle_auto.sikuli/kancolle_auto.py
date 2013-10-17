import time
import random
import ensei as ensei_module

ensei_id_list = [2, 3, 5]
ensei_fleets = [2, 3, 4]
def check_and_click(pict):
    if exists(pict):
        click(pict)
        return True 
    return False

def wait_and_click(pict):
    wait(pict)
    click(pict)

def go_next():
    if exists("next.png"):
        click("next.png")
        time.sleep(5)
        go_next()

def go_bokou():
    go_next()
    check_and_click("bokou.png")
    hover("senseki.png")

def shutsugeki():
    hover("senseki.png")
    wait_and_click("shutsugeki.png")
    wait_and_click("ensei.png")

    ensei_list = map(ensei_module.ensei_factory, ensei_id_list)
    random.shuffle(ensei_list)
    success_ensei_list = []
    for ensei in ensei_list:
        click(ensei.name_pict)
        hover(ensei.area_pict)
        click("decision.png")
        if exists("ensei_enable.png"):
            print "try", ensei
            success_ensei = None
            for fleet_id in ensei_fleets:
                fleet_name = "fleet_%d.png" % fleet_id
                click(fleet_name)
                sleep(3)
                click("ensei_start.png")
                sleep(5)
                if not exists("ensei_enable.png"):
                    ensei.start()
                    success_ensei = ensei
                    time.sleep(10)
                    break
            if success_ensei != None:
                print ensei, "successfully started"
                success_ensei_list.append(success_ensei)
            else:
                print "no fleets were aveilable for this ensei."
                click("ensei_area_01.png")
        else:
            print ensei, "is already running. skipped."
    go_bokou()
    return success_ensei_list

def kitou():
    try:
        wait("ensei_finish.png", 5)
    except:
        return False
    click("ensei_finish.png")
    time.sleep(10)
    go_next()
    kitou()
    return True

def hokyu():
    hover("senseki.png")
    wait("hokyu.png")
    click("hokyu.png")
    for fleet_id in [2, 3, 4]:
        fleet_name = "fleet_%d.png" % fleet_id
        click(fleet_name)
        click("hokyu_all.png")
        if check_and_click("matomete_hokyu.png"): time.sleep(5)
    time.sleep(3)
    click("bokou.png")
    return

running_ensei_list = []

def init():
    go_bokou()
    hokyu()
    while not running_ensei_list:
        main()
        time.sleep(120)

def main():
    if kitou():
        hokyu()
    global running_ensei_list
    running_ensei_list += shutsugeki()

def reflesh():
    hover("senseki.png")
    click("hokyu.png")
    time.sleep(3)
    go_bokou()

init()
while True: 
    if any(running_ensei_list):
        running_ensei_list = filter(lambda e: not e.is_end, running_ensei_list)
        reflesh()
        main()
    elif not running_ensei_list:
        init()
    else:
        end_time = min(map(lambda e: e.end_time(), running_ensei_list))
        print "next ensei end time:", end_time
    time.sleep(10)
