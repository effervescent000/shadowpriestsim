import copy

import sim

stats = ['spell_power', 'spell_hit', 'spell_crit', 'spell_haste', 'intellect', 'spirit']


class StatWeights:
    def __init__(self, toon, iterations, duration):
        self.baseline = 0
        self.stat_values = {}
        self.toon = toon
        self.iterations = iterations
        self.duration = duration

        self.run_sims()
        self.output_weights()

    def run_sims(self):
        base_sim = sim.Sim(self.toon, self.iterations, self.duration)
        self.baseline = base_sim.dps
        print('Baseline simmed: {} dps'.format(self.baseline))
        for x in stats:
            self.stat_values[x] = self.sim_stat(x) - self.baseline
            print('Done simming {0}: {1} dps'.format(x, self.stat_values[x]))
        self.stat_values = self.normalize_values()

    def normalize_values(self):
        norm_values = self.stat_values.copy()
        for x in norm_values:
            norm_values[x] = round(norm_values[x] / self.stat_values['spell_power'], 2)
        return norm_values

    def sim_stat(self, stat):
        toon = copy.deepcopy(self.toon)
        if stat == 'spell_power':
            toon.spell_power += 10
            return self.sim_this(toon)
        elif stat == 'spell_hit':
            toon.spell_hit += (10 / 12.6) / 100
            return self.sim_this(toon)
        elif stat == 'spell_crit':
            toon.spell_crit += ((10 / 22.1) / 100)
            return self.sim_this(toon)
        elif stat == 'spell_haste':
            toon.spell_haste += ((10 / 15.8) / 100)
            return self.sim_this(toon)
        elif stat == 'intellect':
            toon.intellect += 10
            return self.sim_this(toon)
        elif stat == 'spirit':
            toon.spirit += 10
            return self.sim_this(toon)
        else:
            print('Invalid value {0} passed to sim_stat!'.format(stat))

    def sim_this(self, toon):
        return sim.Sim(toon, self.iterations, self.duration).dps

    def output_weights(self):
        print('( Pawn: v1: "shadow": Intellect={0}, SpellHasteRating={1}, SpellCritRating={2}, ShadowSpellDamage={3}, '
              'SpellDamage={3}, SpellHitRating={4}, Spirit={5}, Mp5=0.5)'.format(
            self.stat_values['intellect'],
            self.stat_values['spell_haste'],
            self.stat_values['spell_crit'],
            self.stat_values['spell_power'],
            self.stat_values['spell_hit'],
            self.stat_values['spirit']))
