# Ensei (expedition) task list.
from sikuli import *
import datetime
from util import *

class Quests:
    """
    Quest module to hold relevant variables and data.
    """
    def __init__(self, kc_region, settings):
        self.kc_region = kc_region
        self.quest_check_schedule = settings['quests_check_schedule']
        self.combat_enabled = settings['combat_enabled']
        if self.combat_enabled:
            self.combat_area = settings['combat_area']
            self.combat_subarea = settings['combat_subarea']
        self.pvp_enabled = settings['pvp_enabled']
        self.expeditions_enabled = settings['expeditions_enabled']
        if self.expeditions_enabled:
            self.expeditions_tokyo_express = False
            for fleet in settings['expedition_id_fleet_map']:
                if settings['expedition_id_fleet_map'][fleet] == 37 or settings['expedition_id_fleet_map'][fleet] == 38:
                    self.expeditions_tokyo_express = True
                    break
        self.quests_checklist = list(settings['active_quests'])
        self.define_quest_tree()
        # Make sure quests are valid given the config. If not, remove it from
        # the queue. There is probably a better way to do this + the tree,
        # but I'm doing this in a hurry right now...
        invalid_quests = []
        for quest in self.quests_checklist:
            if self.quest_tree.find(quest) == None:
                invalid_quests.append(quest)
        self.quests_checklist = list(set(self.quests_checklist) - set(invalid_quests))
        # Reset quests
        self.reset_quests()

    def reset_quests(self):
        """
        Method for resetting of tracked quests.
        """
        self.quests_checklist_queue = list(sorted(self.quests_checklist))
        log_success("Quests reset. Checking for the following quests: %s" % self.quests_checklist_queue)
        self.active_quests = 0
        self.activated_sortie_quests = []
        self.activated_pvp_quests = []
        self.done_sorties = 0
        self.done_pvp = 0
        self.done_expeditions = 0
        self.schedule_sorties = []
        self.schedule_pvp = []
        self.schedule_expeditions = []
        self.schedule_loop = 0

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
        if self.schedule_loop >= self.quest_check_schedule:
            check = True
        return check

    def go_quests(self, mode, first_run=False):
        """
        Method for going through quests page(s), turning in completed quests,
        and starting up quests as needed.
        """
        rnavigation(self.kc_region, 'quests', 2)
        sleep(1)
        start_check = True
        temp_list = []
        self.active_quests = 0
        log_msg("Checking quests, filtering for %s quests!" % mode)
        if mode == 'sortie':
            # Enable Sortie quests, disable PvP quests
            # Start from last page and move forward so PvP quests are disabled first
            check_and_click(self.kc_region, 'quests_last_page.png', expand_areas('quests_navigation'))
            sleep(1)
            page_continue = 'quests_prev_page.png'
            page_backtrack = None
            disable = 'c'
            toggled_quests = list(self.activated_sortie_quests)
        elif mode == 'pvp':
            # Enable PvP quests, disable Sortie quests
            page_continue = 'quests_next_page.png'
            page_backtrack = 'quests_prev_page.png'
            disable = 'b'
            toggled_quests = list(self.activated_pvp_quests)
        while start_check:
            toggled_quests.extend([q for q in self.quests_checklist_queue if q[0] != disable])
            toggled_quests = list(set(toggled_quests))
            quest_types = list(set([q[0] for q in toggled_quests]))
            if mode == 'sortie':
                quest_types.sort()
            elif mode == 'pvp':
                quest_types.sort(reverse = True)
            started_quests = []
            skip_page = True
            log_msg("Checking for quests: %s" % ', '.join(toggled_quests))
            log_msg("Enabling quests starting with letters: %s" % ', '.join(quest_types))
            self.finish_quests(page_backtrack)
            self.filter_quests(disable)
            for quest_type in quest_types:
                if global_regions['quest_category'].exists(quest_type + '.png'):
                    skip_page = False
                    break
            if skip_page:
                if not check_and_click(self.kc_region, page_continue, expand_areas('quests_navigation')):
                    start_check = False
                    break
                else:
                    continue
            for quest in toggled_quests:
                if self.kc_region.exists(Pattern(quest + '.png').similar(0.999)):
                    quest_check_area = self.kc_region.getLastMatch().below(1).above(60).right(255)
                    if quest_check_area.exists('quest_in_progress.png'):
                        log_msg("Quest %s already active!" % quest)
                    else:
                        log_msg("Attempting to start quest %s!" % quest)
                        check_and_click(self.kc_region, Pattern(quest + '.png').similar(0.999), expand_areas('quest_bar'))
                        sleep(3)
                        if not quest_check_area.exists('quest_in_progress.png'):
                            log_warning("Couldn't activate quest. Queue must be at maximum!")
                            temp_list.extend(quest)
                            continue
                    # Quest activated. Remove activated quest from queue and
                    # add children to temp queue
                    self.active_quests += 1
                    temp_list.extend(self.quest_tree.get_children_ids(quest))
                    started_quests.append(quest)
                    waits = self.quest_tree.find(quest).wait
                    if waits[0] > 0:
                        self.schedule_sorties.append(self.done_sorties + waits[0])
                    if waits[1] > 0:
                        self.schedule_pvp.append(self.done_pvp + waits[1])
                    if waits[2] > 0:
                        self.schedule_expeditions.append(self.done_expeditions + waits[2])
                    #in_progress_new = self.count_in_progress() # Find number of active quests after pressing quest
                    if quest[0] == 'b':
                        self.activated_sortie_quests.append(quest)
                        self.activated_sortie_quests = list(set(self.activated_sortie_quests))
                    elif quest[0] == 'c':
                        self.activated_pvp_quests.append(quest)
                        self.activated_pvp_quests = list(set(self.activated_pvp_quests))
            self.quests_checklist_queue = list(set(self.quests_checklist_queue) - set(started_quests))
            if not check_and_click(self.kc_region, page_continue, expand_areas('quests_navigation')):
                start_check = False
        if first_run:
            self.quests_checklist_queue = temp_list
        else:
            self.quests_checklist_queue += temp_list
            self.quests_checklist_queue.sort()
        log_msg("New quests to look for next time: %s" % ', '.join(self.quests_checklist_queue))

    def filter_quests(self, disable):
        log_msg("Filtering out quests...")
        try:
            # Check if enabled quests on the page are ones to be disabled
            for i in global_regions['quest_status'].findAll('quest_in_progress.png'):
                quest_check_area = i.left(570)
                # If they are, disable them
                if quest_check_area.exists(disable + '.png'):
                    log_msg("Disabling quest!")
                    self.kc_region.click(quest_check_area)
                    sleep(3)
                else:
                    self.active_quests += 1
        except:
            pass

    def finish_quests(self, page_backtrack):
        """
        Method containing actions for turning in a complete quest and receiving
        rewards.
        """
        while check_and_click(global_regions['quest_status'], 'quest_completed.png', expand_areas('quest_completed')):
            log_success("Completed quest found!")
            while check_and_click(self.kc_region, 'quest_reward_accept.png'):
                sleep(2)
            if page_backtrack:
                if check_and_click(self.kc_region, page_backtrack, expand_areas('quests_navigation')):
                    sleep(2)

    def define_quest_tree(self):
        """
        Method for populating quest tree as required by config. Run once on
        initialization.
        """
        self.quest_tree = QuestNode('root')
        # Sortie quests
        # Commented-out quests are not supported due to lack of images
        if self.combat_enabled:
            if 'bd1' in self.quests_checklist:
                self.quest_tree.add_children('root', [QuestNode('bd1', [1, 0, 0])])
                if 'bd2' in self.quests_checklist:
                    self.quest_tree.add_children('bd1', [QuestNode('bd2', [1, 0, 0])])
                    if 'bd3' in self.quests_checklist:
                        self.quest_tree.add_children('bd2', [QuestNode('bd3', [3, 0, 0])])
                    if 'bd5' in self.quests_checklist:
                        self.quest_tree.add_children('bd2', [QuestNode('bd5', [3, 0, 0])])
                        if 'bd7' in self.quests_checklist and self.combat_area == 2:
                            self.quest_tree.add_children('bd5', [QuestNode('bd7', [5, 0, 0])])
                            if 'bd8' in self.quests_checklist:
                                self.quest_tree.add_children('bd7', [QuestNode('bd8', [2, 0, 0])])
                        if 'bw2' in self.quests_checklist:
                            self.quest_tree.add_children('bd5', [QuestNode('bw2', [5, 0, 0])])
                            if 'bw5' in self.quests_checklist:
                                self.quest_tree.add_children('bw2', [QuestNode('bw5', [5, 0, 0])])
                                if 'bw6' in self.quests_checklist and self.combat_area == 4:
                                    self.quest_tree.add_children('bw5', [QuestNode('bw6', [12, 0, 0])])
                                    #if 'bw8' in self.quests_checklist:
                                    #    self.quest_tree.add_children('bw6', [QuestNode('bw8', [1, 0, 0])])
                                    #    if 'bw9' in self.quests_checklist:
                                    #        self.quest_tree.add_children('bw8', [QuestNode('bw9', [2, 0, 0])])
                                if 'bw7' in self.quests_checklist and self.combat_area == 3 and (self.combat_subarea == 3 or self.combat_subarea == 4 or self.combat_subarea == 5):
                                        self.quest_tree.add_children('bw5', [QuestNode('bw7', [5, 0, 0])])
                    if 'bw1' in self.quests_checklist:
                        self.quest_tree.add_children('bd2', [QuestNode('bw1', [12, 0, 0])])
                        if 'bw4' in self.quests_checklist:
                            self.quest_tree.add_children('bw1', [QuestNode('bw4', [12, 0, 0])])
                            if 'bw10' in self.quests_checklist:
                                self.quest_tree.add_children('bw4', [QuestNode('bw10', [15, 0, 0])])
                    if 'bw3' in self.quests_checklist:
                        self.quest_tree.add_children('bd2', [QuestNode('bw3', [5, 0, 0])])
                if 'bd4' in self.quests_checklist:
                    self.quest_tree.add_children('bd1', [QuestNode('bd4', [3, 0, 0])])
                if 'bd6' in self.quests_checklist:
                    self.quest_tree.add_children('bd1', [QuestNode('bd6', [2, 0, 0])])
        # PvP quests
        if self.pvp_enabled:
            if 'c2' in self.quests_checklist:
                self.quest_tree.add_children('root', [QuestNode('c2', [0, 3, 0])])
                if 'c3' in self.quests_checklist:
                    self.quest_tree.add_children('c2', [QuestNode('c3', [0, 5, 0])])
                if 'c4' in self.quests_checklist:
                    self.quest_tree.add_children('c2', [QuestNode('c4', [0, 20, 0])])
            if 'c8' in self.quests_checklist:
                self.quest_tree.add_children('root', [QuestNode('c8', [0, 7, 0])])
        # Expedition quests
        if self.expeditions_enabled:
            if 'd2' in self.quests_checklist:
                self.quest_tree.add_children('root', [QuestNode('d2', [0, 0, 1])])
                if 'd3' in self.quests_checklist:
                    self.quest_tree.add_children('d2', [QuestNode('d3', [0, 0, 5])])
            if 'd4' in self.quests_checklist:
                self.quest_tree.add_children('root', [QuestNode('d4', [0, 0, 15])])
            if self.expeditions_tokyo_express:
                if 'd9' in self.quests_checklist:
                    self.quest_tree.add_children('root', [QuestNode('d9', [0, 0, 1])])
                    if 'd11' in self.quests_checklist:
                        self.quest_tree.add_children('d9', [QuestNode('d11', [0, 0, 7])])
        # Supply/Docking quests
        if self.combat_enabled:
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
                    children.extend(child.get_children_ids(target_id))
        return children

    def __repr__(self, depth=0):
        """
        For debug purposes.
        """
        text = "\t"*depth + self.id + "\n"
        for child in self.children:
            text += child.__repr__(depth + 1)
        return text
