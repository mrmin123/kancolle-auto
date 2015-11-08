# Ensei (expedition) task list.
from sikuli import *
import datetime
from util import *

class Quests:
    def __init__(self, kc_window, settings):
        self.kc_window = kc_window

    def go_quests(self):
        # Navigate to Expedition menu
        rnavigation(self.kc_window, 'quests', 2)
        wait_and_click(self.kc_window, 'menu_top_home.png', 60) # Go away Ooyodo
        sleep(2)

    def check_quests(self):
        pass
