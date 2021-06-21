import math
import trinket


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

        self.stats_dict = {}
        # storing the dict that's passed in populating the above stats so that stats can be more easily pulled from a
        # base toon for comparison toons

        self.max_mana = 0
        self.cur_mana = 0
        self.mp5 = 0

        self.trinkets = [None, None]
        self.wand_dps = 0

        # talents. only a couple for now
        self.improved_mind_blast = 0
        self.focused_mind = 0

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
            elif key == 'spell_haste':
                self.spell_haste = value
            elif key == 'trinket 1':
                self.trinkets[0] = trinket.Trinket(value)
            elif key == 'trinket 2':
                self.trinkets[1] = trinket.Trinket(value)
            elif key == 'wand dps':
                self.wand_dps = value
            else:
                print("Invalid value {0} passed to assign_dict_stats!".format(key))
        self.stats_dict = stats_dict
        self.max_mana = 2620 + 20 + (15 * (self.intellect - 20))
        self.calc_mp5()

    def assign_talents(self, talent_dict):
        for key, value in talent_dict.items():
            if key == 'imp mb' or key == 'imb' or key == 'improved mind blast':
                self.improved_mind_blast = value
            elif key == 'fm' or key == 'focused mind':
                self.focused_mind = value

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

    def get_proc_trinkets(self):
        answer = [False, []]
        for x in self.trinkets:
            if x is not None:
                if x.on_use is False:
                    answer[0] = True
                    answer[1].append(x)
        return answer

    def modify_stat(self, string, amt):
        if string == 'spp':
            self.spell_power += amt
        elif string == 'sph':
            self.spell_haste += amt
        elif string == 'spc':
            self.spell_crit += amt
        elif string == 'spi':
            self.spirit += amt
        elif string == 'int':
            self.intellect += amt
        else:
            print('Invalid string {} passed to player.modify_stat.'.format(string))
