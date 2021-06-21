def round_to_base(num, base):
    """Round num to a multiplier of base."""
    return base * round(num / base)


def convert_spell_haste(amt):
    return amt / 15.8 / 100


def convert_spell_crit(amt):
    return amt / 22.1 / 100


def convert_spell_hit(amt):
    return amt / 12.6 / 100


def haste_spell(time, time_inc, haste):
    """Apply haste % to a casted spell (or the GCD)"""
    return round_to_base(time / (1 + haste), time_inc)
