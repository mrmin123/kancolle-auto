# Combat module
from sikuli import *
import datetime
from random import randint, choice
from util import *

Settings.OcrTextRead = True
Settings.MinSimilarity = 0.8

# Custom similarity thresholds
DMG_SIMILARITY = 0.7  # Damage state icons
FATIGUE_SIMILARITY = 0.98  # Fatigue state icons
CLASS_SIMILARITY = 0.7  # Ship class icons

class Combat:
    def __init__(self, kc_region, settings):
        self.next_sortie_time = datetime.datetime.now()
        self.kc_region = kc_region
        self.settings = settings
        self.submarine_switch = settings['submarine_switch']
        if self.submarine_switch:
            self.submarine_switch_subs = settings['submarine_switch_subs']
            self.submarine_switch_replace_limit = settings['submarine_switch_replace_limit']
            self.submarine_switch_fatigue_switch = settings['submarine_switch_fatigue_switch']
        self.area_num = settings['combat_area']
        self.subarea_num = settings['combat_subarea']
        self.area_pict = 'combat_area_%s.png' % settings['combat_area']
        self.subarea_pict = 'combat_panel_%s-%s.png' % (settings['combat_area'], settings['combat_subarea'])
        self.combined_fleet = settings['combined_fleet']
        self.nodes = settings['nodes']
        self.node_selects = settings['node_selects']
        self.formations = settings['formations']
        self.night_battles = settings['night_battles']
        self.retreat_limit = settings['retreat_limit']
        self.repair_limit = settings['repair_limit']
        self.repair_time_limit = settings['repair_time_limit']
        self.repair_timers = []
        self.check_fatigue = settings['check_fatigue']
        self.port_check = settings['port_check']
        self.medal_stop = settings['medal_stop']
        self.last_node_push = settings['last_node_push']
        self.lbas_enabled = settings['lbas_enabled']
        if self.lbas_enabled:
            self.lbas_groups = settings['lbas_groups']
            self.lbas_nodes = {}
            self.lbas_nodes[1] = settings['lbas_group_1_nodes']
            self.lbas_nodes[2] = settings['lbas_group_2_nodes']
            self.lbas_nodes[3] = settings['lbas_group_3_nodes']
        self.damage_counts = [0, 0, 0]

    # Tally and return number of ships of each damage state. Supports combined
    # fleets (add=True) as well as pre-sortie and post-sortie screens
    # (combat=False/True)
    def tally_damages(self, add=False, combat=False):
        log_msg("Checking fleet condition...")
        if not add:
            self.damage_counts = [0, 0, 0]
        # Define region to check damages for
        if combat:
            tally_damage_region = global_regions['check_damage_combat']
        else:
            tally_damage_region = global_regions['check_damage']
        # Tally light damages
        damage_matches = tally_damage_region.findAll(Pattern('dmg_light.png').similar(DMG_SIMILARITY))
        for i in (damage_matches if damage_matches is not None else []):
            self.damage_counts[0] += 1
        # Tally moderate damages
        damage_matches = tally_damage_region.findAll(Pattern('dmg_moderate.png').similar(DMG_SIMILARITY))
        for i in (damage_matches if damage_matches is not None else []):
            self.damage_counts[1] += 1
        # Tally critical damages
        damage_matches = tally_damage_region.findAll(Pattern('dmg_critical.png').similar(DMG_SIMILARITY))
        for i in (damage_matches if damage_matches is not None else []):
            self.damage_counts[2] += 1
        log_msg("Light damage: %d; moderate damage: %d; critical damage: %d" % (self.damage_counts[0], self.damage_counts[1], self.damage_counts[2]))
        return self.damage_counts

    # Return number of ships damaged above threshold; relies on tally_damages()
    # for a reliable count
    def count_damage_above_limit(self, limit_type):
        if limit_type == 'retreat':
            limit = self.retreat_limit
        elif limit_type == 'repair':
            limit = self.repair_limit
        count = 0
        for i, dmg_count in enumerate(self.damage_counts):
            if i >= limit:
                count += dmg_count
        return count

    # Checks whether or not ships are fatigued before sortieing. If they are,
    # the method returns the number of minutes kancolle-auto should wait before
    # attempting to sortie again
    def fatigue_check(self):
        log_msg("Checking fleet morale!")
        if global_regions['check_morale'].exists(Pattern('fatigue_high.png').similar(FATIGUE_SIMILARITY)):
            log_warning("Ship(s) with high fatigue found!")
            return 24
        elif global_regions['check_morale'].exists(Pattern('fatigue_med.png').similar(FATIGUE_SIMILARITY)):
            log_warning("Ship(s) with medium fatigue found!")
            return 12
        else:
            log_success("Ships have good morale!")
            return None

    # Wrapper method that calls on pre-sortie check methods
    def pre_sortie_check(self, add=False):
        # Tally damages
        self.tally_damages(add=add)
        # Check for resupply needs
        if (global_regions['check_resupply'].exists('resupply_alert.png') or global_regions['check_resupply'].exists('resupply_red_alert.png')):
            log_warning("Fleet needs resupply!")
            return False
        # Check fleet morale, if necessary
        if self.check_fatigue:
            fatigue_timer = self.fatigue_check()
            if fatigue_timer:
                log_warning("Fleet is fatigued! Sortie cancelled!")
                self.next_sortie_time_set(0, fatigue_timer)
                return False
        return True

    # Navigate to Sortie menu and click through sortie!
    # Returns tuple of booleans: (continue sorties?, sortie passed pre-check?)
    def go_sortie(self):
        continue_combat = True
        rejigger_mouse(self.kc_region, 50, 750, 0, 100)
        sleep(2)
        wait_and_click(self.kc_region, self.area_pict)
        rejigger_mouse(self.kc_region, 50, 750, 0, 100)
        if self.lbas_enabled:
            # If LBAS is enabled, resupply here
            self.lbas_resupply()
        if self.area_num == 'E':
            # Special logic for Event maps
            for page in range(1, int(self.subarea_num[0])):
                check_and_click(self.kc_region, '_event_next_page_' + str(page) + '.png')
                rejigger_mouse(self.kc_region, 50, 750, 0, 100)
                sleep(1)
            wait_and_click(self.kc_region, '_event_panel_' + self.subarea_num + '.png')
            sleep(1)
            if check_and_click(self.kc_region, 'event_start_screen_1.png'):
                sleep(1)
                check_and_click(self.kc_region, 'event_start_screen_2.png')
            else:
                check_and_click(self.kc_region, 'event_start_screen_2.png')
        else:
            # Logic
            # If an EO is specified, press the red EO arrow on the right
            if int(self.subarea_num) > 4:
                wait_and_click(self.kc_region, 'combat_panel_eo.png')
                rejigger_mouse(self.kc_region, 50, 750, 0, 100)
                sleep(1)
            wait_and_click(self.kc_region, self.subarea_pict)
        sleep(1)
        # Check if port is filled, if necessary
        if self.port_check:
            if self.kc_region.exists('combat_start_warning_shipsfull.png'):
                log_warning("Port is full! Please make some room for new ships! Sortie cancelled!")
                self.next_sortie_time_set(0, 15, 5)
                return (continue_combat, False)
        wait_and_click(self.kc_region, 'decision.png')
        sleep(1)
        rejigger_mouse(self.kc_region, 50, 750, 0, 400)
        # Always check port when deploying to Event maps
        if self.area_num == 'E':
            if self.kc_region.exists('combat_start_warning_shipsfull_event.png'):
                log_warning("Port is full for event! Please make some room for new ships! Sortie cancelled!")
                self.next_sortie_time_set(0, 15, 5)
                return (continue_combat, False)
        if self.combined_fleet:
            # If combined fleet, check damage and morale on both pages
            if not self.pre_sortie_check():
                return (continue_combat, False)
            check_and_click(global_regions['fleet_flags_sec'], 'fleet_2.png', expand_areas('fleet_id'))
            sleep_fast()
            if not self.pre_sortie_check(True):
                return (continue_combat, False)
            check_and_click(global_regions['fleet_flags_sec'], 'fleet_1.png', expand_areas('fleet_id'))
            sleep_fast()
        else:
            # If not combined fleet, check damage and morale only on Fleet 1
            if not self.pre_sortie_check():
                return (continue_combat, False)
        # Check fleet damage state
        if self.damage_counts[2] > 0:
            log_warning("Ship(s) in critical condition! Sortie cancelled!")
            return (continue_combat, False)
        if self.count_damage_above_limit('repair') > 0:
            log_warning("Ships (%d) in condition below repair threshold! Sortie cancelled!" % self.count_damage_above_limit('repair'))
            return (continue_combat, False)
        if not self.kc_region.exists(Pattern('combat_start_disabled.png').exact()):
            log_success("Commencing sortie!")
            if self.lbas_enabled and (len(self.lbas_nodes[1]) == 2 or len(self.lbas_nodes[2]) == 2 or len(self.lbas_nodes[3]) == 2):
                # If LBAS is enabled and sortie nodes are assigned, use the special LBAS
                # combat start button and assign LBAS groups to their assigned nodes
                wait_and_click(self.kc_region, 'combat_start_lbas.png')
                sleep(6)
                self.lbas_sortie()
            else:
                wait_and_click(self.kc_region, 'combat_start.png')
            sortie_underway = True
            nodes_run = 0
            fcf_retreated = False
            while sortie_underway:
                # Begin loop that checks for combat, formation select, night
                # battle prompt, or post-battle report screen
                self.loop_pre_combat(nodes_run)
                # Ended on resource nodes. Leave sortie.
                if check_and_click(global_regions['next'], 'next_alt.png', expand_areas('next')):
                    log_success("Sortie complete!")
                    sortie_underway = False
                    return (continue_combat, True)
                # If night battle prompt, proceed based on node and user config
                if self.kc_region.exists('combat_nb_retreat.png'):
                    if self.night_battles[nodes_run] == 'True':
                        # Commence and sleep through night battle
                        log_success("Commencing night battle!")
                        check_and_click(self.kc_region, 'combat_nb_fight.png')
                        while not global_regions['next'].exists('next.png'):
                            pass
                    else:
                        # Decline night battle
                        log_msg("Declining night battle!")
                        check_and_click(self.kc_region, 'combat_nb_retreat.png')
                # Click through post-battle report
                wait_and_click(global_regions['next'], 'next.png', 30, expand_areas('next'))
                sleep(3)
                # Tally damages at post-battle report screen
                while not self.kc_region.exists('post_combat_result_screen.png'):
                    # Additional check to make sure that we're seeing the damage states of ships,
                    # otherwise keep hitting next button until we get there
                    check_and_click(global_regions['next'], 'next.png', expand_areas('next'))
                    sleep(1)
                self.tally_damages(combat=True)
                # Check for medal reward, if enabled
                if self.medal_stop:
                    log_msg("Checking for medal reward!")
                    if self.kc_region.exists('medal.png'):
                        log_success("Medal obtained!")
                        continue_combat = False
                wait_and_click(global_regions['next'], 'next.png', 30, expand_areas('next'))
                rejigger_mouse(self.kc_region, 50, 750, 0, 100)
                sleep(3)
                if self.combined_fleet:
                    # If combined fleet, click through to the additional post-battle report screen and FCF
                    self.tally_damages(add=True, combat=True)
                    wait_and_click(global_regions['next'], 'next.png', 30, expand_areas('next'))
                    sleep(3)
                    if not self.kc_region.exists('combat_retreat.png'):
                        # Rudimentary check to dismiss ship reward before FCF screen (if applicable)
                        if check_and_click(global_regions['next'], 'next_alt.png', expand_areas('next')):
                            sleep(1)
                        if check_and_click(global_regions['next'], 'next.png', expand_areas('next')):
                            sleep(1)
                        sleep(3)
                    if self.kc_region.exists('fcf_check.png'):
                        # Only bother to retreat via FCF if only one ship is critically damaged,
                        # otherwise, continue with FCF and retreat normally
                        if self.damage_counts[2] == 1:
                            log_warning("Retreating ships via FCF!")
                            check_and_click(self.kc_region, 'fcf_retreat.png')
                            self.damage_counts[2] -= 1
                            fcf_retreated = True
                        else:
                            log_warning("%d ships are critically damaged; not retreating via FCF!" % self.damage_counts[2])
                            check_and_click(self.kc_region, 'fcf_continue.png')
                        sleep(2)
                # Check to see if we're at combat retreat/continue screen or item/ship reward screen(s)
                if not self.kc_region.exists('combat_retreat.png'):
                    sleep(2)
                    # If we're not at the home screen, the retreat screen, or the flagship retreat screen,
                    # click through reward(s)
                    while_count = 0
                    while not (self.kc_region.exists('menu_main_sortie.png') or
                               self.kc_region.exists('combat_flagship_dmg.png') or
                               self.kc_region.exists('combat_retreat.png')):
                        if check_and_click(global_regions['next'], 'next_alt.png', expand_areas('next')):
                            sleep(1)
                        if check_and_click(global_regions['next'], 'next.png', expand_areas('next')):
                            sleep(1)
                        while_count += 1
                        while_count_checker(self.kc_region, self.settings, while_count)
                # Check to see if we're at the flagship retreat screen
                if check_and_click(self.kc_region, 'combat_flagship_dmg.png'):
                    sleep(3)
                rejigger_mouse(self.kc_region, 370, 770, 100, 400)
                # Check to see if we're back at Home screen
                if self.kc_region.exists('menu_main_sortie.png'):
                    log_success("Sortie complete!")
                    sortie_underway = False
                    if fcf_retreated:
                        # If a ship was retreated using FCF, mod the damage counts properly to reflect this
                        self.damage_counts[2] += 1
                    return (continue_combat, True)
                # We ran a node, so increase the counter
                nodes_run += 1
                rejigger_mouse(self.kc_region, 50, 750, 0, 100)
                # Set next sortie time to soon in case we have no failures or additional nodes
                self.next_sortie_time_set(0, 0, 2)
                # If required number of nodes have been run, fall back
                if nodes_run >= self.nodes and not self.last_node_push:
                    log_msg("Ran the required number of nodes. Falling back!")
                    wait_and_click(self.kc_region, 'combat_retreat.png', 30)
                    sortie_underway = False
                    return (continue_combat, True)
                # If fleet is damaged, fall back
                if self.count_damage_above_limit('retreat') > 0 or self.damage_counts[2] > 0:
                    if nodes_run == self.nodes and self.last_node_push:
                        # Unless the PushLastNode flag is set, and we've ran the necessary nodes, then push!
                        pass
                    else:
                        log_warning("Ship(s) in condition at or below retreat threshold! Ceasing sortie!")
                        wait_and_click(self.kc_region, 'combat_retreat.png', 30)
                        sortie_underway = False
                        return (continue_combat, True)
                if nodes_run == self.nodes and self.last_node_push:
                    log_warning("Push to next node!")
                else:
                    log_msg("Continuing on to next node...")
                wait_and_click(self.kc_region, 'combat_nextnode.png', 30)
        else:
            if self.kc_region.exists('combat_nogo_repair.png'):
                log_warning("Cannot sortie due to ships under repair!")
                self.go_repair()
            elif self.kc_region.exists('combat_nogo_resupply.png'):
                log_warning("Cannot sortie due to ships needing resupply!")
            elif self.area_num == 'E' and self.kc_region.exists('combat_start_warning_shipsfull_event.png'):
                log_warning("Port is full for event! Please make some room for new ships! Sortie cancelled!")
                self.next_sortie_time_set(0, 15, 5)
        return (continue_combat, True)

    # Main master loop that occurs between all nodes. Handles compass spinning,
    # node selections, formation selections, as well as handling of whether or
    # not to proceed to next node or not
    def loop_pre_combat(self, nodes_run):
        # Check for compass, formation select, night battle prompt, or post-battle report
        loop_pre_combat_stop = False
        while not loop_pre_combat_stop:
            sleep_fast()
            # If compass, press it
            if check_and_click(self.kc_region, 'compass.png', expand_areas('compass')):
                log_msg("Spinning compass!")
                rejigger_mouse(self.kc_region, 50, 350, 0, 100)
                # Restart this loop in case there's another compass coming up
                sleep(5)
                self.loop_pre_combat(nodes_run)
                loop_pre_combat_stop = True
                break
            # Node select
            elif len(self.node_selects) > 0 and self.kc_region.exists('combat_node_select.png'):
                # Try all the nodes specified, since we don't know which one is active
                for node in self.node_selects:
                    check_and_click(self.kc_region, Pattern('%s.png' % node), expand_areas('node_select'))
                # Assume that the node was selected...
                rejigger_mouse(self.kc_region, 50, 350, 0, 100)
                sleep(3)
                self.loop_pre_combat(nodes_run)
                loop_pre_combat_stop = True
                break
            # If formation select, select formation based on user config
            elif nodes_run < len(self.formations) and check_and_click(global_regions['formation_%s' % self.formations[nodes_run]], 'formation_%s.png' % self.formations[nodes_run]):
                # Now check for night battle prompt or post-battle report
                log_msg("Selecting fleet formation!")
                sleep(8)
                mouseDown(Button.LEFT)  # In case of boss monologue
                mouseUp()
                rejigger_mouse(self.kc_region, 50, 350, 0, 100)
                sleep(5)
                self.loop_post_formation()
                loop_pre_combat_stop = True
                break
            elif (self.kc_region.exists('combat_nb_retreat.png') or
                  global_regions['next'].exists('next.png') or
                  global_regions['next'].exists('next_alt.png')):
                loop_pre_combat_stop = True
                break
            elif self.kc_region.exists('catbomb.png'):
                raise FindFailed('Catbombed during sortie :(')

    # Loop that runs after formation has been selected, indicating combat.
    # This loop runs until combat has concluded
    def loop_post_formation(self):
        while not (self.kc_region.exists('combat_nb_retreat.png') or
                   global_regions['next'].exists('next.png') or
                   global_regions['next'].exists('next_alt.png') or
                   self.kc_region.exists('catbomb.png')):
            pass
        # Check for catbomb
        if self.kc_region.exists('catbomb.png'):
            raise FindFailed('Catbombed during sortie :(')

    # On event map selection screen, segues into LBAS resupply interface and
    # resupplies desired air groups
    def lbas_resupply(self):
        menu_button = 'lbas_resupply_menu.png'
        menu_faded = 'lbas_resupply_menu_faded.png'
        # If event interface, look for the event-specific LBAS buttons
        if self.area_num == 'E':
            menu_button = 'lbas_resupply_menu_event.png'
            menu_faded = 'lbas_resupply_menu_event_faded.png'
        check_and_click(self.kc_region, menu_button)
        sleep(2)
        for lbas_group in self.lbas_groups:
            # Loop through active air support groups
            log_msg("Resupplying LBAS group %s!" % lbas_group)
            if lbas_group > 1:
                # Ony click the tab if it's not the first group
                check_and_click(self.kc_region, Pattern('lbas_group_tab_%s.png' % lbas_group).similar(0.95))
                sleep(1)
            if check_and_click(self.kc_region, 'lbas_resupply_button.png'):
                sleep(1)
                rejigger_mouse(self.kc_region, 50, 100, 50, 100)
                sleep(4)
        # Done resupplying
        check_and_click(self.kc_region, menu_faded)
        sleep(2)

    # Sends air groups out to desired nodes at beginning of sortie
    def lbas_sortie(self):
        for lbas_group in self.lbas_groups:
            # Only assign nodes if they were assigned to the LBAS group
            if len(self.lbas_nodes[lbas_group]) == 2:
                rejigger_mouse(self.kc_region, 350, 450, 0, 50)  # Clear the mouse from the LBAS screen
                log_msg("Assigning targets to LBAS group %s" % lbas_group)
                # Check to see if the first specified node exists on screen... because the LBAS screen might be covering it
                if not self.kc_region.exists('%s.png' % self.lbas_nodes[lbas_group][0]):
                    self.kc_region.mouseMove(self.kc_region.find('lbas_panel_switch.png'))
                    sleep(1)
                check_and_click(self.kc_region, '%s.png' % self.lbas_nodes[lbas_group][0], expand_areas('node_select'))
                sleep(1)
                # Check to see if the second specified node exists on screen... because the LBAS screen might be covering it
                if not self.kc_region.exists('%s.png' % self.lbas_nodes[lbas_group][1]):
                    self.kc_region.mouseMove(self.kc_region.find('lbas_panel_switch.png'))
                    sleep(1)
                check_and_click(self.kc_region, '%s.png' % self.lbas_nodes[lbas_group][1], expand_areas('node_select'))
                sleep(1)
                check_and_click(self.kc_region, 'lbas_assign_nodes.png')
        log_msg("LBAS groups ready with their assignments!")

    # Navigate to repair menu and repair any ship above damage threshold. Sets
    # next sortie time accordingly
    def go_repair(self):
        empty_docks = 0
        self.repair_timers = []
        rnavigation(self.kc_region, 'repair', self.settings)
        # Are there any pre-existing repairs happening?
        repair_timer_alt_matches = self.kc_region.findAll(Pattern('repair_timer_alt.png').similar(0.5))
        for i in (repair_timer_alt_matches if repair_timer_alt_matches is not None else []):
            repair_timer = check_timer(self.kc_region, i, 'l', 100)
            timer = self.timer_end(int(repair_timer[0:2]), int(repair_timer[3:5]) - 1)
            self.repair_timers.append(timer)
        # Set next sortie timer in case a ship in-fleet is already being repaired
        self.next_sortie_time_set()
        # Get number of empty/available docks
        repair_empty_matches = self.kc_region.findAll('repair_empty.png')
        for i in (repair_empty_matches if repair_empty_matches is not None else []):
            empty_docks += 1
        # Primary repair action (if dock is available)
        if empty_docks > 0:
            log_msg("Attempting to conduct repairs on %d ship(s)!" % self.count_damage_above_limit('repair'))
            repair_queue = empty_docks if self.count_damage_above_limit('repair') > empty_docks else self.count_damage_above_limit('repair')
            # If repairs are due, reset the next sortie time
            if repair_queue > 0:
                self.next_sortie_time_set(0, 0, 0, True)
            while empty_docks > 0 and repair_queue > 0:
                log_msg("Available docks: %d; repair queue: %d" % (empty_docks, repair_queue))
                repair_start = False
                wait_and_click(self.kc_region, 'repair_empty.png', 30)
                sleep(1)
                log_msg("Check for critically damaged ships.")
                if check_and_click(self.kc_region, Pattern('repair_dmg_critical.png').similar(0.95), expand_areas('repair_list')):
                    log_success("Starting repair on critically damaged ship!")
                    self.damage_counts[2] -= 1
                    repair_start = True
                if not repair_start and self.repair_limit <= 1:
                    log_msg("Check for moderately-damaged ships.")
                    if check_and_click(self.kc_region, Pattern('repair_dmg_moderate.png').similar(0.95), expand_areas('repair_list')):
                        log_success("Starting repair on moderately damaged ship!")
                        self.damage_counts[1] -= 1
                        repair_start = True
                if not repair_start and self.repair_limit == 0:
                    log_msg("Check for lightly-damaged ships.")
                    if check_and_click(self.kc_region, Pattern('repair_dmg_light.png').similar(0.95), expand_areas('repair_list')):
                        log_success("Starting repair on lightly damaged ship!")
                        self.damage_counts[0] -= 1
                        repair_start = True
                if repair_start:
                    repair_queue = empty_docks if self.count_damage_above_limit('repair') > empty_docks else self.count_damage_above_limit('repair')
                    sleep(1)
                    bucket_use = False
                    if self.repair_time_limit == 0:
                        # If set to use buckets for all repairs, no need to check timer
                        log_success("Using bucket for all repairs!")
                        self.kc_region.click('repair_bucket_switch.png')
                        self.next_sortie_time_set(0, 0)
                        bucket_use = True
                    else:
                        # Otherwise, act accordingly to timer and repair timer limit
                        repair_timer = check_timer(self.kc_region, 'repair_timer.png', 'r', 80, 5)
                        if int(repair_timer[0:2] + repair_timer[3:5]) >= self.repair_time_limit:
                            # Use bucket if the repair time is longer than desired
                            log_success("Repair time too long... using bucket!")
                            self.kc_region.click('repair_bucket_switch.png')
                            self.next_sortie_time_set(0, 0)
                            bucket_use = True
                        else:
                            # Try setting next sortie time according to repair timer
                            timer = self.timer_end(int(repair_timer[0:2]), int(repair_timer[3:5]) - 1)
                            log_success("Repair should be done at %s" % timer.strftime("%Y-%m-%d %H:%M:%S"))
                            self.next_sortie_time_set(int(repair_timer[0:2]), int(repair_timer[3:5]) - 1)
                            self.repair_timers.append(timer)
                            self.repair_timers.sort()
                            empty_docks -= 1
                    wait_and_click(self.kc_region, 'repair_start.png', 10)
                    wait_and_click(self.kc_region, 'repair_start_confirm.png', 10)
                    if bucket_use and self.count_damage_above_limit('repair') > 0:
                        sleep(7)
                    sleep_fast()
                log_msg("%d ships needing repairs left..." % self.count_damage_above_limit('repair'))
        else:
            log_warning("Cannot repair; docks are full. Checking back at %s!" % self.next_sortie_time.strftime("%Y-%m-%d %H:%M:%S"))
        # If submarine switching is enabled, run through it if repairs were required
        if self.submarine_switch:
            # Set fastest repair time (which might be a sub) as next sortie time to save time
            if len(self.repair_timers) > 0:
                self.next_sortie_time_set()
            if self.switch_sub():
                log_msg("Attempting to switch out submarines!")
                # If switch_subs() returns True (all ships being repaired are switched out)
                # empty repair_timers and set a fast next sortie time
                self.repair_timers = []
                self.next_sortie_time_set(0, 0, 2, True)

    def switch_sub(self):
        # See if it's possible to switch any submarines out
        rnavigation(self.kc_region, 'fleetcomp', self.settings)
        scan_list = ['fleetcomp_dmg_repair', 'dmg_critical']
        scan_list_status = {
            'fleetcomp_dmg_repair': False,
            'dmg_critical': False
        }
        scan_list_dict = {
            'fleetcomp_dmg_repair': 'under repair',
            'dmg_critical': 'critically damaged',
            'dmg_moderate': 'moderately damaged',
            'dmg_light': 'lightly damaged',
            'fatigue_high': 'highly fatigued',
            'fatigue_med': 'moderately fatigued'
        }
        similarity_dict = {
            'fleetcomp_dmg_repair': DMG_SIMILARITY,
            'dmg_critical': DMG_SIMILARITY,
            'dmg_moderate': DMG_SIMILARITY,
            'dmg_light': DMG_SIMILARITY,
            'fatigue_high': FATIGUE_SIMILARITY,
            'fatigue_med': FATIGUE_SIMILARITY
        }
        if isinstance(self.submarine_switch_replace_limit, int) and self.submarine_switch_replace_limit in [0, 1]:
            if self.submarine_switch_replace_limit <= 1:
                scan_list.append('dmg_moderate')
                scan_list_status['dmg_moderate'] = False
            if self.submarine_switch_replace_limit == 0:
                scan_list.append('dmg_light')
                scan_list_status['dmg_light'] = False
        if self.submarine_switch_fatigue_switch:
            scan_list.extend(['fatigue_high', 'fatigue_med'])
            # Set status of fatigue checks to True by default, so that even if these subs are not
            # replaced, it doesn't stop kancolle-auto from continuing sortie as long as damaged ships
            # have all been replaced
            scan_list_status['fatigue_high'] = True
            scan_list_status['fatigue_med'] = True
        for image in scan_list:
            ships_to_switch = 0
            ships_switched_out = 0
            shiplist_page = 1
            # Check each ship with specified repair/damage state
            image_matches = self.kc_region.findAll(Pattern('%s.png' % image).similar(similarity_dict[image]))
            for i in (image_matches if image_matches is not None else []):
                rejigger_mouse(self.kc_region, 50, 100, 50, 100)
                log_msg("Found ship that is %s!" % scan_list_dict[image])
                target_region = i.offset(Location(-170, -30)).right(195).below(110)
                ships_to_switch += 1
                if (target_region.exists(Pattern('ship_class_ss.png').similar(CLASS_SIMILARITY)) or
                        target_region.exists(Pattern('ship_class_ssv.png').similar(CLASS_SIMILARITY))):
                    log_msg("Ship is a submarine!")
                    target_region.click('fleetcomp_ship_switch_button.png')
                    self.kc_region.wait('fleetcomp_shiplist_sort_arrow.png')
                    sleep_fast()
                    # Make sure the sort order is correct
                    log_msg("Checking shiplist sort order and moving to first page if necessary!")
                    while_count = 0
                    while not self.kc_region.exists('fleetcomp_shiplist_sort_type.png'):
                        check_and_click(self.kc_region, 'fleetcomp_shiplist_sort_arrow.png')
                        sleep_fast()
                        while_count += 1
                        while_count_checker(self.kc_region, self.settings, while_count)
                    if shiplist_page == 1:
                        check_and_click(self.kc_region, 'fleetcomp_shiplist_first_page.png')
                    rejigger_mouse(self.kc_region, 50, 100, 50, 100)
                    # Sort through pages and find a sub that's not damaged/under repair
                    sub_chosen = False
                    sub_unavailable = False
                    saw_subs = False
                    while not sub_chosen and not sub_unavailable:
                        if self.kc_region.exists('fleetcomp_shiplist_submarine.png'):
                            log_msg("We are seeing available submarines!")
                            saw_subs = True
                        else:
                            if saw_subs:
                                # We're not seeing any more submarines in the shiplist...
                                log_warning("No more submarines!")
                                return False
                        for enabled_sub in self.submarine_switch_subs:
                            fleetcomp_shiplist_submarine_img = 'fleetcomp_shiplist_submarine_%s.png' % enabled_sub
                            fleetcomp_shiplist_submarine_img_matches = self.kc_region.findAll(Pattern(fleetcomp_shiplist_submarine_img).similar(0.95))
                            for sub in (fleetcomp_shiplist_submarine_img_matches if fleetcomp_shiplist_submarine_img_matches is not None else []):
                                self.kc_region.click(sub)
                                sleep(1)
                                if not self.kc_region.exists(Pattern('fleetcomp_shiplist_ship_switch_button.png').exact()):
                                    # The damaged sub can't be replaced with this subtype
                                    log_msg("Can't replace with this sub type!")
                                    check_and_click(self.kc_region, 'fleetcomp_shiplist_first_page.png')
                                    # This sub class can't be switched in, so break out of the for loop
                                    sleep_fast()
                                    break
                                if not (self.kc_region.exists(Pattern('dmg_moderate.png').similar(DMG_SIMILARITY)) or
                                        self.kc_region.exists(Pattern('dmg_critical.png').similar(DMG_SIMILARITY)) or
                                        self.kc_region.exists(Pattern('dmg_repair.png').similar(DMG_SIMILARITY))):
                                    # Submarine available. Switch it in!
                                    log_msg("Swapping submarines!")
                                    check_and_click(self.kc_region, 'fleetcomp_shiplist_ship_switch_button.png')
                                    ships_switched_out += 1
                                    sub_chosen = True
                                    sleep(1)
                                    break
                                else:
                                    # Submarine is damaged/under repair; click away
                                    log_msg("Submarine not available, moving on!")
                                    check_and_click(self.kc_region, 'fleetcomp_shiplist_first_page.png')
                                    sleep_fast()
                        # If we went through all the submarines on the shiplist page and haven't found a valid
                        # replacement, head to the next page (up to page 11 supported)
                        if not sub_chosen:
                            shiplist_page += 1
                            if shiplist_page < 12:
                                if check_and_click(self.kc_region, 'fleetcomp_shiplist_pg%s.png' % shiplist_page):
                                    sleep_fast()
                                    continue
                            # If we do not have any more available pages, we do not have any more available submarines
                            log_msg("No more ships to look at, moving on!")
                            check_and_click(self.kc_region, 'fleetcomp_shiplist_misc.png')
                            sub_unavailable = True
                else:
                    log_msg("Ship is not a submarine! Continuing!")
            if image_matches is None:
                # No matches; continue on
                scan_list_status[image] = True
                log_msg("No ships %s at the moment. Continuing..." % scan_list_dict[image])
            elif ships_to_switch == ships_switched_out:
                # Matches, with correct number of ships swapped out; continue on
                scan_list_status[image] = True
                log_success("All submarines (%s) successfully swapped out! Continuing!" % scan_list_dict[image])
        if False not in scan_list_status.itervalues():
            log_success("All submarines successfully swapped out! Continuing sorties!")
            return True
        else:
            log_warning("Not all ships under repairs are submarines, or not all submarines could not be swapped out! Waiting for repairs!")
            return False

    def __str__(self):
        return '%s' % self.next_sortie_time.strftime("%Y-%m-%d %H:%M:%S")

    # Set next sortie time; if the proposed time is longer than the previously
    # stored time, replace. Otherwise, keep the older (longer) one
    def next_sortie_time_set(self, hours=-1, minutes=-1, flex=0, override=False):
        if hours == -1 and minutes == -1:
            if len(self.repair_timers) > 0:
                self.repair_timers.sort()
                self.next_sortie_time = self.repair_timers[0]
            else:
                self.next_sortie_time = datetime.datetime.now()
        else:
            proposed_time = datetime.datetime.now() + datetime.timedelta(hours=hours, minutes=minutes + randint(0, flex))
            if override:
                self.next_sortie_time = proposed_time
            else:
                if proposed_time > self.next_sortie_time:
                    self.next_sortie_time = proposed_time

    def timer_end(self, hours, minutes):
        return datetime.datetime.now() + datetime.timedelta(hours=hours, minutes=minutes)


