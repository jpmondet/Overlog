"""
    Simple module to display result as nicely as possible in the console.
    (yeah, will be rough :p )
"""
#! /usr/bin/env python3

# pylint: disable=bad-continuation

from os import system, name as nme


def sort_and_dict_display(combat_dict, phrase, suffix_per_line):
    """
        Simple func that display a combat dict and the phrase passed in param
    """
    sorted_dict = sorted(combat_dict.items(), key=lambda kv: kv[1]["tot"], reverse=True)
    print()
    print(phrase)
    for guy, dmgs in sorted_dict:
        print(
            "    {0:15} {1:10} ({2:6} {3}".format(
                guy, dmgs["tot"], dmgs["hits"], suffix_per_line
            )
        )


def display_overall_stats(args, super_dict, all_stats):
    """
        Func that aim to display only overall stats
        (basically display what overlog used to display
        in it's 0.02 release)
    """
    system("cls" if nme == "nt" else "clear")

    stats_dict = super_dict["overall_combat_stats"]

    if args.dmgs or all_stats:
        phrase = "Overall damages (crits included) dealt (ordered from most to least):"
        sort_and_dict_display(stats_dict["dmgs"], phrase, "hits (or ticks from DoT))")

    if args.dmgs_crits or all_stats:
        phrase = "Overall critical damages dealt (ordered from most to least):"
        sort_and_dict_display(
            stats_dict["crit_dmgs"], phrase, "hits (or ticks from DoT))"
        )

    if args.dmgs_received or all_stats:
        phrase = "Overall damages Received (ordered from most to least):"
        sort_and_dict_display(
            stats_dict["rcv_dmgs"], phrase, "hits (or ticks from DoT))"
        )

    if args.heals_received or all_stats:
        phrase = "Overall heals received (ordered from most to least):"
        sort_and_dict_display(
            stats_dict["rcv_heals"], phrase, "heals (or ticks from HoT))"
        )

    if args.heals or all_stats:
        phrase = "Overall heals (crits included) given (ordered from most to least):"
        sort_and_dict_display(stats_dict["heals"], phrase, "heals (or ticks from HoT))")

    if args.heals_crits or all_stats:
        phrase = "Overall critical heals given (ordered from most to least):"
        sort_and_dict_display(
            stats_dict["crit_heals"], phrase, "heals (or ticks from HoT))"
        )

    if args.loots:
        if super_dict["loots"]:
            print("\n\nWow, what a lucky person you are, you've acquired : ")
            for loot in super_dict["loots"]:
                print("    - {}".format(loot))
        else:
            print("Oh, no loots during this session :-(")

    if args.misc_infos or all_stats:
        print(
            "\n\nYou won {} XP, {} Dram and {} Reputation on this session! :-)".format(
                super_dict["xp"], super_dict["dram"], super_dict["rep"]
            )
        )
        if super_dict["dung_nbr"] > 0:
            print(
                "You even completed {} dungeons ! Amazing !".format(
                    super_dict["dung_nbr"]
                )
            )
        super_dict["overall_combat_time"] = str(super_dict["overall_combat_time"])
        print(
            "And btw, you were in combat for {} hour(s)".format(
                super_dict["overall_combat_time"]
            )
        )


def detailed_stats_display(args, super_dict):
    """
        Function that displays the detailed combat
        stats to the console
    """
    # TODO: Find a way to display this part of the
    # dict on the console without being overwhelm.
    return args, super_dict


def console_display(args, super_dict):
    """
        Takes all the args as dict and all the stats parsed
        and display them in the console.
    """
    """
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

    display_overall_stats(args, super_dict, all_stats)
