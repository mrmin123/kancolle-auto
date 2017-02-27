# Config-reader module
import ConfigParser, sys
from sikuli import *
from util import *


# Load the config.ini file
def get_config(settings, sleep_cycle):
    log_msg("Reading config file!")
    # Change paths and read config.ini
    os.chdir(getBundlePath())
    os.chdir('..')
    config = ConfigParser.ConfigParser()
    config.read('config.ini')
    # Set user settings
    # 'General' section
    settings['program'] = config.get('General', 'Program')
    settings['recovery_method'] = config.get('General', 'RecoveryMethod')
    settings['basic_recovery'] = config.getboolean('General', 'BasicRecovery')
    settings['jst_offset'] = config.getint('General', 'JSTOffset')
    sleep_cycle = config.getint('General', 'SleepCycle')
    # 'Scheduled Sleep' section
    if config.getboolean('ScheduledSleep', 'Enabled'):
        settings['scheduled_sleep_enabled'] = True
        settings['scheduled_sleep_start'] = "%04d" % config.getint('ScheduledSleep', 'StartTime')
        settings['scheduled_sleep_length'] = config.getfloat('ScheduledSleep', 'SleepLength')
        log_msg("Scheduled Sleep enabled: ~%s hours starting at ~%s" % (settings['scheduled_sleep_length'], settings['scheduled_sleep_start']))
    else:
        settings['scheduled_sleep_enabled'] = False
    # 'Scheduled Stop' section
    if config.getboolean('ScheduledStop', 'Enabled'):
        settings['scheduled_stop_enabled'] = True
        settings['scheduled_stop_mode'] = config.get('ScheduledStop', 'Mode').lower()
        if (settings['scheduled_stop_mode'] not in ['time', 'expedition', 'sortie', 'pvp']):
            log_error("'%s' is not a scheduled stop mode! Please check your config file." % settings['scheduled_stop_mode'])
            sys.exit()
        settings['scheduled_stop_count'] = config.getint('ScheduledStop', 'Count')
        log_msg("Scheduled Stop enabled: %s (%s)" % (settings['scheduled_stop_count'], settings['scheduled_stop_mode']))
    else:
        settings['scheduled_stop_enabled'] = False
    # 'Expeditions' section
    if config.getboolean('Expeditions', 'Enabled'):
        settings['expeditions_enabled'] = True
        if config.get('Expeditions', 'Fleet2'):
            settings['expedition_id_fleet_map'][2] = config.getint('Expeditions', 'Fleet2')
        if config.get('Expeditions', 'Fleet3'):
            settings['expedition_id_fleet_map'][3] = config.getint('Expeditions', 'Fleet3')
        if config.get('Expeditions', 'Fleet4'):
            settings['expedition_id_fleet_map'][4] = config.getint('Expeditions', 'Fleet4')
        log_msg("Expeditions enabled: %s" % (', '.join('fleet %s: %s' % (key, settings['expedition_id_fleet_map'][key]) for key in sorted(settings['expedition_id_fleet_map'].keys()))))
    else:
        settings['expeditions_enabled'] = False
    # 'PvP' section
    if config.getboolean('PvP', 'Enabled'):
        settings['pvp_enabled'] = True
        settings['pvp_fleetcomp'] = config.getint('PvP', 'FleetComp')
        log_msg("Combat enabled (PvP mode)")
    else:
        settings['pvp_enabled'] = False
    # 'Combat' section
    if config.getboolean('Combat', 'Enabled'):
        settings['combat_enabled'] = True
        settings['combat_fleetcomp'] = config.getint('Combat', 'FleetComp')
        settings['combat_area'] = config.get('Combat', 'Area')
        settings['combat_subarea'] = config.get('Combat', 'Subarea')
        settings['combined_fleet'] = config.getboolean('Combat', 'CombinedFleet')
        if settings['combined_fleet']:
            # Remove fleet 2 from expedition list if combined fleet is enabled
            settings['expedition_id_fleet_map'].pop(2, None)
            # Disable PvP if combined fleet is enabled
            settings['pvp_enabled'] = False
            settings_check_valid_formations = ['combinedfleet_1', 'combinedfleet_2', 'combinedfleet_3', 'combinedfleet_4']
            settings_check_valid_formations += ['line_ahead', 'double_line', 'diamond', 'echelon', 'line_abreast', ]
            settings_check_filler_formation = 'combinedfleet_4'
        else:
            settings_check_valid_formations = ['line_ahead', 'double_line', 'diamond', 'echelon', 'line_abreast', ]
            settings_check_filler_formation = 'line_ahead'
        settings['nodes'] = config.getint('Combat', 'Nodes')
        settings['node_selects'] = config.get('Combat', 'NodeSelects').replace(' ', '').split(',')
        if '' in settings['node_selects']:
            settings['node_selects'].remove('')
        settings['formations'] = config.get('Combat', 'Formations').replace(' ', '').split(',')
        # Check that supplied formations are valid
        for formation in settings['formations']:
            if formation not in settings_check_valid_formations:
                log_error("'%s' is not a valid formation! Please check your config file." % formation)
                sys.exit()
        if len(settings['formations']) < settings['nodes']:
            settings['formations'].extend([settings_check_filler_formation] * (settings['nodes'] - len(settings['formations'])))
        settings['night_battles'] = config.get('Combat', 'NightBattles').replace(' ', '').split(',')
        if len(settings['night_battles']) < settings['nodes']:
            settings['night_battles'].extend(['True'] * (settings['nodes'] - len(settings['night_battles'])))
        settings['retreat_limit'] = config.getint('Combat', 'RetreatLimit')
        settings['repair_limit'] = config.getint('Combat', 'RepairLimit')
        settings['repair_time_limit'] = config.getint('Combat', 'RepairTimeLimit')
        settings['check_fatigue'] = config.getboolean('Combat', 'CheckFatigue')
        settings['port_check'] = config.getboolean('Combat', 'PortCheck')
        settings['medal_stop'] = config.getboolean('Combat', 'MedalStop')
        settings['last_node_push'] = config.getboolean('Combat', 'LastNodePush')
        log_msg("Combat enabled (sortie mode): sortieing to %s-%s" % (settings['combat_area'], settings['combat_subarea']))
    else:
        settings['combat_enabled'] = False
    # 'SubmarineSwitch' section
    if config.getboolean('SubmarineSwitch', 'Enabled') and settings['combat_enabled']:
        settings['submarine_switch'] = True
        settings_check_valid_subs = ['all', 'i-8', 'i-8-kai', 'i-13', 'i-14', 'i-19', 'i-19-kai', 'i-26', 'i-26-kai', 'i-58', 'i-58-kai', 'i-168', 'i-401', 'maruyu', 'ro-500', 'u-511']
        settings['submarine_switch_subs'] = config.get('SubmarineSwitch', 'EnabledSubs').replace(' ', '').lower().split(',')
        try:
            settings['submarine_switch_replace_limit'] = config.getint('SubmarineSwitch', 'ReplaceLimit')
        except ValueError:
            settings['submarine_switch_replace_limit'] = None
        # If 'submarines' is specified, disregard the other specified options
        if 'all' in settings['submarine_switch_subs']:
            settings['submarine_switch_subs'] = ['i-8', 'i-19', 'i-26', 'i-58', 'i-168', 'maruyu', 'ro-500', 'u-511']
        for sub in settings['submarine_switch_subs']:
            if sub not in settings_check_valid_subs:
                log_error("'%s' is not a valid sub selection! Please check your config file." % formation)
                sys.exit()
        log_msg("Submarine Switch enabled")
    else:
        settings['submarine_switch'] = False
    # 'LBAS' section
    if config.getboolean('LBAS', 'Enabled') and settings['combat_enabled']:
        settings['lbas_enabled'] = True
        settings['lbas_groups'] = config.get('LBAS', 'EnabledGroups').replace(' ', '').split(',')
        if (len(settings['lbas_groups']) < 1):
            log_error("If LBAS is enabled, you must specify at least one active LBAS group")
            sys.exit()
        else:
            for i, val in enumerate(settings['lbas_groups']):
                settings['lbas_groups'][i] = int(val)
        settings['lbas_groups'].sort()
        settings['lbas_group_1_nodes'] = config.get('LBAS', 'Group1Nodes').replace(' ', '').split(',')
        if (1 in settings['lbas_groups'] and (settings['lbas_group_1_nodes'] != [''] and len(settings['lbas_group_1_nodes']) != 2)):
            log_error("You must specify zero (0) or two (2) nodes for active LBAS group 1!")
            sys.exit()
        settings['lbas_group_2_nodes'] = config.get('LBAS', 'Group2Nodes').replace(' ', '').split(',')
        if (2 in settings['lbas_groups'] and (settings['lbas_group_2_nodes'] != [''] and len(settings['lbas_group_2_nodes']) != 2)):
            log_error("You must specify zero (0) or two (2) nodes for active LBAS group 2!")
            sys.exit()
        settings['lbas_group_3_nodes'] = config.get('LBAS', 'Group3Nodes').replace(' ', '').split(',')
        if (3 in settings['lbas_groups'] and (settings['lbas_group_3_nodes'] != [''] and len(settings['lbas_group_3_nodes']) != 2)):
            log_error("You must specify zero (0) or two (2) nodes for active LBAS group 3!")
            sys.exit()
        log_msg("LBAS enabled: groups %s" % ', '.join(str(group) for group in settings['lbas_groups']))
    else:
        settings['lbas_enabled'] = False
    # 'Quests' section
    settings['active_quests'] = config.get('Quests', 'Quests').replace(' ', '').split(',')
    settings['active_quests'].sort()
    if config.getboolean('Quests', 'Enabled') and len(settings['active_quests']) > 0:
        settings['quests_enabled'] = True
        settings['quests_check_schedule'] = config.getint('Quests', 'CheckSchedule')
        log_msg("Quests enabled")
    else:
        settings['quests_enabled'] = False
    return settings, sleep_cycle
