"""
    Simple module to display result as nicely as possible in the console.
    (yeah, will be rough :p )
"""
#! /usr/bin/env python3


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
