"""
    Parse combat logs from OrbusVR and try to display useful infos from it.
"""
#! /usr/bin/env python3

import sys
from os import access, R_OK, system, getenv, name as nme
from time import sleep
from datetime import timedelta
import re
from argparse import ArgumentParser
from pprint import pprint

# pylint: disable=line-too-long, bad-continuation, anomalous-backslash-in-string

COMBAT_PATTERN = re.compile(
    "(?P<time>\d{2}:\d{2}:\d{2}:\d{3}) \[Combat] (?P<dude_hurt>[\S\s]+) took (?P<damages>\S+) damage from (?P<damage_dealer>[\S ]+)\s+"
)
XP_PATTERN = re.compile(
    "(?P<time>\d{2}:\d{2}:\d{2}:\d{3}) \[Loot] Gained (?P<pts>\S+) XP?"
)
DRAM_PATTERN = re.compile(
    "(?P<time>\d{2}:\d{2}:\d{2}:\d{3}) \[Loot] Gained (?P<pts>\S+) Dram?"
)
REP_PATTERN = re.compile(
    "(?P<time>\d{2}:\d{2}:\d{2}:\d{3}) \[Loot] Earned (?P<pts>\S+) Reputation?"
)
LOOT_PATTERN = re.compile(
    "(?P<time>\d{2}:\d{2}:\d{2}:\d{3}) \[Loot] Item Acquired: (?P<loot>.*)"
)
ENTER_COMBAT_PATTERN = re.compile(
    "(?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2}):(?P<milsec>\d{3}) \[Combat] You are now in combat."
)
EXIT_COMBAT_PATTERN = re.compile(
    "(?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2}):(?P<milsec>\d{3}) \[Combat] You are no longer in combat."
)
ENTER_COMBAT_PATTERN_TIME = re.compile(
    "(?P<time>\d{2}:\d{2}:\d{2}:\d{3}) \[Combat] You are now in combat."
)
EXIT_COMBAT_PATTERN_TIME = re.compile(
    "(?P<time>\d{2}:\d{2}:\d{2}:\d{3}) \[Combat] You are no longer in combat."
)


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


def build_stats_superdict(line_type, line_infos, super_dict):
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
                        "player1": 10,
                        "player2": 13,
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


def parse_file(logfile, super_dict):
    """
        Parse en entire file in one-shot.
    """

    with open(logfile, "r") as clog:
        for line in clog:
            log_type, infos = get_parsed_line(line)
            super_dict = build_stats_superdict(log_type, infos, super_dict)

    # Should we convert the timedelta back to a string here ?
    # (or let the display func (gui/console) do it so it can leverage the
    # timedelta for whatever needed)

    return super_dict


def watch_file(logfile):
    """
        Watch continuously the logfile and get only new logs when they arrive
    """
    log_f = open(logfile, "r+")
    log_f.seek(0, 2)  # End of stream
    while True:
        position = log_f.tell()
        new_line = log_f.readline()
        # Once all lines are read this just returns ''
        # until the file changes and a new line appears
        if new_line:
            print(get_parsed_line(new_line))
        else:
            print("waiting...")
            log_f.seek(position)
            sleep(3)


