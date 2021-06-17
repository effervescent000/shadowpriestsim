import random
import combat_log


class Sim:
    def __init__(self, toon, total_iterations, duration, logging=False, mode=None):
        self.dps = 0
        self.dps_list = []
        self.cur_iterations = 0
        self.time = 0
        self.toon = toon
        self.log_this = False
        if logging is True:
            self.log = combat_log.CombatLog(mode=mode)

        self.swp = None
        self.vt = None
        self.mf = None
        self.mb = None
        self.swd = None

        self.run_iterations(total_iterations, duration, logging)
        self.dps = sum(self.dps_list) / len(self.dps_list)

    def run_iterations(self, total_iterations, duration, logging):
        base_duration = duration * 1000
        time_inc = 100
        # I'm fudging mp5 right now
        mana_regen = self.toon.mp5 / 5 * (time_inc / 1000)
        if logging is True:
            iteration_to_log = random.randint(1, total_iterations - 1)
            # pick a random iteration to log

        while self.cur_iterations < total_iterations:
            if logging is True:
                if iteration_to_log == self.cur_iterations:
                    self.log_this = True
                elif iteration_to_log < self.cur_iterations:
                    self.log_this = False
            duration = base_duration * (random.randint(8, 12) / 10)
            self.time = 0
            self.toon.cur_mana = self.toon.max_mana
            damage = 0
            gcd = 0
            act = self.Action()
            mana_pot_cd = 0
            shadowfiend_available = True

            self.swp = self.ShadowWordPain()
            self.vt = self.VampiricTouch()
            self.mf = self.MindFlay()
            self.mb = self.MindBlast()
            self.swd = self.ShadowWordDeath()

            while self.time < duration:
                self.toon.add_mana(mana_regen)
                if act.current_action is None or act.duration >= act.current_action.action_time:
                    # resolve current casts
                    if act.current_action is not None and act.duration == act.current_action.action_time:
                        if act.current_action is self.mb:
                            self.mb.reset_time()
                            damage = damage + self.calc_damage(self.mb)
                        elif act.current_action is self.vt:
                            self.vt = self.apply_dot(self.vt)
                    if gcd <= 0:

                        # check for mana pot
                        if self.toon.cur_mana + 3000 < self.toon.max_mana and mana_pot_cd <= 0:
                            mana_pot_cd = 120000
                            mana_amt = random.randint(1800, 3000)
                            self.toon.add_mana(mana_amt)
                            # this should clip mind flay but it's off the gcd so I'm a little uncertain how to handle it
                            if self.log_this is True:
                                self.log.add_mana_regen(mana_amt, self.time)
                        # now check for shadowfiend
                        if self.toon.cur_mana / self.toon.max_mana < .3 and mana_pot_cd > 2000 \
                                and shadowfiend_available:
                            # TODO figure out mechanics of actual shadowfiend. For now I'm just giving mana
                            shadowfiend_mana = 3000
                            self.toon.add_mana(shadowfiend_mana)
                            shadowfiend_available = False
                            act.current_action = None
                            if self.log_this is True:
                                self.log.add_mana_regen(shadowfiend_mana, self.time)
                            self.clip_mind_flay()
                            gcd = self.get_gcd()

                        elif self.swp.duration < 0 and self.toon.cur_mana > self.swp.mana_cost:
                            self.swp = self.apply_dot(self.swp)
                            act = self.Action(self.swp)
                            self.clip_mind_flay()
                            gcd = self.get_gcd()
                        elif self.vt.duration < 1500 and self.toon.cur_mana > self.vt.mana_cost:
                            act = self.Action(self.vt)
                            self.clip_mind_flay()
                            if self.log_this is True:
                                self.log.add_other(self.time, "Vampiric Touch begins casting.")
                            gcd = self.get_gcd()
                        elif self.mb.cooldown <= 0 and self.toon.cur_mana > self.mb.mana_cost:
                            # TODO add proper casting integration. For now I'm just adding a cludge where the CD
                            #  needs to be at -1.5 to cast
                            act = self.Action(self.mb)
                            self.clip_mind_flay()
                            if self.log_this is True:
                                self.log.add_other(self.time, "Mind Blast begins casting.")
                            gcd = self.get_gcd()
                        elif self.swd.cooldown <= 0 and self.toon.cur_mana > self.swd.mana_cost:
                            self.swd.reset_time()
                            act = self.Action(self.swd)
                            self.clip_mind_flay()
                            damage = damage + self.calc_damage(self.swd)
                            gcd = self.get_gcd()
                        elif self.toon.cur_mana > self.mf.mana_cost and act.current_action is not self.mf:
                            self.mf = self.apply_dot(self.mf)
                            act = self.Action(self.mf)
                            gcd = self.get_gcd()

                damage = damage + self.tic_dots()

                mana_pot_cd = mana_pot_cd - time_inc
                self.swp.duration = self.swp.duration - time_inc
                self.vt.duration = self.vt.duration - time_inc
                self.mf.duration = self.mf.duration - time_inc
                self.mb.cooldown = self.mb.cooldown - time_inc
                self.swd.cooldown = self.swd.cooldown - time_inc
                gcd = gcd - time_inc
                act.duration = act.duration + time_inc
                self.time = self.time + time_inc

            self.dps_list.append(damage / (duration / 1000))
            if self.log_this is True:
                self.log.finalize_log()
            self.cur_iterations = self.cur_iterations + 1

    def get_gcd(self):
        gcd = round(1500 / (1 + self.toon.spell_haste))
        if gcd < 750:
            gcd = 750
        return gcd

    def clip_mind_flay(self, act=None):
        if self.mf.duration > 0:
            self.mf.duration = -1
            # setting this to -.25 to prevent it accidentally ticking on 0 (which would normally be the last tick)
            if self.log_this is True:
                self.log.clip_mind_flay(self.time)

    def tic_dots(self):
        damage = 0
        if self.swp.duration >= 0 and self.swp.duration % 3000 == 0 and self.swp.duration != 24000:
            new_damage = self.deal_damage(self.swp)
            if self.log_this is True:
                self.log.add_damage(self.swp, new_damage, self.time)
            damage = damage + new_damage
        if self.vt.duration >= 0 and self.vt.duration % 3000 == 0 and self.vt.duration != 15000:
            new_damage = self.deal_damage(self.vt)
            if self.log_this is True:
                self.log.add_damage(self.vt, new_damage, self.time)
            damage = damage + new_damage
        if self.mf.duration >= 0 and self.mf.duration % 1500 == 0:
            # this isn't entirely accurate (it will cause MF to tick on application, but for now it will do)
            new_damage = self.deal_damage(self.mf)
            if self.log_this is True:
                self.log.add_damage(self.mf, new_damage, self.time)
            damage = damage + new_damage
        self.toon.add_mana(damage * .05)
        return damage

    def deal_damage(self, spell):
        # extra modifiers are shadow weaving and misery, and shadowform
        return round(spell.base_dmg + self.toon.spell_power * spell.coefficient * 1.10 * 1.05 * 1.15)

    def calc_damage(self, spell):
        damage = 0
        self.toon.cur_mana = self.toon.cur_mana - spell.mana_cost

        if self.try_hit(spell) is True:
            damage = self.deal_damage(spell)
            # extra crit is from shadow power talent
            if random.random() > 1 - self.toon.spell_crit - .15:
                damage = damage * 1.5
            if self.log_this is True:
                self.log.add_damage(spell, damage, self.time)
        self.toon.add_mana(damage * .05)
        return damage

    def apply_dot(self, dot):
        if self.try_hit(dot) is True:
            dot.reset_time()
            if self.log_this is True:
                self.log.add_dot_application(dot, self.time)
        self.toon.cur_mana = self.toon.cur_mana - dot.mana_cost
        return dot

    def try_hit(self, spell=None):
        if random.random() > 1 - .16 + self.toon.spell_hit:
            if self.log_this is True:
                self.log.add_miss(spell, self.time)
            return False
        else:
            return True

    class Action:
        def __init__(self, act=None):
            self.current_action = act
            self.duration = 0

    class DoT:
        def __init__(self):
            self.name = 'unset string'
            self.action_time = 0
            self.duration = -100
            self.max_duration = 0
            self.mana_cost = 0
            self.base_dmg = 0
            self.coefficient = 0

        def reset_time(self):
            self.duration = self.max_duration

    class DirectSpell:
        def __init__(self):
            self.name = 'unset string'
            self.action_time = 0
            self.cooldown = 0
            self.max_cooldown = 0
            self.mana_cost = 0
            self.base_dmg = 0
            self.coefficient = 0

        def reset_time(self):
            self.cooldown = self.max_cooldown

    class ShadowWordPain(DoT):

        def __init__(self):
            super().__init__()
            self.name = "Shadow Word: Pain"
            self.action_time = 0
            self.duration = -100
            self.max_duration = 24000
            self.mana_cost = 575
            self.base_dmg = 206 * 1.1
            self.coefficient = .183

    class VampiricTouch(DoT):

        def __init__(self):
            super().__init__()
            self.name = 'Vampiric Touch'
            self.action_time = 1500
            self.duration = -100
            self.max_duration = 15000
            self.mana_cost = 425
            self.base_dmg = 130 * 1.1
            self.coefficient = .2

    class MindFlay(DoT):

        def __init__(self):
            super().__init__()
            self.name = 'Mind Flay'
            self.action_time = 0
            self.duration = -100
            self.max_duration = 3000
            self.mana_cost = 196
            self.base_dmg = 176 * 1.1
            self.coefficient = .19

    class MindBlast(DirectSpell):
        def __init__(self):
            super().__init__()
            self.name = 'Mind Blast'
            self.action_time = 1500
            self.cooldown = -100
            self.max_cooldown = 6000
            self.mana_cost = 382
            self.base_dmg = 731 * 1.1
            self.coefficient = .429

    class ShadowWordDeath(DirectSpell):
        def __init__(self):
            super().__init__()
            self.name = 'Shadow Word: Death'
            self.action_time = 0
            self.cooldown = -100
            self.max_cooldown = 12000
            self.mana_cost = 309
            self.base_dmg = 618 * 1.1
            self.coefficient = .429