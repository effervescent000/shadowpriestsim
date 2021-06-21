def round_to_base(num, base):
    return base * round(num / base)


def convert_spell_haste(amt):
    return amt / 15.8 / 100


def convert_spell_crit(amt):
    return amt / 22.1 / 100


def convert_spell_hit(amt):
    return amt / 12.6 / 100
