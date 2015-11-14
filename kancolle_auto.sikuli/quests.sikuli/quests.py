# Ensei (expedition) task list.
from sikuli import *
import datetime
from util import *

class Quests:
    def __init__(self, kc_window, settings):
        self.kc_window = kc_window
        self.active_quests = list(settings['active_quests'])
        self.active_quests_unchecked = list(settings['active_quests'])
        self.first_type = self.active_quests[0][0]
        self.last_type = self.active_quests[-1][0]
        self.done_expeditions = 0
        self.done_sorties = 0

    def go_quests(self):
        # Navigate to Expedition menu
        rnavigation(self.kc_window, 'quests', 2)

    def check_quests(self):
        start_check = True
        while not self.kc_window.exists(self.first_type + '.png'):
            self.finish_quests()
            if check_and_click(self.kc_window, Pattern('quests_next_page.png').exact()):
                pass
            else:
                print 'Quests not found!'
                start_check = False
                break

        while start_check:
            self.finish_quests()
            for quest in self.active_quests_unchecked:
                if check_and_click(self.kc_window, Pattern(quest + '.png').exact()):
                    self.active_quests_unchecked.remove(quest)
            if check_and_click(self.kc_window, Pattern('quests_next_page.png').exact()):
                pass
            else:
                start_check = False

    def finish_quests(self):
        while self.kc_window.exists('quest_completed.png'):
            if check_and_click('quest_completed.png'):
                while self.kc_window.exists('quest_reward_accept.png'):
                    check_and_click('quest_reward_accept.png')
                    sleep(3)

    def reset_quests(self):
        self.active_quests_unchecked = list(settings['active_quests'])
        self.done_expeditions = 0
        self.done_sorties = 0

class Quest_Tree:
    def __init__(self):
        pass
