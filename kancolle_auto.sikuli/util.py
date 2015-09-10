from time import strftime

# common Sikuli actions
def check_and_click(kc_window, pic):
    if kc_window.exists(pic):
        kc_window.click(pic)
        return True
    return False

def wait_and_click(kc_window, pic, time=0):
    if time:
        kc_window.wait(pic, time)
    else:
        kc_window.wait(pic)
    kc_window.click(pic)

# log colors
class color:
    MSG = '\033[94m'
    SUCCESS = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    END = '\033[0m'

def format(msg):
    now = strftime("%Y-%m-%d %H:%M:%S")
    return "[%s] %s" % (now, msg)

def log_msg(msg):
    print "%s%s%s" % (color.MSG, format(msg), color.END)

def log_success(msg):
    print "%s%s%s" % (color.SUCCESS, format(msg), color.END)

def log_warning(msg):
    print "%s%s%s" % (color.WARNING, format(msg), color.END)

def log_error(msg):
    print "%s%s%s" % (color.ERROR, format(msg), color.END)