def overalls(logfile):
    """
        Legacy function which parse & process the whole log file
    """
    fighters = dict()
    fighters_criticals = dict()
    damages_taken = dict()
    heals_given = dict()
    heals_given_crits = dict()
    heals_received = dict()
    tot_xp = 0
    tot_dram = 0
    tot_rep = 0
    tot_dungeons = 0
    loots = []
    tot_combat_time = timedelta()
    entered_time = timedelta()
    exited_time = timedelta()
    entered_combat = False
    with open(logfile, "r") as clog:
        for line in clog:
            critical = False
            combat_log_matched = re.match(COMBAT_PATTERN, line)
            if combat_log_matched:
                get_struct_combat_line(combat_log_matched)
                damages = (int)(combat_log_matched.group("damages"))
                dude_hurt = combat_log_matched.group("dude_hurt")
                damage_dealer = combat_log_matched.group("damage_dealer")
                if "(Critical)" in damage_dealer:
                    critical = True
                    damage_dealer = "".join(damage_dealer.split()[:-1])
                if "(" in damage_dealer or "Unknown" in damage_dealer:
                    # The damage_dealer is a mob or a weird spell

                    if "(" in dude_hurt:
                        # Bugged log line (players are not allowed to have
                        # parenthesis in their name)
                        continue

                    # We update the damages_taken by players
                    if damages_taken.get(dude_hurt):
                        total_dmgs = (int)(damages_taken[dude_hurt][0]) + damages
                        nbr_hits = damages_taken[dude_hurt][1] + 1
                        damages_taken[dude_hurt] = (total_dmgs, nbr_hits)
                    else:
                        damages_taken[dude_hurt] = (damages, 1)
                    continue

                if damages > 0:
                    if fighters.get(damage_dealer):
                        total_dmgs = (int)(fighters[damage_dealer][0]) + damages
                        nbr_hits = fighters[damage_dealer][1] + 1
                        fighters[damage_dealer] = (total_dmgs, nbr_hits)
                    else:
                        fighters[damage_dealer] = (damages, 1)
                    if critical:
                        if fighters_criticals.get(damage_dealer):
                            total_crits = (int)(
                                fighters_criticals[damage_dealer][0]
                            ) + damages
                            nbr_crits = fighters_criticals[damage_dealer][1] + 1
                            fighters_criticals[damage_dealer] = (total_crits, nbr_crits)
                        else:
                            fighters_criticals[damage_dealer] = (damages, 1)
                elif damages < 0:
                    damages = -damages
                    if heals_given.get(damage_dealer):
                        tot_heals = (int)(heals_given[damage_dealer][0]) + damages
                        nbr_heals = heals_given[damage_dealer][1] + 1
                        heals_given[damage_dealer] = (tot_heals, nbr_heals)
                    else:
                        heals_given[damage_dealer] = (damages, 1)

                    if heals_received.get(dude_hurt):
                        tot_heals = (int)(heals_received[dude_hurt][0]) + damages
                        nbr_heals = heals_received[dude_hurt][1] + 1
                        heals_received[dude_hurt] = (tot_heals, nbr_heals)
                    else:
                        heals_received[dude_hurt] = (damages, 1)

                    if critical:
                        if heals_given_crits.get(damage_dealer):
                            tot_heals_crit = (int)(
                                heals_given_crits[damage_dealer][0]
                            ) + damages
                            nbr_crit_heals = heals_given_crits[damage_dealer][1] + 1
                            heals_given_crits[damage_dealer] = (
                                tot_heals_crit,
                                nbr_crit_heals,
                            )
                        else:
                            heals_given_crits[damage_dealer] = (damages, 1)
                continue
            xp_log_matched = re.match(XP_PATTERN, line)
            if xp_log_matched:
                tot_xp = tot_xp + (int)(xp_log_matched["pts"])
                continue
            dram_log_matched = re.match(DRAM_PATTERN, line)
            if dram_log_matched:
                tot_dram = tot_dram + (int)(dram_log_matched["pts"])
                continue
            rep_log_matched = re.match(REP_PATTERN, line)
            if rep_log_matched:
                tot_rep = tot_rep + (int)(rep_log_matched["pts"])
                continue
            loot_log_matched = re.match(LOOT_PATTERN, line)
            if loot_log_matched:
                loots.append(loot_log_matched["loot"])
                continue
            entered_log_matched = re.match(ENTER_COMBAT_PATTERN, line)
            if entered_log_matched:
                entered_combat = True
                hour = (int)(entered_log_matched["hour"])
                minu = (int)(entered_log_matched["min"])
                sec = (int)(entered_log_matched["sec"])
                milsec = (int)(entered_log_matched["milsec"])
                entered_time = timedelta(
                    hours=hour, minutes=minu, seconds=sec, milliseconds=milsec
                )
            exited_log_matched = re.match(EXIT_COMBAT_PATTERN, line)
            if exited_log_matched:
                hour = (int)(exited_log_matched["hour"])
                minu = (int)(exited_log_matched["min"])
                sec = (int)(exited_log_matched["sec"])
                milsec = (int)(exited_log_matched["milsec"])
                exited_time = timedelta(
                    hours=hour, minutes=minu, seconds=sec, milliseconds=milsec
                )
                if not entered_combat:
                    print("Hmm something wrong here. Incomplete log file ? ")
                    print(
                        "I'm seeing that you left a combat you never started on time {}".format(
                            exited_time
                        )
                    )
                    print("Not counting it to avoid weird datas.")
                    continue
                tot_combat_time = tot_combat_time + (exited_time - entered_time)
            if "Dungeon Completed" in line:
                tot_dungeons = tot_dungeons + 1
                continue

    sorted_fighters = sorted(fighters.items(), key=lambda kv: kv[1][0], reverse=True)
    sorted_fighters_crits = sorted(
        fighters_criticals.items(), key=lambda kv: kv[1][0], reverse=True
    )
    sorted_takers = sorted(damages_taken.items(), key=lambda kv: kv[1][0], reverse=True)
    sorted_healers = sorted(heals_given.items(), key=lambda kv: kv[1][0], reverse=True)
    sorted_healers_crits = sorted(
        heals_given_crits.items(), key=lambda kv: kv[1][0], reverse=True
    )
    sorted_healed = sorted(
        heals_received.items(), key=lambda kv: kv[1][0], reverse=True
    )

    stats_dict = {
        "dmgs": sorted_fighters,
        "crit_dmgs": sorted_fighters_crits,
        "rcv_dmgs": sorted_takers,
        "heals": sorted_healers,
        "crit_heals": sorted_healers_crits,
        "rcv_heals": sorted_healed,
        "tot_dung": tot_dungeons,
        "combat_t": tot_combat_time,
        "dram": tot_dram,
        "rep": tot_rep,
        "xp": tot_xp,
        "loots": loots,
    }

    return stats_dict


