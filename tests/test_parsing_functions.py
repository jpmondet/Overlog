"""
    Test functions from the parsing_functions.py file
"""
#! /usr/bin/env python3

import pytest
import re
from backend.parsing_functions import get_struct_combat_line, get_parsed_line
from backend.overlog_consts import COMBAT_PATTERN

COMBAT_LOG_LINE = "19:06:35:470 [Combat]  Scav Knight(21) took 39520 damage from Melghor\n"
XP_LOG_LINE = "20:09:36:997 [Loot] Gained 430 XP\n"
DRAM_LOG_LINE = "18:17:15:112 [Loot] Gained 36 Dram\n"
REP_LOG_LINE = "19:29:03:166 [Loot] Earned 200 Reputation\n"
LOOTS_LOG_LINE = "19:29:59:286 [Loot] Item Acquired: Aged Enhanced Intellect Potion\n"
ENTER_CMBT_LOG_LINE = "19:37:19:947 [Combat] You are now in combat.\n"
EXIT_CMBT_LOG_LINE = "19:33:58:081 [Combat] You are no longer in combat.\n"
DUNG_LOG_LINE = "20:09:38:988 [System] Dungeon Completed You have completed the dungeon! Congratulations!\n"

LOG_STRUCTURED = {
    "id_ddealer": 0,
    "id_dtaker": 21,
    "time": "19:06:35:470",
    "damages": 39520,
    "damage_taker": " Scav Knight",
    "dtaker_is_mob": True,
    "damage_dealer": "Melghor",
    "ddealer_is_mob": False,
    "crit": False,
    "heal": False,
}

def test_get_parsed_line_combat():
    """
        Checks if get_parsed_line func
        matches on combat log
    """
    line_type, _ = get_parsed_line(COMBAT_LOG_LINE)

    assert line_type == "combat"

def test_get_parsed_line_xp():
    """
        Checks if get_parsed_line func
        matches on xp log
    """
    line_type, _ = get_parsed_line(XP_LOG_LINE)

    assert line_type == "xp"

def test_get_parsed_line_dram():
    """
        Checks if get_parsed_line func
        matches on dram log
    """
    line_type, _ = get_parsed_line(DRAM_LOG_LINE)

    assert line_type == "dram"

def test_get_parsed_line_rep():
    """
        Checks if get_parsed_line func
        matches on rep log
    """
    line_type, _ = get_parsed_line(REP_LOG_LINE)

    assert line_type == "rep"

def test_get_parsed_line_loots():
    """
        Checks if get_parsed_line func
        matches on rep log
    """
    line_type, _ = get_parsed_line(LOOTS_LOG_LINE)

    assert line_type == "loots"

def test_get_parsed_line_enter_cmbt():
    """
        Checks if get_parsed_line func
        matches on entered combat log
    """
    line_type, _ = get_parsed_line(ENTER_CMBT_LOG_LINE)

    assert line_type == "entered_combat"

def test_get_parsed_line_exit_cmbt():
    """
        Checks if get_parsed_line func
        matches on exited combat log
    """
    line_type, _ = get_parsed_line(EXIT_CMBT_LOG_LINE)

    assert line_type == "exited_combat"

def test_get_parsed_line_dung():
    """
        Checks if get_parsed_line func
        matches on Dungeon Completed log
    """
    line_type, _ = get_parsed_line(DUNG_LOG_LINE)

    assert line_type == "dung"

def test_get_parsed_line_combat_fail():
    """
        Checks if get_parsed_line func
        matches on combat log
    """
    line_type, _ = get_parsed_line(XP_LOG_LINE)

    assert line_type != "combat"

def test_get_parsed_line_xp_fail():
    """
        Checks if get_parsed_line func
        matches on xp log
    """
    line_type, _ = get_parsed_line(COMBAT_LOG_LINE)

    assert line_type != "xp"

def test_get_parsed_line_dram_fail():
    """
        Checks if get_parsed_line func
        matches on dram log
    """
    line_type, _ = get_parsed_line(XP_LOG_LINE)

    assert line_type != "dram"

def test_get_parsed_line_rep_fail():
    """
        Checks if get_parsed_line func
        matches on rep log
    """
    line_type, _ = get_parsed_line(COMBAT_LOG_LINE)

    assert line_type != "rep"

def test_get_parsed_line_loots_fail():
    """
        Checks if get_parsed_line func
        matches on rep log
    """
    line_type, _ = get_parsed_line(XP_LOG_LINE)

    assert line_type != "loots"

def test_get_parsed_line_enter_cmbt_fail():
    """
        Checks if get_parsed_line func
        matches on entered combat log
    """
    line_type, _ = get_parsed_line(EXIT_CMBT_LOG_LINE)

    assert line_type != "entered_combat"

def test_get_parsed_line_exit_cmbt_fail():
    """
        Checks if get_parsed_line func
        matches on exited combat log
    """
    line_type, _ = get_parsed_line(ENTER_CMBT_LOG_LINE)

    assert line_type != "exited_combat"

def test_get_parsed_line_dung_fail():
    """
        Checks if get_parsed_line func
        matches on Dungeon Completed log
    """
    line_type, _ = get_parsed_line(COMBAT_LOG_LINE)

    assert line_type != "dung"

def test_get_struct_combat_line():
    """
        Checks if a COMBAT log line is correctly
        parsed and structured.
    """
    combat_log_matched = re.match(COMBAT_PATTERN, COMBAT_LOG_LINE)
    line_structured = get_struct_combat_line(combat_log_matched)

    assert line_structured == LOG_STRUCTURED

