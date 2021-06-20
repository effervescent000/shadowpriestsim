import random
import combat_log
import utils
import trinket


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
        proc_trinkets = self.toon.get_proc_trinkets()

        if logging is True:
            # pick a random iteration to log
            iteration_to_log = random.randint(1, total_iterations - 1)

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
            trinket_gcd = 0
            act = self.Action(self.toon, time_inc)
            mana_pot_cd = 0
            shadowfiend_available = True

            self.swp = self.ShadowWordPain()
            self.vt = self.VampiricTouch()
            self.mf = self.MindFlay()
            self.mb = self.MindBlast(self.toon)
            self.swd = self.ShadowWordDeath()

            while self.time < duration:
                # TODO implement inner focus
                self.toon.add_mana(mana_regen)
                mana = self.toon.cur_mana
                max_mana = self.toon.max_mana
                if act.current_action is None or act.duration >= act.current_action.action_time:
                    # resolve current casts
                    if act.current_action is not None and act.duration == act.current_action.action_time:
                        if act.current_action is self.mb:
                            self.mb.reset_time()
                            damage += self.calc_damage(self.mb)
                        elif act.current_action is self.vt:
                            self.vt = self.apply_dot(self.vt)
                    if gcd <= 0:
                        # use trinkets if possible
                        if self.toon.trinkets is not None:
                            if trinket_gcd <= 0:
                                for x in self.toon.trinkets:
                                    if x.cooldown <= 0:
                                        self.start_trinket_effect(x)
                                        trinket_gcd = 30000
                                        break

						# TODO figure out how to only clip Mind Flay if it's shortly after a tick
                        # check for mana pot
                        if mana + 3000 < max_mana and mana_pot_cd <= 0:
                            mana_pot_cd = 120000
                            mana_amt = random.randint(1800, 3000)
                            self.toon.add_mana(mana_amt)
                            # this should clip mind flay but it's off the gcd so I'm a little uncertain how to handle it
                            if self.log_this is True:
                                self.log.add_mana_regen(mana_amt, self.time)
                        # now check for shadowfiend
                        if mana < max_mana * .3 and mana_pot_cd > 20000 \
                                and shadowfiend_available:
                            # numbers based on
                            # https://web.archive.org/web/20100209225350/http://shadowpriest.com/viewtopic.php?f=13&t=7616
                            # TODO actually sim lil guys' attacks n stuff
                            shadowfiend_mana = (2977 + self.toon.spell_power * 1.5) * .8 * 1 - .16 + self.toon.spell_hit
                            # the .8 modifier is assuming that the target has some shadow resist
                            self.toon.add_mana(shadowfiend_mana)
                            shadowfiend_available = False
                            act.current_action = None
                            if self.log_this is True:
                                self.log.add_mana_regen(shadowfiend_mana, self.time)
                            self.clip_mind_flay()
                            gcd = self.get_gcd()

                        # spell logic goes here
                        elif self.swp.duration < 0 and mana > self.swp.mana_cost:
                            self.swp = self.apply_dot(self.swp)
                            act = self.Action(self.toon, time_inc, self.swp)
                            self.clip_mind_flay()
                            gcd = self.get_gcd()
                        elif self.vt.duration < 1500 and mana > self.vt.mana_cost:
                            act = self.Action(self.toon, time_inc, self.vt)
                            self.clip_mind_flay()
                            if self.log_this is True:
                                self.log.add_other(self.time, 'Vampiric Touch begins casting.')
                            gcd = self.get_gcd()
                        elif self.mb.cooldown <= 0 and mana > self.mb.mana_cost:
                            act = self.Action(self.toon, time_inc, self.mb)
                            self.clip_mind_flay()
                            if self.log_this is True:
                                self.log.add_other(self.time, 'Mind Blast begins casting.')
                            gcd = self.get_gcd()
                        elif self.swd.cooldown <= 0 and mana > self.swd.mana_cost:
                            self.swd.reset_time()
                            act = self.Action(self.toon, time_inc, self.swd)
                            self.clip_mind_flay()
                            damage += self.calc_damage(self.swd)
                            gcd = self.get_gcd()
                        elif mana > self.mf.mana_cost:
                            if act.current_action is not self.mf:
                                self.mf = self.apply_dot(self.mf)
                                act = self.Action(self.toon, time_inc, self.mf)
                                gcd = self.get_gcd()
                        # sit and wand for 10 seconds if OOM
                        # TODO get actual wand stats and sim wands
                        else:
                            wand_damage = self.toon.wand_dps * 10
                            damage += wand_damage
                            if self.log_this is True:
                                self.log.add_wand(wand_damage, self.time)
                            gcd = 10000

                damage += self.tic_dots()

                # end active trinkets
                if self.toon.trinkets is not None:
                    for x in self.toon.trinkets:
                        if x.active is True and x.duration <= 0:
                            self.end_trinket_effect(x)
                            x.active = False
                        x.increment_time(time_inc)

                # see if trinket proc'd from this action
                if gcd == self.get_gcd():
                    if proc_trinkets[0] is True:
                        for x in proc_trinkets[1]:
                            if x.cooldown <= 0:
                                if random.random() < x.proc_chance:
                                    x.use_trinket()
                                    self.start_trinket_effect(x)

                mana_pot_cd -= time_inc
                self.swp.duration -= time_inc
                self.vt.duration -= time_inc
                self.mf.duration -= time_inc
                self.mb.cooldown -= time_inc
                self.swd.cooldown -= time_inc
                gcd -= time_inc
                trinket_gcd -= time_inc
                act.duration += time_inc
                self.time += time_inc

			# end of iteration stuff here
            self.dps_list.append(damage / (duration / 1000))
            # end any trinkets that are currently active
            if self.toon.trinkets is not None:
                for x in self.toon.trinkets:
                    if x.active is True:
                        self.end_trinket_effect(x)
                    x.reset_trinket()

            if self.log_this is True:
                self.log.finalize_log()
            self.cur_iterations += 1

    def start_trinket_effect(self, t):
        t.use_trinket()
        if self.log_this is True:
            self.log.add_other(self.time, 'Trinket {0} used.'.format(t.name))
        self.toon.modify_stat(t.stat[1], t.stat[0])

    def end_trinket_effect(self, t):
        self.toon.modify_stat(t.stat[1], t.stat[0] * -1)
        if self.log_this is True:
            self.log.add_other(self.time, 'Trinket {0} effect removed.'.format(t.name))

    def is_channeling_mind_flay(self, act):
        if act.current_action is self.mf and act.current_action.duration < act.current_action.max_duration:
            return True
        else:
            return False

    def get_gcd(self, time_inc=10):
        # TODO for now adding in a cludge to mimic latency/reaction time (setting GCD to .1 second higher).
        #  Find a better way to do this.
        gcd = utils.round_to_base(1600 / (1 + self.toon.spell_haste), time_inc)
        # gcd can't be lowered below .75 seconds
        if gcd < 750:
            gcd = 750
        return gcd

    def clip_mind_flay(self):
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
            damage += new_damage
        if self.vt.duration >= 0 and self.vt.duration % 3000 == 0 and self.vt.duration != 15000:
            new_damage = self.deal_damage(self.vt)
            if self.log_this is True:
                self.log.add_damage(self.vt, new_damage, self.time)
            damage += new_damage
        if self.mf.duration >= 0 and self.mf.duration in act.ticks:
            new_damage = self.deal_damage(self.mf)
            if self.log_this is True:
                self.log.add_damage(self.mf, new_damage, self.time)
            damage += new_damage
        if self.vt.duration >= 0:
            self.toon.add_mana(damage * .05)
        return damage

    def deal_damage(self, spell):
        # extra modifiers are shadow weaving, misery, and shadowform
        return round((spell.get_damage() + self.toon.spell_power * spell.coefficient) * 1.10 * 1.05 * 1.15)

    def calc_damage(self, spell):
        damage = 0
        self.toon.cur_mana -= spell.mana_cost

        if self.try_hit(spell) is True:
            damage = self.deal_damage(spell)
            # extra crit is from shadow power talent
            if random.random() > 1 - self.toon.spell_crit - .15:
                damage = damage * 1.5
            if self.log_this is True:
                self.log.add_damage(spell, damage, self.time)
        if self.vt.duration >= 0:
            self.toon.add_mana(damage * .05)
        return damage

    def apply_dot(self, dot):
        if self.try_hit(dot) is True:
            dot.reset_time()
            if self.log_this is True:
                self.log.add_dot_application(dot, self.time)
        self.toon.cur_mana -= dot.mana_cost
        return dot

    def try_hit(self, spell=None):
        if random.random() > 1 - .16 + self.toon.spell_hit:
            if self.log_this is True:
                self.log.add_miss(spell, self.time)
            return False
        else:
            return True

    class Action:
        def __init__(self, toon, time_inc, act=None):
            self.current_action = act
            self.duration = 0
            if self.current_action is not None:
                self.current_action.set_action_time(toon, time_inc)
                # I'm not sure this will work but I'm on my ipad rn so I can't check easily
                if isinstance(self.current_action, MindFlay):
                	self.ticks = mf.get_ticks(time_inc, toon)

    class Spell:
        def __init__(self):
            self.name = 'unset string'
            self.action_time = 0
            self.base_dmg = 0

        def set_action_time(self, toon, time_inc):
            if self.action_time > 0:
                self.action_time = utils.round_to_base(self.action_time / (1 - toon.spell_haste), time_inc)

        def get_damage(self):
            return self.base_dmg * 1.1

    class DoT(Spell):
        def __init__(self):
            super().__init__()
            self.name = 'unset string'
            self.action_time = 0
            self.duration = -100
            self.max_duration = 0
            self.mana_cost = 0
            self.base_dmg = 0
            self.coefficient = 0
            # TODO add spell power snapshotting

        def reset_time(self):
            self.duration = self.max_duration

    class DirectSpell(Spell):
        def __init__(self):
            super().__init__()
            self.name = 'unset string'
            self.action_time = 0
            self.cooldown = 0
            self.max_cooldown = 0
            self.mana_cost = 0
            self.base_dmg = [0, 0]
            # base_dmg is for spells with damage ranges, the first number should be the lower end, the second is the
            # higher end
            self.coefficient = 0

        def reset_time(self):
            self.cooldown = self.max_cooldown

        def get_damage(self):
            # TODO research if this is just a flat average or if it's more complex than that
            return random.randint(self.base_dmg[0], self.base_dmg[1]) * 1.1

    class ShadowWordPain(DoT):

        def __init__(self):
            super().__init__()
            self.name = 'Shadow Word: Pain'
            self.action_time = 0
            self.duration = -100
            self.max_duration = 24000
            self.mana_cost = 575
            self.base_dmg = 206  # per tick
            self.coefficient = .183

    class VampiricTouch(DoT):

        def __init__(self):
            super().__init__()
            self.name = 'Vampiric Touch'
            self.action_time = 1500
            self.duration = -100
            self.max_duration = 15000
            self.mana_cost = 425
            self.base_dmg = 130  # per tick
            self.coefficient = .2

    class MindFlay(DoT):

        def __init__(self):
            super().__init__()
            self.name = 'Mind Flay'
            self.action_time = 0
            self.duration = -100
            self.base_duration = 3000
            self.max_duration = 3000
            self.mana_cost = 196
            self.base_dmg = 176
            self.coefficient = .19
            
        def get_ticks(self, time_inc, toon):
			# so MF by default lasts 3 seconds, and there's a tick at 0, 1, and 2 seconds. Just trying to wrap my head around this
			ticks = [0, 1000, 2000]
				for x in ticks:
					x = utils.round_to_base(x / (1 + toon.spell_haste), time_inc)
			return ticks	
			
		def reset_time(toon, time_inc):
			self.max_duration = utils.round_to_base(self.base_duration / (1 + toon.spell_haste), time_inc)
					
    class MindBlast(DirectSpell):
        def __init__(self, toon):
            super().__init__()
            self.name = 'Mind Blast'
            self.action_time = 1500
            self.cooldown = -100
            self.max_cooldown = 8000
            self.mana_cost = 382
            self.base_dmg = [711, 752]
            self.coefficient = .429
            
            self.get_cd(toon)
           

        def get_cd(self, toon):
            self.max_cooldown -= 500 * toon.improved_mind_blast

    class ShadowWordDeath(DirectSpell):
        def __init__(self):
            super().__init__()
            self.name = 'Shadow Word: Death'
            self.action_time = 0
            self.cooldown = -100
            self.max_cooldown = 12000
            self.mana_cost = 309
            self.base_dmg = [572, 664]
            self.coefficient = .429
