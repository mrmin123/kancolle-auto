# Ensei (expedition) task list.
from sikuli import *
import datetime
from util import *

class Quests:
    """
    Quest module to hold relevant variables and data.
    """
    def __init__(self, kc_window, settings):
        self.kc_window = kc_window
        self.quests_checklist = list(settings['active_quests'])
        self.reset_quests()
        self.define_quest_tree()

    def reset_quests(self):
        """
        Method for resetting of tracked quests.
        """
        self.quests_checklist_queue = list(self.quests_checklist)
        self.first_type = self.quests_checklist_queue[0][0]
        self.last_type = self.quests_checklist_queue[-1][0]
        self.active_quests = 0
        self.done_sorties = 0
        self.done_pvp = 0
        self.done_expeditions = 0
        self.schedule_sorties = []
        self.schedule_pvp = []
        self.schedule_expeditions = []
        self.schedule_loop = 0

    def go_quests(self):
        """
        Method for navigating to Quests screen.
        """
        rnavigation(self.kc_window, 'quests', 2)

    def need_to_check(self):
        check = False
        if len(self.quests_checklist_queue) == 0 and self.active_quests == 0:
            # No quests in queue, and no known active quests. No need to check
            # quests.
            return check
        temp_list = [i for i in self.schedule_sorties if i > self.done_sorties]
        if len(temp_list) < len(self.schedule_sorties):
            check = True
            self.schedule_sorties = list(temp_list)
        temp_list = [i for i in self.schedule_pvp if i > self.done_pvp]
        if len(temp_list) < len(self.schedule_pvp):
            check = True
            self.schedule_pvp = list(temp_list)
        temp_list = [i for i in self.schedule_expeditions if i > self.done_expeditions]
        if len(temp_list) < len(self.schedule_expeditions):
            check = True
            self.schedule_expeditions = list(temp_list)
        if self.schedule_loop >= 3:
            self.schedule_loop = 0
            check = True
        return check

    def check_quests(self):
        """
        Method for going through quests page(s), turning in completed quests,
        and starting up quests as needed.
        """
        start_check = True
        temp_list = []
        self.active_quests = 0
        while not self.kc_window.exists(self.first_type + '.png'):
            self.finish_quests()
            self.active_quests += self.count_in_progress()
            if not check_and_click(self.kc_window, 'quests_next_page.png', expand_areas('quests_navigation')):
                log_warning("Couldn't find any relevant quests!")
                start_check = False
                break
        while start_check:
            started_quests = []
            self.finish_quests()
            in_progress = self.count_in_progress() # Find number of active quests
            for quest in self.quests_checklist_queue:
                if check_and_click(self.kc_window, Pattern(quest + '.png').exact()):
                    log_msg("Attempting to start quest %s!" % quest)
                    sleep(3)
                    in_progress_new = self.count_in_progress() # Find number of active quests after pressing quest
                    if in_progress_new < in_progress:
                        # Less active quests than previously. Reclick to reactivate
                        check_and_click(self.kc_window, Pattern(quest + '.png').exact())
                        log_msg("Accidentally inactivated quest... reactivating!")
                        sleep(3)
                    if in_progress_new == in_progress:
                        # Clicked quest, but it wouldn't activate. Queue at max!
                        log_warning("Couldn't activate quest. Queue must be at maximum!")
                        temp_list.extend([quest])
                    else:
                        # Quest activated. Remove activated quest from queue and
                        # add children to temp queue
                        temp_list.extend(self.quest_tree.get_children_ids(quest))
                        started_quests.append(quest)
                        waits = self.quest_tree.find(quest).wait
                        if waits[0] > 0:
                            self.schedule_sorties.append(self.done_sorties + waits[0])
                        if waits[1] > 0:
                            self.schedule_pvp.append(self.done_pvp + waits[1])
                        if waits[2] > 0:
                            self.schedule_expeditions.append(self.done_expeditions + waits[2])
                        if in_progress_new > in_progress:
                            in_progress = in_progress_new
            self.active_quests += in_progress
            self.quests_checklist_queue = list(set(self.quests_checklist_queue) - set(started_quests))
            if not check_and_click(self.kc_window, 'quests_next_page.png', expand_areas('quests_navigation')):
                start_check = False
        self.quests_checklist_queue = temp_list
        if len(self.quests_checklist_queue) > 0:
            self.first_type = self.quests_checklist_queue[0][0]
            self.last_type = self.quests_checklist_queue[-1][0]
        log_msg("New quests to look for next time: %s" % ', '.join(self.quests_checklist_queue))

    def count_in_progress(self):
        """
        Method for counting how many quests in screen are already active. Returns
        number (int) of active quests visible on screen.
        """
        in_progress = 0
        if self.kc_window.exists('quest_in_progress.png'):
            for i in self.kc_window.findAll('quest_in_progress.png'):
                in_progress += 1
        return in_progress

    def finish_quests(self):
        """
        Method containing actions for turning in a complete quest and receiving
        rewards.
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

    def define_quest_tree(self):
        """
        Method for populating quest tree as required by config. Run once on
        initialization.
        """
        self.quest_tree = QuestNode('root')
        # Sortie quests
        if 'bd1' in self.quests_checklist:
            self.quest_tree.add_children('root', [QuestNode('bd1', [1, 0, 0])])
        # PvP quests
        if 'c2' in self.quests_checklist:
            self.quest_tree.add_children('root', [QuestNode('c2', [0, 3, 0])])
            if 'c3' in self.quests_checklist:
                self.quest_tree.add_children('c2', [QuestNode('c3', [0, 5, 0])])
        if 'c4' in self.quests_checklist:
            self.quest_tree.add_children('root', [QuestNode('c4', [0, 20, 0])])
        if 'c8' in self.quests_checklist:
            self.quest_tree.add_children('root', [QuestNode('c8', [0, 7, 0])])
        # Expedition quests
        if 'd2' in self.quests_checklist:
            self.quest_tree.add_children('root', [QuestNode('d2', [0, 0, 1])])
            if 'd3' in self.quests_checklist:
                self.quest_tree.add_children('d2', [QuestNode('d3', [0, 0, 5])])
        if 'd4' in self.quests_checklist:
            self.quest_tree.add_children('root', [QuestNode('d4', [0, 0, 15])])
        if 'd9' in self.quests_checklist:
            self.quest_tree.add_children('root', [QuestNode('d9', [0, 0, 1])])
            if 'd11' in self.quests_checklist:
                self.quest_tree.add_children('d9', [QuestNode('d11', [0, 0, 7])])
        # Supply/Docking quests
        if 'e3' in self.quests_checklist:
            self.quest_tree.add_children('root', [QuestNode('e3', [0, 2, 0])])
            if 'e4' in self.quests_checklist:
                self.quest_tree.add_children('e3', [QuestNode('e4', [15, 10, 15])])

class QuestNode(object):
    """
    QuestNode object to hold individual quests and connect to child quests.
    """
    def __init__(self, id, wait=[0, 0, 0]):
        self.id = id
        self.wait = wait
        self.children = []

    def find(self, target_id):
        target = None
        if self.id == target_id:
            return self
        else:
            for child in self.children:
                target = child.find(target_id)
                if target is not None:
                    return target

    def add_children(self, target_id, payload):
        if self.id == target_id:
            self.children.extend(payload)
        else:
            for child in self.children:
                child.add_children(target_id, payload)

    def get_children_ids(self, target_id):
        children = []
        if len(self.children) > 0:
            for child in self.children:
                if self.id == target_id:
                    children.extend([child.id])
                else:
                    return child.get_children_ids(target_id)
        return children

    def __repr__(self, depth=0):
        """
        For debug purposes.
        """
        text = "\t"*depth + self.id + "\n"
        for child in self.children:
            text += child.__repr__(depth + 1)
        return text