def console_display(args, stats_dict):
    """
        Takes all the args and all the stats parsed
        and display them in the console.
    """
    if nme == "nt":
        system("mode con: lines=800")
    all_stats = True
    if (
        args.dmgs
        or args.dmgs_crits
        or args.dmgs_received
        or args.heals
        or args.heals_crits
        or args.heals_received
        or args.misc_infos
        or args.loots
    ):
        all_stats = False

    if args.dmgs or all_stats:
        print("\nOverall damages (crits included) dealt (ordered from most to least):")
        for guy, dmgs in stats_dict["dmgs"]:
            print(
                "    {0:15} {1:10} ({2:6} hits (or ticks from DoT))".format(
                    guy, dmgs[0], dmgs[1]
                )
            )

    if args.dmgs_crits or all_stats:
        print("\nOverall critical dmgs dealt (ordered from most to least):")
        for guy, dmgs in stats_dict["crit_dmgs"]:
            print(
                "    {0:15} {1:10} ({2:6} crit hits (or ticks from DoT))".format(
                    guy, dmgs[0], dmgs[1]
                )
            )

    if args.dmgs_received or all_stats:
        print("\nOverall damages Received (ordered from most to least):")
        for guy, dmgs in stats_dict["rcv_dmgs"]:
            print(
                "    {0:15} {1:10} ({2:6} hits (or ticks from DoT))".format(
                    guy, dmgs[0], dmgs[1]
                )
            )

    if args.heals_received or all_stats:
        print("\nOverall heals received (ordered from most to least):")
        for guy, dmgs in stats_dict["rcv_heals"]:
            print(
                "    {0:15} {1:10} ({2:6} heals (or ticks from HoT))".format(
                    guy, dmgs[0], dmgs[1]
                )
            )

    if args.heals or all_stats:
        print("\nOverall heals (crits included) given (ordered from most to least):")
        for guy, dmgs in stats_dict["heals"]:
            print(
                "    {0:15} {1:10} ({2:6} heals (or ticks from HoT))".format(
                    guy, dmgs[0], dmgs[1]
                )
            )

    if args.heals_crits or all_stats:
        print("\nOverall critical heals given (ordered from most to least):")
        for guy, dmgs in stats_dict["crit_heals"]:
            print(
                "    {0:15} {1:10} ({2:6} crit heals (or ticks from HoT))".format(
                    guy, dmgs[0], dmgs[1]
                )
            )

    if args.loots:
        if stats_dict["loots"]:
            print("\n\nWow, what a lucky person you are, you've acquired : ")
            for loot in stats_dict["loots"]:
                print("    - {}".format(loot))
        else:
            print("Oh, no loots during this session :-(")

    if args.misc_infos:
        print(
            "\n\nYou won {} XP, {} Dram and {} Reputation on this session! :-)".format(
                stats_dict["xp"], stats_dict["dram"], stats_dict["rep"]
            )
        )
        if stats_dict["tot_dung"] > 0:
            print(
                "You even completed {} dungeons ! Amazing !".format(
                    stats_dict["tot_dung"]
                )
            )
        print(
            "And btw, you were in combat for {} hour(s)".format(stats_dict["combat_t"])
        )