class PvP:
    def __init__(self, kc_region, settings):
        self.kc_region = kc_region
        self.settings = settings

    def go_pvp(self):
        enemy_ship_count = 0
        enemy_sub_count = 0

        # Select random pvp opponent
        random_choices = ['pvp_row_1.png', 'pvp_row_2.png']
        random_choice_one = choice(random_choices)
        random_choices.remove(random_choice_one)
        random_choice_two = random_choices[0]
        sleep(1)
        if not check_and_click(self.kc_region, random_choice_one, expand_areas('pvp_row')):
            if not check_and_click(self.kc_region, random_choice_two, expand_areas('pvp_row')):
                log_warning("No available PvP opponents!")
                return False
        # An opponent was chosen
        rejigger_mouse(self.kc_region, 50, 750, 50, 350)
        self.kc_region.wait('pvp_start_1.png', 30)
        sleep(1)

        # Identify opponent ship and sub counts
        enemy_ship_count_matches = self.kc_region.findAll(Pattern('pvp_lvl.png').similar(0.95))
        for i in (enemy_ship_count_matches if enemy_ship_count_matches is not None else []):
            enemy_ship_count += 1
        enemy_sub_count_matches = self.kc_region.findAll(Pattern('ship_class_ss.png'))
        for i in (enemy_sub_count_matches if enemy_sub_count_matches is not None else []):
            enemy_sub_count += 1
        enemy_sub_count_matches = self.kc_region.findAll(Pattern('ship_class_ssv.png'))
        for i in (enemy_sub_count_matches if enemy_sub_count_matches is not None else []):
            enemy_sub_count += 1
        formation, nb = self.formation_nb_selector(enemy_ship_count, enemy_sub_count)
        log_msg("Sortieing against %s ships (%s subs); deploying with %s formation!" % (enemy_ship_count, enemy_sub_count, formation[10:].replace('_', ' ')))

        # Continue sortie
        wait_and_click(self.kc_region, 'pvp_start_1.png', 30)
        wait_and_click(self.kc_region, 'pvp_start_2.png', 30)
        log_msg("Beginning PvP sortie!")
        rejigger_mouse(self.kc_region, 50, 350, 0, 100)
        sleep(2)
        wait_and_click(global_regions[formation], '%s.png' % formation, 30)
        rejigger_mouse(self.kc_region, 50, 750, 0, 100)
        while not (global_regions['next'].exists('next.png') or
                   self.kc_region.exists('combat_nb_fight.png')):
            pass
        if nb:
            check_and_click(self.kc_region, 'combat_nb_fight.png')
        else:
            check_and_click(self.kc_region, 'combat_nb_retreat.png')
        while not check_and_click(global_regions['next'], 'next.png', expand_areas('next')):
            pass
        sleep(2)
        while_count = 0
        while not self.kc_region.exists('menu_main_sortie.png'):
            check_and_click(global_regions['next'], 'next.png', expand_areas('next'))
            sleep_fast()
            while_count += 1
            while_count_checker(self.kc_region, self.settings, while_count)
        log_msg("PvP complete!")
        return True

    def formation_nb_selector(self, enemy_ship_count, enemy_sub_count):
        formation = 'formation_line_ahead'
        nb = True
        if enemy_ship_count == 0:
            # Return defaults if enemy ship count detection fails; avoid divide by 0
            return (formation, nb)
        sub_ratio = float(enemy_sub_count) / float(enemy_ship_count)
        if sub_ratio > 0.5:
            formation = 'formation_line_abreast'
        elif sub_ratio == 0.5:
            formation = 'formation_diamond'
        if sub_ratio == 1:
            nb = False  # Skip night battle if the entire enemy fleet are subs
        return (formation, nb)


class FleetcompSwitcher:
    def __init__(self, kc_region, settings):
        self.kc_region = kc_region
        self.settings = settings

    def switch_fleetcomp(self, fleetcomp):
        # Navigate to the fleetcomp page, then enter the fleetcomp screen
        rnavigation(self.kc_region, 'fleetcomp', self.settings)
        wait_and_click(self.kc_region, 'fleetcomp_preset_screen_button.png', 30)
        self.kc_region.wait('fleetcomp_preset_switch_button_offset.png', 30)
        # the button_offset image is located 50 pixels above the first button,
        # and each subsequent buttons are situated 52 pixels apart vertically
        target_button = Pattern('fleetcomp_preset_switch_button_offset.png').targetOffset(randint(-15, 15), 50 + (52 * (fleetcomp - 1)) + randint(-8, 8))
        self.kc_region.click(target_button)
