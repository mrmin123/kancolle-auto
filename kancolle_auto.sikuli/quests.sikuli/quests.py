# Ensei (expedition) task list.
from sikuli import *
import datetime
from util import *

class Quests:
    def __init__(self, kc_window, settings):
        self.kc_window = kc_window
        self.active_quests = ['d2', 'd3', 'd4', 'd9'].sort()
        self.active_quests_unchecked = ['d2', 'd3', 'd4', 'd9'].sort()
        self.first_type = self.active_quests[0][0]
        self.last_type = self.active_quests[-1][0]

    def go_quests(self):
        # Navigate to Expedition menu
        rnavigation(self.kc_window, 'quests', 2)
        wait_and_click(self.kc_window, 'menu_top_home.png', 60) # Go away Ooyodo
        sleep(2)

    def check_quests(self):
        start_check = True
        while not self.kc_window.exists(self.first_type + '.png'):
            if check_and_click(self.kc_window, Pattern('quests_next_page.png').exact()):
                pass
            else:
                print 'Quests not found!'
                start_check = False
                break

        while start_check:
            for quest in self.active_quests_unchecked:
                if check_and_click(self.kc_window, Pattern(quest + '.png').exact()):
                    self.active_quests_unchecked.remove(quest)
            if check_and_click(self.kc_window, Pattern('quests_next_page.png').exact()):
                pass
            else:
                start_check = False

