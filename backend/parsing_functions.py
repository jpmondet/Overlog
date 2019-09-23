"""
    Lil' parsing functions that aim to parse infos from 1 line of log.
"""
#! /usr/bin/env python3

from datetime import timedelta
from time import sleep

# pylint: disable=wildcard-import,unused-wildcard-import
from backend.overlog_consts import *

# pylint: disable=bad-continuation, fixme


def get_struct_combat_line(combat_log_matched):
    """
        Parameter : matched regex from COMBAT_PATTERN
        Return : a structured dict
    """
    # Unpacking the log line and preparing the structured dict
    struct_log = {
        "id_ddealer": 0,
        "id_dtaker": 0,
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
    if (
        "(Critical)" in struct_log["damage_dealer"]
        or "(Crushing)" in struct_log["damage_dealer"]
    ):
        struct_log["crit"] = True
        struct_log["damage_dealer"] = "".join(
            struct_log["damage_dealer"].split()[:-1]
        )

    if "(" in struct_log["damage_dealer"]:
        # Players are not allowed to have parenthesis in their name
        # (see Riley's post on the forum)
        struct_log["ddealer_is_mob"] = True
        # TODO: Replace this 'id' extraction by a better regex pattern
        splitted_name = struct_log["damage_dealer"].split("(")
        struct_log["id_ddealer"] = (int)("".join(splitted_name[-1])[:-1])
        struct_log["damage_dealer"] = "".join(splitted_name[0])

    if "(" in struct_log["damage_taker"]:
        # Players are not allowed to have parenthesis in their name
        # (see Riley's post on the forum)
        # BUG: We know for a fact that when a player die, there is no name, only an id
        # Ignoring for now..
        struct_log["dtaker_is_mob"] = True
        splitted_name = struct_log["damage_taker"].split("(")
        struct_log["id_dtaker"] = (int)("".join(splitted_name[-1])[:-1])
        struct_log["damage_taker"] = "".join(splitted_name[0])
        if not struct_log["damage_taker"]:
            print(combat_log_matched)

    if struct_log["damages"] < 0:
        struct_log["heal"] = True
        struct_log["damages"] = -struct_log["damages"]

    # if "Unknown" in struct_log["damage_dealer"]:
    # Another bug...
    # This happens (at least) when everybody gets hit
    # on the last raid boss when a circle wasn't correctly filled
    # We ignore for now and pretend that "Unknown" is a mob since
    # it's still interesting that we add those damages to total rcv
    # dmgs of a player.

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

    return timedelta(
        hours=hour, minutes=minu, seconds=sec, milliseconds=milsec
    )


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
        return (
            "entered_combat",
            get_timedelta_from_matched(entered_log_matched),
        )

    exited_log_matched = re.match(EXIT_COMBAT_PATTERN_TIME, line)
    if exited_log_matched:
        return "exited_combat", get_timedelta_from_matched(exited_log_matched)

    if "Dungeon Completed" in line:
        return "dung", 1

    return None, None


# TODO: Maybe merge those very similar update functions
def update_stats_superdict_for_rcv_dmgs(infos, super_dict):
    """
        Updating the super_dict with dmgs received by players
    """
    try:
        super_dict["overall_combat_stats"]["rcv_dmgs"][infos["damage_taker"]][
            "tot"
        ] += infos["damages"]
        super_dict["overall_combat_stats"]["rcv_dmgs"][infos["damage_taker"]][
            "hits"
        ] += 1
    except KeyError:
        super_dict["overall_combat_stats"]["rcv_dmgs"][
            infos["damage_taker"]
        ] = {"tot": infos["damages"], "hits": 1}
    if infos["crit"]:
        # We start by filling the healer's infos
        try:
            super_dict["overall_combat_stats"]["rcv_crit_dmgs"][
                infos["damage_taker"]
            ]["tot"] += infos["damages"]
            super_dict["overall_combat_stats"]["rcv_crit_dmgs"][
                infos["damage_taker"]
            ]["hits"] += 1
        except KeyError:
            super_dict["overall_combat_stats"]["rcv_crit_dmgs"][
                infos["damage_taker"]
            ] = {"tot": infos["damages"], "hits": 1}
    return super_dict


def update_stats_superdict_for_dmgs(infos, super_dict):
    """
        Updating the super_dict with dmgs done by players
    """
    try:
        super_dict["overall_combat_stats"]["dmgs"][infos["damage_dealer"]][
            "tot"
        ] += infos["damages"]
        super_dict["overall_combat_stats"]["dmgs"][infos["damage_dealer"]][
            "hits"
        ] += 1
    except KeyError:
        super_dict["overall_combat_stats"]["dmgs"][infos["damage_dealer"]] = {
            "tot": infos["damages"],
            "hits": 1,
        }
    if infos["crit"]:
        # We start by filling the healer's infos
        try:
            super_dict["overall_combat_stats"]["crit_dmgs"][
                infos["damage_dealer"]
            ]["tot"] += infos["damages"]
            super_dict["overall_combat_stats"]["crit_dmgs"][
                infos["damage_dealer"]
            ]["hits"] += 1
        except KeyError:
            super_dict["overall_combat_stats"]["crit_dmgs"][
                infos["damage_dealer"]
            ] = {"tot": infos["damages"], "hits": 1}
    return super_dict


def update_stats_superdict_for_heal(infos, super_dict):
    """
        Updating the super_dict with healing infos
    """
    # We start by filling the healer's infos
    try:
        super_dict["overall_combat_stats"]["heals"][infos["damage_dealer"]][
            "tot"
        ] += infos["damages"]
        super_dict["overall_combat_stats"]["heals"][infos["damage_dealer"]][
            "hits"
        ] += 1
    except KeyError:
        super_dict["overall_combat_stats"]["heals"][infos["damage_dealer"]] = {
            "tot": infos["damages"],
            "hits": 1,
        }
    # Then we fill the healed guy's infos
    try:
        super_dict["overall_combat_stats"]["rcv_heals"][infos["damage_taker"]][
            "tot"
        ] += infos["damages"]
        super_dict["overall_combat_stats"]["rcv_heals"][infos["damage_taker"]][
            "hits"
        ] += 1
    except KeyError:
        super_dict["overall_combat_stats"]["rcv_heals"][
            infos["damage_taker"]
        ] = {"tot": infos["damages"], "hits": 1}
    if infos["crit"]:
        # We start by filling the healer's infos
        try:
            super_dict["overall_combat_stats"]["crit_heals"][
                infos["damage_dealer"]
            ]["tot"] += infos["damages"]
            super_dict["overall_combat_stats"]["crit_heals"][
                infos["damage_dealer"]
            ]["hits"] += 1
        except KeyError:
            super_dict["overall_combat_stats"]["crit_heals"][
                infos["damage_dealer"]
            ] = {"tot": infos["damages"], "hits": 1}
        # Then we fill the healed guy's infos
        try:
            super_dict["overall_combat_stats"]["rcv_crit_heals"][
                infos["damage_taker"]
            ]["tot"] += infos["damages"]
            super_dict["overall_combat_stats"]["rcv_crit_heals"][
                infos["damage_taker"]
            ]["hits"] += 1
        except KeyError:
            super_dict["overall_combat_stats"]["rcv_crit_heals"][
                infos["damage_taker"]
            ] = {"tot": infos["damages"], "hits": 1}
    return super_dict


def update_misc_details_superdict_with_combat(
    target, id_ddealer, name_ddealer, dmgs_tuple, super_dict
):
    """
        Quick func that updates misc details on a target and return the dict updated
    """

    dmgs = dmgs_tuple[1]

    if not super_dict["current_combats"][target]["Misc"].get(id_ddealer):
        super_dict["current_combats"][target]["Misc"][id_ddealer] = {
            "Name": name_ddealer,
            "tot_dmgs": dmgs,
            "details": [dmgs_tuple],
        }
    else:
        super_dict["current_combats"][target]["Misc"][id_ddealer][
            "tot_dmgs"
        ] += dmgs
        super_dict["current_combats"][target]["Misc"][id_ddealer][
            "details"
        ].append(dmgs_tuple)
    return super_dict


def update_details_stats_superdict_with_combat(infos, super_dict):
    """
        Handling combat infos is convulated enough to get
        its own functions

        The aim of this one is to store detailed structured infos
        to cover the gui needs.

        Leverage this :

        struct_log = {
            "id_ddealer": int,
            "id_dtaker": int,
            "time": combat_log_matched.group("time"),
            "damages": (int)(combat_log_matched.group("damages")),
            "damage_taker": combat_log_matched.group("dude_hurt"),
            "dtaker_is_mob": False,
            "damage_dealer": combat_log_matched.group("damage_dealer"),
            "ddealer_is_mob": False,
            "crit": False,
            "heal": False,
        }

        to store it as:

        run_name : {
            Target : { # Target is the name of the player or the ID of the Monster
                Name : "target_name" (if player, it's the same as Target),
                Dealer1 : {"tot_dmgs", "details": [(dmg_tuple1), (dmg_tuple2)...]}
                Dealer2 : {"tot_dmgs", "details": [(dmg_tuple1), (dmg_tuple2)...]}
                Misc: {  # Those dmgs are done by objects or whatever weird thing
                    MiscDealer1 : {"tot_dmgs", "details": [(dmg_tuple1), (dmg_tuple2)...]}
                    MiscDealer2 : {"tot_dmgs", "details": [(dmg_tuple1), (dmg_tuple2)...]}
                }
            }
        }
    """
    target = (
        infos["damage_taker"] if not infos["id_dtaker"] else infos["id_dtaker"]
    )
    dealer = (
        infos["damage_dealer"]
        if not infos["id_ddealer"]
        else infos["id_ddealer"]
    )
    dmgs_tuple = (
        infos["time"],
        infos["damages"],
        infos["crit"],
        infos["heal"],
    )
    if not super_dict["current_combats"].get(target):
        super_dict["current_combats"][target] = {
            "Name": infos["damage_taker"],
            "Misc": {},
        }
    if not super_dict["current_combats"][target].get(dealer):
        if infos["id_ddealer"] and infos["id_dtaker"]:
            return update_misc_details_superdict_with_combat(
                target, dealer, infos["damage_dealer"], dmgs_tuple, super_dict
            )
        super_dict["current_combats"][target][dealer] = {
            "tot_dmgs": infos["damages"],
            "details": [dmgs_tuple],
        }
    else:
        if infos["id_ddealer"] and infos["id_dtaker"]:
            return update_misc_details_superdict_with_combat(
                target, dealer, infos["damage_dealer"], dmgs_tuple, super_dict
            )
        super_dict["current_combats"][target][dealer]["tot_dmgs"] += infos[
            "damages"
        ]
        super_dict["current_combats"][target][dealer]["details"].append(
            dmgs_tuple
        )

    return super_dict


def update_overall_stats_superdict_with_combat(infos, super_dict):
    """
        Handling combat infos is convulated enough to get
        its own functions

        This one stores the infos for the overall combat stats
        in the actual super dict and return it

        Must leverage this :

        struct_log = {
            "id_ddealer": int,
            "id_dtaker": int,
            "time": combat_log_matched.group("time"),
            "damages": (int)(combat_log_matched.group("damages")),
            "damage_taker": combat_log_matched.group("dude_hurt"),
            "dtaker_is_mob": False,
            "damage_dealer": combat_log_matched.group("damage_dealer"),
            "ddealer_is_mob": False,
            "crit": False,
            "heal": False,
        }

    First we handle the easiest : Overall stats
        "overall_combats_stats": {
            "dmgs": {
                "player1": { tot: 121, hits: 3 },
                "player2": { tot: 102, hits: 2 },
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

    if infos["dtaker_is_mob"] and infos["ddealer_is_mob"]:
        # We are not interested in mobs killing other mobs
        # in the Overall stats (we store this in the details part
        # under "misc" key tho. Ignoring here...
        return super_dict

    if infos["heal"]:
        return update_stats_superdict_for_heal(infos, super_dict)

    if infos["dtaker_is_mob"]:
        return update_stats_superdict_for_dmgs(infos, super_dict)

    if infos["ddealer_is_mob"]:
        return update_stats_superdict_for_rcv_dmgs(infos, super_dict)

    return super_dict


def build_stats_superdict(line, super_dict=None):
    """
        This is the core "logic" of this script

        From a parsed line (returned by 'get_parsed_line')
        Deduce actual stats from the parsed lines and
        add them to the super final dict

        The dict should be structured as :
        super_dict = {
            "current_combats": {
                Target1: {
                    "Name": id_or_name,
                    "player1": { 'tot_dmgs': 10000, 'details':
                            [(time, dmgs, critTrueOrFalse, healTrueOrFalse), ...] },
                    "player2": { 'tot_dmgs': 10000, 'details':
                            [(time, dmgs, critTrueOrFalse, healTrueOrFalse), ...] },
                    "id": { 'tot_dmgs': 10000, 'details':
                            [(time, dmgs, critTrueOrFalse, healTrueOrFalse), ...] },
                }
                Target2: {
                    "Name": id_or_name,
                    "player1": { 'tot_dmgs': 10000, 'details':
                            [(time, dmgs, critTrueOrFalse, healTrueOrFalse), ...] },
                    "player2": { 'tot_dmgs': 10000, 'details':
                            [(time, dmgs, critTrueOrFalse, healTrueOrFalse), ...] },
                    "id": { 'tot_dmgs': 10000, 'details':
                            [(time, dmgs, critTrueOrFalse, healTrueOrFalse), ...] },
                }
            }
            "Dungeon1": {
                Target1: {
                    "Name": id_or_name,
                    "player1": { 'tot_dmgs': 10000, 'details':
                            [(time, dmgs, critTrueOrFalse, healTrueOrFalse), ...] },
                    "player2": { 'tot_dmgs': 10000, 'details':
                            [(time, dmgs, critTrueOrFalse, healTrueOrFalse), ...] },
                    "id": { 'tot_dmgs': 10000, 'details':
                            [(time, dmgs, critTrueOrFalse, healTrueOrFalse), ...] },
                }
                Target2: {
                    "Name": id_or_name,
                    "player1": { 'tot_dmgs': 10000, 'details':
                            [(time, dmgs, critTrueOrFalse, healTrueOrFalse), ...] },
                    "player2": { 'tot_dmgs': 10000, 'details':
                            [(time, dmgs, critTrueOrFalse, healTrueOrFalse), ...] },
                    "id": { 'tot_dmgs': 10000, 'details':
                            [(time, dmgs, critTrueOrFalse, healTrueOrFalse), ...] },
                }
            }
            "overall_combats_stats": {
                "dmgs": {
                    "player1": {'tot':121, 'hits': 3},
                    "player2": {'tot':121, 'hits': 3},
                }
                "crit_dmgs": { same },
                "heals": { same },
                "crit_heals": { same },
                "rcv_dmgs": { same },
            },
            "dung_nbr": 1,
            "xp": 100,
            "rep": 20,
            "dram": 11110,
            "loots": ['loot1', 'loot2',...],
            "current_combat_time": timedelta(0),
            "overall_combat_time": timedelta(0),
        }
    """
    if not super_dict:
        # If the super_dict wasn't passed in param, we initialize it

        # Note that a player may start killing mobs outside of a dungeon which
        # can completed mess up the stats if the player does into a dungeon right after that
        # (we can only know that
        # a player finished a dungeon... If the player killed mobs before or between
        # dungeons, we are doomed)
        # TODO: Maybe split up this dict or use another data structure
        # to avoid an explosion ^^
        # (tried with a 200k logfile -> the dict ended up taking 36 MB X_X)
        super_dict = {
            "current_combats": dict(),
            "dung_nbr": 0,
            "xp": 0,
            "rep": 0,
            "dram": 0,
            "loots": [],
            "current_combat_time": timedelta(0),
            "overall_combat_time": timedelta(0),
            "overall_combat_stats": {
                "dmgs": dict(),
                "crit_dmgs": dict(),
                "heals": dict(),
                "crit_heals": dict(),
                "rcv_dmgs": dict(),
                "rcv_heals": dict(),
                "rcv_crit_dmgs": dict(),
                "rcv_crit_heals": dict(),
            },
        }

    line_type, line_infos = get_parsed_line(line)

    if (not line_type) or (not line_infos):
        # Found a line not supported/interesting. We skip it
        return super_dict

    if line_type == "combat":
        super_dict = update_overall_stats_superdict_with_combat(
            line_infos, super_dict
        )
        return update_details_stats_superdict_with_combat(
            line_infos, super_dict
        )

    if line_type in ("xp", "dram", "rep"):
        super_dict[line_type] = super_dict[line_type] + line_infos
        return super_dict

    if line_type == "loots":
        super_dict[line_type].append(line_infos)
        return super_dict

    if line_type == "dung":
        # The is a dungeon completion line
        # We assume that what was before that was in the dungeon
        # since we have no way to know when the dungeon start.
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
            # the player left a combat without starting it on the first place..
            # We ignore this combat to avoid weird calculations
            return super_dict
        super_dict["overall_combat_time"] = super_dict[
            "overall_combat_time"
        ] + (line_infos - super_dict["current_combat_time"])
        super_dict["current_combat_time"] = timedelta(0)
        return super_dict

    return super_dict


def parse_file(logfile, super_dict=None):
    """
        Parse en entire file in one-shot.
    """

    with open(logfile, "r") as clog:
        for line in clog:
            super_dict = build_stats_superdict(line, super_dict)

    return super_dict


def watch_and_parse_file(
    logfile, refresh=3, display_func=None, func_args=None, super_dict=None
):
    """
        Watch continuously the logfile and get only new logs when they arrive
        Optionnally, a func that can display super_dict can be passed in param
        to be part of the loop (experimental).
    """
    log_f = open(logfile, "r+")
    log_f.seek(0, 2)  # End of stream
    prev_pos = log_f.tell()
    new_pos = prev_pos
    while True:
        if new_pos > prev_pos:
            log_f.seek(prev_pos)
            new_line = "new_line"
            while new_line:
                new_line = log_f.readline()
                super_dict = build_stats_superdict(new_line, super_dict)
                if display_func:
                    display_func(func_args, super_dict)
            prev_pos = log_f.tell()
        else:
            log_f = open(logfile, "r+")
            log_f.seek(0, 2)  # End of stream
            new_pos = log_f.tell()
            # log_f.seek(new_pos)
            sleep(refresh)
