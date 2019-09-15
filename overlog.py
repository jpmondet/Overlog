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

from backend.parsing_functions import build_stats_superdict

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
    prev_pos = log_f.tell()
    new_pos = prev_pos
    while True:
        if new_pos > prev_pos:
            log_f.seek(prev_pos)
            new_line = "new_line"
            while new_line:
                new_line = log_f.readline()
                super_dict = build_stats_superdict(new_line, super_dict)
                # TODO: del this test print
                pprint(super_dict)
            prev_pos = log_f.tell()
        else:
            print("waiting...")
            log_f = open(logfile, "r+")
            log_f.seek(0, 2)  # End of stream
            new_pos = log_f.tell()
            # log_f.seek(new_pos)
            sleep(3)


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
    # (tried with a 200k logfile -> the dict end up taking 36 MB X_X)
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
    # watch_file(args.logfile, super_dict)

    # TODO: just for dev, need to be cleaned up or entirely removed :
    super_dict["overall_combat_time"] = str(super_dict["overall_combat_time"])
    del super_dict["current_combat_time"]
    pprint(super_dict)

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
