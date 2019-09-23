"""
    Parse combat logs from OrbusVR and try to display useful infos from it.

"""
#! /usr/bin/env python3

import sys
from os import access, R_OK, getenv, name as nme
from argparse import ArgumentParser

from backend.parsing_functions import watch_and_parse_file, parse_file
from frontend.console import console_display

# pylint: disable=line-too-long, bad-continuation, anomalous-backslash-in-string

USER_PATH = ""


def handle_arguments():
    """
        Simple func to export the code from main func (and make it clearer)
    """
    global USER_PATH  # pylint: disable=global-statement

    if nme == "nt":
        USER_PATH = getenv("USERPROFILE")

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
        default=USER_PATH
        + "\AppData\LocalLow\Orbus Online, LLC\OrbusVR\combat.log",
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
        "-hl",
        "--heals",
        help="Display the overall heals provided",
        action="store_true",
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
        "-lo",
        "--loots",
        help="Display all the loots acquired",
        action="store_true",
    )
    parser.add_argument(
        "--version", action="version", version="%(prog)s v0.02"
    )
    args = parser.parse_args()

    return args


def get_arguments_as_dict(args):
    """
        Simply returns the args (which are wrapped in an Argparse
        object) as a dict
    """
    return args.__dict__


def main():
    """
        Parse the args passed by the user and implements the core logic of the script
    """

    args = handle_arguments()

    if not access(args.logfile, R_OK):
        print(
            "The file {} is not readable. Please enter a valid file.\n".format(
                args.logfile
            )
        )
        return sys.exit(1)

    # Exple of usage to get the old features
    if args.follow:
        print(
            "Ok, going loopy (keeps looking the file & refreshing the stats accordingly)"
        )
        # (If you need to get a dict from the args, just pass args.__dict__)
        watch_and_parse_file(args.logfile, args.refresh, console_display, args)
    else:
        console_display(args, parse_file(args.logfile))

    return sys.exit(0)


if __name__ == "__main__":
    main()
