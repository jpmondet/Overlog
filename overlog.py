"""
    Parse combat logs from OrbusVR and try to display useful infos from it.

"""
#! /usr/bin/env python3

import sys
from os import access, R_OK, system, getenv, name as nme
from time import sleep
from argparse import ArgumentParser
from datetime import timedelta
from pprint import pprint

from parsing_functions import build_stats_superdict

# pylint: disable=line-too-long, bad-continuation, anomalous-backslash-in-string


def parse_file(logfile, super_dict):
    """
        Parse en entire file in one-shot.
    """

    with open(logfile, "r") as clog:
        for line in clog:
            super_dict = build_stats_superdict(line, super_dict)

    # Should we convert the timedelta back to a string here ?
    # (or let the display func (gui/console) do it so it can leverage the
    # timedelta for whatever needed)

    return super_dict


def watch_file(logfile, super_dict):
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
            super_dict = build_stats_superdict(line, super_dict)
        else:
            print("waiting...")
            log_f.seek(position)
            sleep(3)


def console_display(args, stats_dict):
    """
        Takes all the args and all the stats parsed
        and display them in the console.
    """
    # sorted_fighters = sorted(fighters.items(), key=lambda kv: kv[1][0], reverse=True)
    """
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

    # watch_file(args.logfile, super_dict)

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
