"""
    Test functions from the parsing_functions.py file
"""
#! /usr/bin/env python3

import pytest
import re
from backend.parsing_functions import get_struct_combat_line, get_parsed_line
from backend.overlog_consts import COMBAT_PATTERN

COMBAT_LOG_LINE = "19:06:35:470 [Combat]  Scav Knight(21) took 3952 damage from Nerozarg\n"
LOG_STRUCTURED = {
    "id_ddealer": 0,
    "id_dtaker": 21,
    "time": "19:06:35:470",
    "damages": 3952,
    "damage_taker": " Scav Knight",
    "dtaker_is_mob": True,
    "damage_dealer": "Nerozarg",
    "ddealer_is_mob": False,
    "crit": False,
    "heal": False,
}

def test_get_struct_combat_line():
    """
        Checks if a COMBAT log line is correctly
        parsed and structured.
    """
    combat_log_matched = re.match(COMBAT_PATTERN, COMBAT_LOG_LINE)
    line_structured = get_struct_combat_line(combat_log_matched)

    assert line_structured == LOG_STRUCTURED


