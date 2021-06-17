import math


class Player:

    def __init__(self, character_class, name='base'):
        self.character_class = character_class
        self.name = name
        self.spell_power = 0
        self.spell_hit = 0
        self.spell_haste = 0
        self.spell_crit = 0
        self.intellect = 0
        self.spirit = 0
        self.max_mana = 0
        self.cur_mana = 0
        self.mp5 = 0

    def assign_dict_stats(self, stats_dict):
        for key, value in stats_dict.items():
            if key == 'spell_power':
                self.spell_power = value
            elif key == 'spell_hit':
                self.spell_hit = value
            elif key == 'spell_crit':
                self.spell_crit = value
            elif key == 'intellect':
                self.intellect = value
            elif key == 'spirit':
                self.spirit = value
            elif key == 'mana':
                self.max_mana = value
            elif key == 'spell_haste':
                self.spell_haste = value
            else:
                print("Invalid value passed to assign_dict_stats!")
        self.calc_mp5()

    def calc_mp5(self):
        # calculate casting mp5
        # self.mp5 = self.mp5 + self.intellect * .15
        # self.mp5 = self.mp5 + self.spirit * .3
        self.mp5 = (.001 + (self.spirit * math.sqrt(self.intellect) * .009327)) * 5 * .3
        # for now also assume blessing of wisdom
        self.mp5 = self.mp5 + 41

    def add_mana(self, amt):
        if self.cur_mana + amt > self.max_mana:
            self.cur_mana = self.max_mana
        else:
            self.cur_mana = self.cur_mana + amt
