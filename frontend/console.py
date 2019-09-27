"""
    Simple module to display result as nicely as possible in the console.
    (yeah, will be rough :p )
"""
#! /usr/bin/env python3

# pylint: disable=bad-continuation, fixme

from os import system, name as nme


def sort_and_dict_display(combat_dict, phrase, suffix_per_line):
    """
        Simple func that display a combat dict and the phrase passed in param
    """
    sorted_dict = sorted(
        combat_dict.items(), key=lambda kv: kv[1]["tot"], reverse=True
    )
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
        sort_and_dict_display(
            stats_dict["dmgs"], phrase, "hits (or ticks from DoT))"
        )

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
        sort_and_dict_display(
            stats_dict["heals"], phrase, "heals (or ticks from HoT))"
        )

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
        super_dict["overall_combat_time"] = str(
            super_dict["overall_combat_time"]
        )
        print(
            "And btw, you were in combat for {} hour(s)".format(
                super_dict["overall_combat_time"]
            )
        )


def sort_detailed_dpsers(target_details_dict):
    """
        Sort dpsers before displaying.

        The specifity here is that the keys are not
        consistent and must be checked (so it's a bit too
        much convulated for a lambda)

        As a first quick & dirty way, we can transform
        the dict to a list of actual dpsers (without
        misc things)

        Then we sort
    """
    # Infos that are not used for now
    not_used = ("Name", "Boss", "Misc")

    dpsers_list = []

    for dpser, hits in target_details_dict.items():
        if dpser in not_used:
            continue
        # if dpser == "Name":
        #     continue
        # if dpser == "Boss":
        #     continue
        # if dpser == "Misc":
        #     continue
        # for misc_dpser, misc_hits in hits.items():
        #     print(
        #         "misc_thingy: {}, {}".format(
        #             misc_hits["Name"], misc_hits["tot_dmgs"]
        #         )
        #     )
        dpsers_list.append((dpser, hits["tot_dmgs"]))

    sorted_dpsers = sorted(dpsers_list, key=lambda kv: kv[1], reverse=True)

    return sorted_dpsers


def detailed_stats_console_display(args, super_dict):
    """
        Function that displays the detailed combat
        stats to the console
        The detailed struct looks like this :
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

        On a first version and to avoid pushing too much infos to the console,
        we'll only display dmgs from players on bosses
    """

    # TODO : Use args to know what to display
    # For now, it's only sorted dmgs on bosses
    system("cls" if nme == "nt" else "clear")

    for dung, details_dung in super_dict.items():
        if not details_dung:
            continue
        if dung != "current_combats" and "Dungeon" not in dung:
            continue
        try:
            if details_dung["dung_name"]:
                dung_name = details_dung["dung_name"]
        except KeyError:
            continue
        print()
        print("#" * 30)
        print("DETAILS FOR BOSSES IN {}".format(dung_name.upper()))
        print("#" * 30)
        for target, details_target in details_dung.items():
            if target == "dung_name":
                continue
            if details_target["Boss"]:
                name = (
                    target
                    if not details_target["Name"]
                    else details_target["Name"]
                )
                print("\n{}".format(name.upper()))
                print("-" * 20)
                sorted_dict = sort_detailed_dpsers(details_target)

                for dpser, hits in sorted_dict:
                    print(dpser, hits)
    return args


def console_display(args, super_dict):
    """
        Takes all the args as dict and all the stats parsed
        and display them in the console.

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

    if args.boss:
        detailed_stats_console_display(args, super_dict)
    else:
        all_stats = True
        options = (
            args.dmgs,
            args.dmgs_crits,
            args.dmgs_received,
            args.heals,
            args.heals_crits,
            args.heals_received,
            args.misc_infos,
            args.loots,
        )
        if any(options):
            all_stats = False

        display_overall_stats(args, super_dict, all_stats)

    if not args.follow:
        input("\n\nPress ENTER key to quit...")
