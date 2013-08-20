import time

def check_and_click(pict):
    if exists(pict):
        click(pict)
    return 

def shutsugeki():
    hover("1376840150580.png")
    wait("1376837741389.png")
    click("1376837529526.png")
    click("1376837538484.png")
    
    click("1376837552261.png")
    click("1376837610684.png")
    if not exists("1376841606981.png"):

        click("1376837589532.png")
        click("1376837610684.png")
    hover("1376839396372.png")
    if not exists("1376841606981.png"):
        click("1376839396372.png")
        return
    check_and_click("1376837727476.png")
    time.sleep(10)
    if exists("1376837670396.png"):
        click("1376837670396.png")
        check_and_click("1376837727476.png")
    wait("1376839396372.png", 10)
    click("1376839396372.png")
    return

def kitou():
    try:
        wait("1376839138084.png", 5)
    except:
        return False
    click("1376839144069.png")
    wait("1376839169972.png", 20)
    click("1376839186924.png")
    time.sleep(2)
    click("1376839186924.png")
    kitou()
    return True

def hokyu():

    wait("1376839215262.png")
    click("1376839225876.png")
    click("1376839239180.png")
    click("1376839272508.png")
    if exists("1376846616135.png"):
        click("1376846616135.png")
    click("1376839309140.png")
    time.sleep(10)
    click("1376839272508.png")
    if exists("1376846616135.png"):
        click("1376846616135.png")
    time.sleep(3)
    click("1376839396372.png")
    return
    
while True:    
    time.sleep(5)
    check_and_click("1376839396372.png")
    if kitou():
        hokyu()
    if kitou():
        hokyu()
    shutsugeki()


    
    