def main():
    """
        Parse the args passed by the user and implements the core logic of the script
    """

    if nme == "nt":
        user_path = getenv("USERPROFILE")
    else:
        user_path = ""

    parser = ArgumentParser(
        prog="overlog.exe",
        description="Parse combat logs from OrbusVR and, by default, displays all the stats \
                (overall dmgs,dmgs_received, heals and criticals). You can filter the stats \
                with options.",
    )
    parser.add_argument(
        "-l",
        "--logfile",
        type=str,
        help="The log file to parse",
        default=user_path + "\AppData\LocalLow\Orbus Online, LLC\OrbusVR\combat.log",
    )
    parser.add_argument(
        "-f", "--follow", help="Keep watching the file", action="store_true"
    )
    parser.add_argument(
        "-r",
        "--refresh",
        help="When watching the file, set the refresh time (by default, it refreshes every 30 sec)",
        type=int,
        default=30,
    )
    parser.add_argument(
        "-d", "--dmgs", help="Display the overall dmgs", action="store_true"
    )
    parser.add_argument(
        "-dc",
        "--dmgs_crits",
        help="Display the overall critical dmgs",
        action="store_true",
    )
    parser.add_argument(
        "-dr",
        "--dmgs_received",
        help="Display the overall dmgs received",
        action="store_true",
    )
    parser.add_argument(
        "-hr",
        "--heals_received",
        help="Display the overall heals received",
        action="store_true",
    )
    parser.add_argument(
        "-hl", "--heals", help="Display the overall heals provided", action="store_true"
    )
    parser.add_argument(
        "-hlc",
        "--heals_crits",
        help="Display the overall critical heals provided",
        action="store_true",
    )
    parser.add_argument(
        "-m",
        "--misc_infos",
        help="Display some other infos we can find in the log file (like xp/gold/rep, \
                nbr of dungeons, time in combat, maybe more?)",
        action="store_true",
    )
    parser.add_argument(
        "-lo", "--loots", help="Display all the loots acquired", action="store_true"
    )
    parser.add_argument("--version", action="version", version="%(prog)s v0.02")
    args = parser.parse_args()

    if not access(args.logfile, R_OK):
        print(
            "The file {} is not readable. Please enter a valid file.\n".format(
                args.logfile
            )
        )
        return sys.exit(1)

    # can't use 'dungeon1' since we may start killing mobs outside of a dungeon which
    # can completed mess up the stats (we can only know that
    # a player finished a dungeon... If the player killed mobs before or between
    # dungeons, we are doomed)
    # TODO: Maybe split up this dict or use another data structure
    # to avoid an explosion ^^
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

    super_dict = parse_file(args.logfile, super_dict)

    # TODO: just for dev, need to be cleaned up or entirely removed :
    super_dict["overall_combat_time"] = str(super_dict["overall_combat_time"])
    del super_dict["current_combat_time"]
    pprint(super_dict)

    # watch_file(args.logfile)

    # if args.follow:
    #    print(
    #        "Ok, going loopy (keeps looking the file & refreshing the stats accordingly)"
    #    )
    #    while True:
    #        system("cls" if nme == "nt" else "clear")
    #        stats_dict = overalls(args.logfile)
    #        console_display(args, stats_dict)
    #        sleep(args.refresh)
    # else:
    #    stats_dict = overalls(args.logfile)
    #    console_display(args, stats_dict)

    if nme == "nt":
        system("pause")

    return sys.exit(0)


if __name__ == "__main__":
    main()
