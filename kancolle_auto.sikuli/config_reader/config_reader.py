import ConfigParser, datetime
from sikuli import *
from util import *

# Load the config.ini file
def get_config(settings, sleep_cycle):
    log_msg("Reading config file")
    # Change paths and read config.ini
    os.chdir(getBundlePath())
    os.chdir('..')
    config = ConfigParser.ConfigParser()
    config.read('config.ini')
    # Set user settings
    # 'General' section
    settings['program'] = config.get('General', 'Program')
    settings['recovery_method'] = config.get('General', 'RecoveryMethod')
    settings['jst_offset'] = config.getint('General', 'JSTOffset')
    sleep_cycle = config.getint('General', 'SleepCycle')
    # 'Scheduled Sleep' section
    if config.getboolean('ScheduledSleep', 'Enabled'):
        settings['scheduled_sleep_enabled'] = True
        settings['scheduled_sleep_start'] = "%04d"%config.getint('ScheduledSleep', 'StartTime')
        settings['scheduled_sleep_length'] = config.getfloat('ScheduledSleep', 'SleepLength')
    else:
        settings['scheduled_sleep_enabled'] = False
    # 'Scheduled Stop' section
    if config.getboolean('ScheduledStop', 'Enabled'):
        settings['scheduled_stop_enabled'] = True
        settings['scheduled_stop_type'] = config.get('ScheduledStop', 'Type')
        settings['scheduled_stop_count'] = config.getint('ScheduledStop', 'Count')
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
        log_success("Expeditions (%s) enabled!" % (', '.join('fleet %s: %s' % (key, settings['expedition_id_fleet_map'][key]) for key in sorted(settings['expedition_id_fleet_map'].keys()))))
    else:
        settings['expeditions_enabled'] = False
    # 'PvP' section
    if config.getboolean('PvP', 'Enabled'):
        settings['pvp_enabled'] = True
        settings['pvp_fleetcomp'] = config.getint('PvP', 'FleetComp')
    else:
        settings['pvp_enabled'] = False
    # 'Combat' section
    if config.getboolean('Combat', 'Enabled'):
        settings['combat_enabled'] = True
        settings['combat_fleetcomp'] = config.getint('Combat', 'FleetComp')
        settings['submarine_switch'] = config.getboolean('Combat', 'SubmarineSwitch')
        settings['combat_area'] = config.get('Combat', 'Area')
        settings['combat_subarea'] = config.get('Combat', 'Subarea')
        settings['combined_fleet'] = config.getboolean('Combat', 'CombinedFleet')
        if settings['combined_fleet']:
            # Remove fleet 2 from expedition list if combined fleet is enabled
            settings['expedition_id_fleet_map'].pop(2, None)
            # Disable PvP if combined fleet is enabled
            settings['pvp_enabled'] = False
            settings_check_valid_formations = ['combinedfleet_1', 'combinedfleet_2', 'combinedfleet_3', 'combinedfleet_4']
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
                exit()
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
        log_success("Combat enabled!")
    else:
        settings['combat_enabled'] = False
    # 'Quests' section
    settings['active_quests'] = config.get('Quests', 'Quests').replace(' ', '').split(',')
    settings['active_quests'].sort()
    if config.getboolean('Quests', 'Enabled') and len(settings['active_quests']) > 0:
        settings['quests_enabled'] = True
        settings['quests_check_schedule'] = config.getint('Quests', 'CheckSchedule')
    else:
        settings['quests_enabled'] = False
    log_success("Config loaded!")
    return settings, sleep_cycle
