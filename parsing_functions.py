"""
    Lil' parsing functions that aim to parse infos from 1 line of log.
"""
#! /usr/bin/env python3

from datetime import timedelta

from overlog_consts import *


def get_struct_combat_line(combat_log_matched):
    """
        Parameter : matched regex from COMBAT_PATTERN
        Return : a structured dict
    """
    # Unpacking the log line and preparing the structured dict
    struct_log = {
        "time": combat_log_matched.group("time"),
        "damages": (int)(combat_log_matched.group("damages")),
        "damage_taker": combat_log_matched.group("dude_hurt"),
        "dtaker_is_mob": False,
        "damage_dealer": combat_log_matched.group("damage_dealer"),
        "ddealer_is_mob": False,
        "crit": False,
        "heal": False,
    }

    # Updating the struct with some specifics :
    if "(Critical)" in struct_log["damage_dealer"]:
        struct_log["crit"] = True
        struct_log["damage_dealer"] = "".join(struct_log["damage_dealer"].split()[:-1])

    if "(" in struct_log["damage_dealer"]:
        # Players are not allowed to have parenthesis in their name
        # (see Riley's post on the forum)
        struct_log["ddealer_is_mob"] = True
        if "(" in struct_log["damage_taker"]:
            # A mob can't hit another mob so this is certainly a bugged line where
            # the player is only identified by an id but no name...
            # This is often the case when the hit killed the player (however we can't
            # identify the player with this id since it's randomized and the mapping
            # player <-> id is never shown elsewhere...
            #
            #
            # This also take care of some other weird cases where an object hit a mob
            # (like lever in sewers) but we don't care about it anyways so we ignore
            # the line.
            return None

    if "(" in struct_log["damage_taker"]:
        # Players are not allowed to have parenthesis in their name
        # (see Riley's post on the forum)
        struct_log["dtaker_is_mob"] = True

    if struct_log["damages"] < 0:
        struct_log["heal"] = True
        struct_log["damages"] = -struct_log["damages"]

    # if "Unknown" in struct_log["damage_dealer"]:
    # Another bug...
    # This happens (at least) when everybody gets hit
    # on the last raid boss when a circle wasn't correctly filled
    # We ignore for now and pretend that "Unknown" is a mob since
    # it's still interesting that we add those damages to total rcv
    # dmgs.

    return struct_log


def get_timedelta_from_matched(matched):
    """
        This func parse the line passed in param to get the time
        Return : A handy timedelta to allow easy operations.
    """
    time_l = matched["time"].split(":")
    hour = (int)(time_l[0])
    minu = (int)(time_l[1])
    sec = (int)(time_l[2])
    milsec = (int)(time_l[3])

    return timedelta(hours=hour, minutes=minu, seconds=sec, milliseconds=milsec)


# pylint: disable=too-many-return-statements
def get_parsed_line(line):
    """
        Pass the line to parse in parameter.

        Return: The type of the log line and its parsed content (and
        structured when necessary (on combat for example)).
    """

    combat_log_matched = re.match(COMBAT_PATTERN, line)
    if combat_log_matched:
        return "combat", get_struct_combat_line(combat_log_matched)

    xp_log_matched = re.match(XP_PATTERN, line)
    if xp_log_matched:
        return "xp", (int)(xp_log_matched["pts"])

    dram_log_matched = re.match(DRAM_PATTERN, line)
    if dram_log_matched:
        return "dram", (int)(dram_log_matched["pts"])

    rep_log_matched = re.match(REP_PATTERN, line)
    if rep_log_matched:
        return "rep", (int)(rep_log_matched["pts"])

    loot_log_matched = re.match(LOOT_PATTERN, line)
    if loot_log_matched:
        return "loots", loot_log_matched["loot"]

    entered_log_matched = re.match(ENTER_COMBAT_PATTERN_TIME, line)
    if entered_log_matched:
        return "entered_combat", get_timedelta_from_matched(entered_log_matched)

    exited_log_matched = re.match(EXIT_COMBAT_PATTERN_TIME, line)
    if exited_log_matched:
        return "exited_combat", get_timedelta_from_matched(exited_log_matched)

    if "Dungeon Completed" in line:
        return "dung", 1

    return None, None


def update_stats_superdict_for_rcv_dmgs(infos, super_dict):
    """
        Updating the super_dict with dmgs received by players
    """
    try:
        super_dict["overall_combat_stats"]["rcv_dmgs"][infos["damage_taker"]] += infos[
            "damages"
        ]
    except KeyError:
        super_dict["overall_combat_stats"]["rcv_dmgs"][infos["damage_taker"]] = infos[
            "damages"
        ]
    if infos["crit"]:
        # We start by filling the healer's infos
        try:
            super_dict["overall_combat_stats"]["rcv_crit_dmgs"][
                infos["damage_taker"]
            ] += infos["damages"]
        except KeyError:
            super_dict["overall_combat_stats"]["rcv_crit_dmgs"][
                infos["damage_taker"]
            ] = infos["damages"]
    return super_dict


def update_stats_superdict_for_dmgs(infos, super_dict):
    """
        Updating the super_dict with dmgs done by players
    """
    try:
        super_dict["overall_combat_stats"]["dmgs"][infos["damage_dealer"]] += infos[
            "damages"
        ]
    except KeyError:
        super_dict["overall_combat_stats"]["dmgs"][infos["damage_dealer"]] = infos[
            "damages"
        ]
    if infos["crit"]:
        # We start by filling the healer's infos
        try:
            super_dict["overall_combat_stats"]["crit_dmgs"][
                infos["damage_dealer"]
            ] += infos["damages"]
        except KeyError:
            super_dict["overall_combat_stats"]["crit_dmgs"][
                infos["damage_dealer"]
            ] = infos["damages"]
    return super_dict


