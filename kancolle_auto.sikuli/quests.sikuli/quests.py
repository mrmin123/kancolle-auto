# Ensei (expedition) task list.
from sikuli import *
import datetime
from util import *

class Quests:
    def __init__(self, kc_window, settings):
        self.kc_window = kc_window
        self.quests_checklist = list(settings['active_quests'])
        self.quests_checklist_unchecked = list(settings['active_quests'])
        self.first_type = self.quests_checklist[0][0]
        self.last_type = self.quests_checklist[-1][0]
        self.done_expeditions = 0
        self.done_pvp = 0
        self.done_sorties = 0
        self.define_quest_tree()

    def go_quests(self):
        """
        Navigate to Quests menu
        """
        rnavigation(self.kc_window, 'quests', 2)

    def check_quests(self):
        """
        Method for going through quests page(s), turning in completed quests,
        and starting up quests as needed
        """
        start_check = True
        temp_list = []
        while not self.kc_window.exists(self.first_type + '.png'):
            self.finish_quests()
            if check_and_click(self.kc_window, 'quests_next_page.png', expand_areas('quests_navigation')):
                pass
            else:
                log_warning("Couldn't find any relevant quests!")
                start_check = False
                break
        while start_check:
            self.finish_quests()
            in_progress = self.count_in_progress()
            print in_progress
            for quest in self.quests_checklist_unchecked:
                if check_and_click(self.kc_window, Pattern(quest + '.png').exact()):
                    log_success("Starting quest %s!" % quest)
                    temp_list.extend(self.quest_tree.get_children_ids(quest))
                    self.quests_checklist_unchecked.remove(quest)
                    sleep(2)
                    in_progress_new = self.count_in_progress()
                    print in_progress_new
                    if in_progress_new < in_progress:
                        check_and_click(self.kc_window, Pattern(quest + '.png').exact())
                        log_msg("Accidentally inactivated quest... reactivating!")
                        sleep(2)
            if check_and_click(self.kc_window, 'quests_next_page.png', expand_areas('quests_navigation')):
                pass
            else:
                start_check = False
        self.quests_checklist_unchecked = temp_list
        log_msg("Quests to look for next time: %s" % ', '.join(self.quests_checklist_unchecked))

    def finish_quests(self):
        """
        Action for turning in a complete quest and receiving rewards
        """
        log_msg("Checking for completed quests!")
        while self.kc_window.exists('quest_completed.png'):
            if check_and_click(self.kc_window, 'quest_completed.png'):
                log_success("Completed quest found!")
                while self.kc_window.exists('quest_reward_accept.png'):
                    check_and_click(self.kc_window, 'quest_reward_accept.png')
                    sleep(2)
                if check_and_click(self.kc_window, 'quests_prev_page.png', expand_areas('quests_navigation')):
                    sleep(2)

    def count_in_progress(self):
        in_progress = 0
        for i in self.kc_window.findAll('quest_in_progress.png'):
            in_progress += 1
        return in_progress

    def reset_quests(self):
        """
        For daily resetting of tracked quests
        """
        self.quests_checklist_unchecked = list(settings['active_quests'])
        self.done_expeditions = 0
        self.done_sorties = 0

    def define_quest_tree(self):
        """
        Populate quest tree depending on config
        """
        self.quest_tree = QuestNode('root')
        # Sortie quests
        if 'bd1' in self.quests_checklist:
            self.quest_tree.add_children('root', [QuestNode('bd1', wait_sortie=1)])
        # PvP quests
        if 'c2' in self.quests_checklist:
            self.quest_tree.add_children('root', [QuestNode('c2', wait_pvp=3)])
            if 'c3' in self.quests_checklist:
                self.quest_tree.add_children('c2', [QuestNode('c3', wait_pvp=5)])
        if 'c4' in self.quests_checklist:
            self.quest_tree.add_children('root', [QuestNode('c4', wait_pvp=20)])
        if 'c8' in self.quests_checklist:
            self.quest_tree.add_children('root', [QuestNode('c8', wait_pvp=7)])
        # Expedition quests
        if 'd2' in self.quests_checklist:
            self.quest_tree.add_children('root', [QuestNode('d2', wait_expedition=1)])
            if 'd3' in self.quests_checklist:
                self.quest_tree.add_children('d2', [QuestNode('d3', wait_expedition=5)])
        if 'd4' in self.quests_checklist:
            self.quest_tree.add_children('root', [QuestNode('d4', wait_expedition=15)])
        if 'd9' in self.quests_checklist:
            self.quest_tree.add_children('root', [QuestNode('d9', wait_expedition=1)])
            if 'd11' in self.quests_checklist:
                self.quest_tree.add_children('d9', [QuestNode('d11', wait_expedition=7)])
        # Supply/Docking quests
        if 'e3' in self.quests_checklist:
            self.quest_tree.add_children('root', [QuestNode('e3', wait_sortie=2)])
            if 'e4' in self.quests_checklist:
                self.quest_tree.add_children('e3', [QuestNode('e4', wait_sortie=15, wait_expedition=15)])

class QuestNode(object):
    def __init__(self, id, wait_sortie=0, wait_pvp=0, wait_expedition=0):
        self.id = id
        self.wait_sortie = wait_sortie
        self.wait_pvp = wait_pvp
        self.wait_expedition = wait_expedition
        self.children = []

    def add_children(self, target_id, payload):
        if self.id == target_id:
            return self.children.extend(payload)
        else:
            for child in self.children:
                return child.add_children(target_id, payload)

    def get_children_ids(self, id):
        children = []
        if len(self.children) > 0:
            for child in self.children:
                if self.id == id:
                    children.extend([child.id])
                else:
                    return child.get_children_ids(id)
        return children

    def __repr__(self, depth=0):
        text = "\t"*depth + self.id + "\n"
        for child in self.children:
            text += child.__repr__(depth + 1)
        return text