def update_stats_superdict_for_heal(infos, super_dict):
    """
        Updating the super_dict with healing infos
    """
    # We start by filling the healer's infos
    try:
        super_dict["overall_combat_stats"]["heals"][infos["damage_dealer"]] += infos[
            "damages"
        ]
    except KeyError:
        super_dict["overall_combat_stats"]["heals"][infos["damage_dealer"]] = infos[
            "damages"
        ]
    # Then we fill the healed guy's infos
    try:
        super_dict["overall_combat_stats"]["rcv_heals"][infos["damage_taker"]] += infos[
            "damages"
        ]
    except KeyError:
        super_dict["overall_combat_stats"]["rcv_heals"][infos["damage_taker"]] = infos[
            "damages"
        ]
    if infos["crit"]:
        # We start by filling the healer's infos
        try:
            super_dict["overall_combat_stats"]["crit_heals"][
                infos["damage_dealer"]
            ] += infos["damages"]
        except KeyError:
            super_dict["overall_combat_stats"]["crit_heals"][
                infos["damage_dealer"]
            ] = infos["damages"]
        # Then we fill the healed guy's infos
        try:
            super_dict["overall_combat_stats"]["rcv_crit_heals"][
                infos["damage_taker"]
            ] += infos["damages"]
        except KeyError:
            super_dict["overall_combat_stats"]["rcv_crit_heals"][
                infos["damage_taker"]
            ] = infos["damages"]
    return super_dict


def update_stats_superdict_with_combat(infos, super_dict):
    """
        Handling combat infos is convulated enough to get
        its own func

        This func stores the infos in the actual super dict
        (this must handle a lot of cases)
    """
    """
        Must leverage this :

        struct_log = {
            "time": combat_log_matched.group("time"),
            "damages": (int)(combat_log_matched.group("damages")),
            "damage_taker": combat_log_matched.group("dude_hurt"),
            "dtaker_is_mob": False,
            "damage_dealer": combat_log_matched.group("damage_dealer"),
            "ddealer_is_mob": False,
            "crit": False,
            "heal": False,
        }
    """
    # First we handle the easiest : Overall stats
    """
        "overall_combats_stats": {
            "dmgs": {
                "player1": 121,
                "player2": 222,
            }
            "crit_dmgs": {},
            "heals": {},
            "crit_heals": {},
            "rcv_dmgs": {},
            "rcv_heals": {},
            "rcv_crit_dmgs": {},
            "rcv_crit_heals": {},
        },
    """
    if not infos:
        return super_dict

    if infos["dtaker_is_mob"] and infos["ddealer_is_mob"]:
        # We are not interested in mobs killing other mobs
        # Ignoring...
        # For dev curiousity, we still print it for now
        # TODO: suppr this print
        print(infos)
        return super_dict

    if infos["heal"]:
        return update_stats_superdict_for_heal(infos, super_dict)

    if infos["dtaker_is_mob"]:
        return update_stats_superdict_for_dmgs(infos, super_dict)

    if infos["ddealer_is_mob"]:
        return update_stats_superdict_for_rcv_dmgs(infos, super_dict)

    return super_dict


def build_stats_superdict(line, super_dict):
    """
        This is the core "logic" of this script

        From a parsed line (returned by 'get_parsed_line')
        Deduce actual stats from the parsed lines and
        add them to the super final dict

        The dict should be structured as :
        super_dict = {
            "current_combats": {
                "Monster1": {
                    "dmgs": {
                        "player1": (10 (dmgs), 2 (hits))
                        "player2": (10 (dmgs), 2 (hits)),
                    }
                    "heals": {
                        "player1": 10,
                        "player2": 13,
                    }
                }
            }
            "Dungeon1": {
                "Monster1": {
                    "All": {
                        "player1": dmgs,
                        "player2": dmgs,
                    }
                }
            }
            "overall_combats_stats": {
                "dmgs": {
                    "player1": 121,
                    "player2": 222,
                }
                "crit_dmgs": {},
                "heals": {},
                "crit_heals": {},
                "rcv_dmgs": {},
            },
            "dung_nbr": 0,
            "xp": 0,
            "rep": 0,
            "dram": 0,
            "loots": [],
            "current_combat_time": timedelta(0),
            "overall_combat_time": timedelta(0),
        }
    """

    line_type, line_infos = get_parsed_line(line)

    # TODO: Add number of hits
    # TODO: Add details per dungeons/mobs/players
    if not line_type:
        return super_dict

    if line_type in ("xp", "dram", "rep"):
        super_dict[line_type] = super_dict[line_type] + line_infos
        return super_dict

    if line_type == "loots":
        super_dict[line_type].append(line_infos)
        return super_dict

    if line_type == "dung":
        # The is a dungeon completion line
        # We assume that what was before that was in the dungeon
        # We store that un dungeonX and clean the current_combats dict
        super_dict["dung_nbr"] = super_dict["dung_nbr"] + 1
        super_dict["Dungeon" + str(super_dict["dung_nbr"])] = super_dict[
            "current_combats"
        ]
        super_dict["current_combats"] = dict()
        return super_dict

    if line_type == "entered_combat":
        super_dict["current_combat_time"] = line_infos
        return super_dict

    if line_type == "exited_combat":
        if super_dict["current_combat_time"] == timedelta(0):
            # The logfile is certainly not complete and we found out that
            # the player left a combat without starting it on the first place
            return super_dict
        super_dict["overall_combat_time"] = super_dict["overall_combat_time"] + (
            line_infos - super_dict["current_combat_time"]
        )
        super_dict["current_combat_time"] = timedelta(0)
        return super_dict

    if line_type == "combat":
        return update_stats_superdict_with_combat(line_infos, super_dict)

    return super_dict
