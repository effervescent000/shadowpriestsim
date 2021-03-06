import random
import combat_log
import utils


class Sim:
    def __init__(self, toon, total_iterations, duration, logging=False, mode=None, debug=False):
        self.dps = 0
        self.dps_list = []
        self.cur_iterations = 0
        self.time = 0
        self.toon = toon
        self.debug = debug
        self.log_this = False
        if logging is True:
            self.log = combat_log.CombatLog(mode=mode)

        self.swp = None
        self.vt = None
        self.mf = None
        self.mb = None
        self.swd = None
        self.inf = None

        self.run_iterations(total_iterations, duration, logging)
        self.dps = sum(self.dps_list) / len(self.dps_list)

    def run_iterations(self, total_iterations, duration, logging):
        base_duration = duration * 1000
        time_inc = 50
        # I'm fudging mp5 right now
        mana_regen = self.toon.mp5 / 5 * (time_inc / 1000)
        proc_trinkets = self.toon.get_proc_trinkets()

        if logging is True:
            # pick a random iteration to log
            if total_iterations == 1:
                iteration_to_log = 1
            else:
                iteration_to_log = random.randint(1, total_iterations)

        while self.cur_iterations <= total_iterations:
            if logging is True:
                if iteration_to_log == self.cur_iterations:
                    self.log_this = True
                    self.log.add_other(0.0, 'Logging iteration {}.'.format(self.cur_iterations))
                elif iteration_to_log < self.cur_iterations:
                    self.log_this = False
            duration = base_duration * (random.randint(8, 12) / 10)
            self.time = 0
            self.toon.cur_mana = self.toon.max_mana
            damage = 0
            gcd = 0
            trinket_gcd = 0
            meta_gem = self.toon.meta_gem
            act = self.Action(self.toon, time_inc)
            mana_pot_cd = 0
            shadowfiend_available = True

            self.swp = self.ShadowWordPain()
            self.vt = self.VampiricTouch()
            self.mf = self.MindFlay(time_inc, self.toon)
            self.mb = self.MindBlast(self.toon)
            self.swd = self.ShadowWordDeath()
            self.inf = self.InnerFocus()

            while self.time < duration:
                self.toon.add_mana(mana_regen)
                mana = self.toon.cur_mana
                max_mana = self.toon.max_mana
                if act.current_action is None or act.duration >= act.current_action.action_time:
                    # resolve current casts
                    if act.current_action is not None and act.duration == act.current_action.action_time:
                        if act.current_action is self.mb:
                            self.mb.reset_time()
                            damage += self.calc_damage(self.mb)
                            # if self.inf.active is True:
                            #     self.inf.start_cooldown()
                            #     if self.log_this is True:
                            #         self.log.add_other(self.time, 'Inner Focus removed.')
                        elif act.current_action is self.vt:
                            self.vt = self.apply_dot(self.vt, time_inc, self.inf)

                        # remove mystical skyfire diamond effect after a completed cast

                        if meta_gem.name == 'MSD' and meta_gem.active is True:
                            # meta_gem.active = False
                            self.end_special_effect(meta_gem)

                    if gcd <= 0:
                        # use trinkets if possible
                        if self.toon.trinkets is not None:
                            if trinket_gcd <= 0:
                                for x in self.toon.trinkets:
                                    if x.cooldown <= 0:
                                        self.start_special_effect(x)
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
                            gcd = self.get_gcd(time_inc)

                        # spell logic goes here
                        elif self.swp.duration < 0 and mana > self.swp.mana_cost:
                            if self.inf.cooldown <= 0:
                                self.inf.use()
                                if self.log_this is True:
                                    self.log.add_other(self.time, 'Inner Focus activated.')
                            self.swp = self.apply_dot(self.swp, time_inc, self.inf)
                            if self.inf.active is True:
                                self.inf.start_cooldown()
                                if self.log_this is True:
                                    self.log.add_other(self.time, 'Inner Focus removed.')
                            self.check_procs(proc_trinkets, meta_gem)
                            act = self.Action(self.toon, time_inc, self.swp)
                            self.clip_mind_flay()
                            gcd = self.get_gcd(time_inc)
                        elif self.vt.duration < 1500 and mana > self.vt.mana_cost:
                            self.check_procs(proc_trinkets, meta_gem)
                            act = self.Action(self.toon, time_inc, self.vt)
                            self.clip_mind_flay()
                            if self.log_this is True:
                                self.log.add_other(self.time, 'Vampiric Touch begins casting.')
                            gcd = self.get_gcd(time_inc)
                        elif self.mb.cooldown <= 0 and mana > self.mb.mana_cost:
                            self.check_procs(proc_trinkets, meta_gem)
                            # if self.inf.cooldown <= 0:
                            #     self.inf.use()
                            #     if self.log_this is True:
                            #         self.log.add_other(self.time, 'Inner Focus activated.')
                            act = self.Action(self.toon, time_inc, self.mb)
                            self.clip_mind_flay()
                            if self.log_this is True:
                                self.log.add_other(self.time, 'Mind Blast begins casting.')
                            gcd = self.get_gcd(time_inc)
                        elif self.swd.cooldown <= 0 and mana > self.swd.mana_cost:
                            self.check_procs(proc_trinkets, meta_gem)
                            self.swd.reset_time()
                            act = self.Action(self.toon, time_inc, self.swd)
                            self.clip_mind_flay()
                            damage += self.calc_damage(self.swd)
                            gcd = self.get_gcd(time_inc)
                        elif mana > self.mf.mana_cost:
                            if act.current_action != self.mf or \
                                    (act.current_action == self.mf and self.mf.duration < 0):
                                self.check_procs(proc_trinkets, meta_gem)
                                self.mf = self.apply_dot(self.mf, time_inc, self.inf)
                                act = self.Action(self.toon, time_inc, self.mf)
                                gcd = self.get_gcd(time_inc)
                                # TODO ensure that if a new MF channel starts with MSD up, the proc gets removed after
                                #  channel time/ticks are calculated
                                if meta_gem is not None and meta_gem.name == 'MSD' and meta_gem.active is True:
                                    self.end_special_effect(meta_gem)
                        # sit and wand for 10 seconds if OOM
                        # TODO get actual wand stats and sim wands
                        else:
                            wand_damage = self.toon.wand_dps * 10
                            damage += wand_damage
                            if self.log_this is True:
                                self.log.add_wand(wand_damage, self.time)
                            gcd = 10000

                damage += self.tic_dots(act)

                # end active trinkets
                if self.toon.trinkets is not None:
                    for x in self.toon.trinkets:
                        if x.active is True and x.duration <= 0:
                            self.end_special_effect(x)
                            x.active = False
                        x.increment_time(time_inc)

                self.inf.cooldown -= time_inc
                meta_gem.duration -= time_inc
                meta_gem.cooldown -= time_inc
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
            # end any trinkets/meta gems that are currently active
            if self.toon.trinkets is not None:
                for x in self.toon.trinkets:
                    if x.active is True:
                        self.end_special_effect(x)
                    x.reset_item()
            if meta_gem is not None:
                if meta_gem.active is True:
                    # meta_gem.active = False
                    self.end_special_effect(meta_gem)

            if self.log_this is True:
                self.log.finalize_log()
            self.cur_iterations += 1

    def check_procs(self, proc_trinkets, meta_gem):
        # see if trinket proc'd from this action
        if proc_trinkets[0] is True:
            for x in proc_trinkets[1]:
                if x.cooldown <= 0:
                    if random.random() < x.proc_chance:
                        x.trigger_effect()
                        self.start_special_effect(x)

        # see if meta gem proc'd from this action
        if meta_gem is not None and meta_gem.proc_chance > 0:
            if meta_gem.cooldown <= 0 and meta_gem.active is False:
                if random.random() < meta_gem.proc_chance:
                    self.start_special_effect(meta_gem)

    def start_special_effect(self, effect):
        effect.trigger_effect()
        if self.log_this is True:
            self.log.add_other(self.time, 'Special effect {0} triggered.'.format(effect.name))
        self.toon.modify_stat(effect.stat[1], effect.stat[0])

    def end_special_effect(self, effect):
        effect.active = False
        self.toon.modify_stat(effect.stat[1], effect.stat[0] * -1)
        if self.log_this is True:
            self.log.add_other(self.time, 'Special effect {0} removed.'.format(effect.name))

    def is_channeling_mind_flay(self, act):
        if act.current_action is self.mf and act.current_action.duration < act.current_action.max_duration:
            return True
        else:
            return False

    def get_gcd(self, time_inc):
        # TODO for now adding in a cludge to mimic latency/reaction time (setting GCD to .1 second higher).
        #  Find a better way to do this.
        gcd = utils.haste_spell(1600, time_inc, self.toon.spell_haste)
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

    def tic_dots(self, act):
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
        if self.mf.duration >= 0 and self.mf.duration in self.mf.ticks:
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

    def calc_damage(self, spell, inner_focus=None):
        damage = 0
        if (inner_focus is not None and inner_focus.active is False) or inner_focus is None:
            self.toon.cur_mana -= spell.mana_cost

        if self.try_hit(spell) is True:
            damage = self.deal_damage(spell)
            # extra crit is from shadow power talent
            crit_mod = .15
            if inner_focus is not None and inner_focus.active is True:
                crit_mod += .25
            if random.random() > 1 - self.toon.spell_crit - crit_mod:
                damage *= self.toon.crit_multiplier
            if self.log_this is True:
                self.log.add_damage(spell, damage, self.time)
        if self.vt.duration >= 0:
            self.toon.add_mana(damage * .05)
        return damage

    def apply_dot(self, dot, time_inc, inner_focus=None):
        if self.try_hit(dot) is True:
            dot.reset_time(self.toon, time_inc, self.debug, self.cur_iterations)
            if self.log_this is True:
                self.log.add_dot_application(dot, self.time)
        if (inner_focus is not None and inner_focus.active is False) or inner_focus is None:
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
            self.ticks = []
            if self.current_action is not None:
                self.current_action.set_action_time(toon, time_inc)
                # if self.current_action.name == 'Mind Flay':
                #     self.ticks = self.current_action.get_ticks(time_inc, toon)

    class InnerFocus:
        def __init__(self):
            self.max_cooldown = 180000
            self.cooldown = -100
            self.active = False

        def use(self):
            self.active = True

        def start_cooldown(self):
            self.active = False
            self.cooldown = self.max_cooldown

    class Spell:
        def __init__(self, time_inc, toon):
            self.name = 'unset string'
            self.action_time = 0
            self.base_dmg = 0

        def set_action_time(self, toon, time_inc):
            if self.action_time > 0:
                self.action_time = utils.haste_spell(self.action_time, time_inc, toon.spell_haste)

        def get_damage(self):
            return self.base_dmg * 1.1

    class DoT(Spell):
        def __init__(self, time_inc=None, toon=None):
            super().__init__(time_inc, toon)
            self.name = 'unset string'
            self.action_time = 0
            self.duration = -100
            self.max_duration = 0
            self.mana_cost = 0
            self.base_dmg = 0
            self.coefficient = 0
            # TODO add spell power snapshotting

        def reset_time(self, toon=None, time=None, debug=False, iteration=-1):
            self.duration = self.max_duration

    class DirectSpell(Spell):
        def __init__(self, time_inc=None, toon=None):
            super().__init__(time_inc, toon)
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
            super().__init__(time_inc=None, toon=None)
            self.name = 'Shadow Word: Pain'
            self.action_time = 0
            self.duration = -100
            self.max_duration = 24000
            self.mana_cost = 575
            self.base_dmg = 206  # per tick
            self.coefficient = .183

    class VampiricTouch(DoT):

        def __init__(self, time_inc=None, toon=None):
            super().__init__(time_inc, toon)
            self.name = 'Vampiric Touch'
            self.action_time = 1500
            self.duration = -100
            self.max_duration = 15000
            self.mana_cost = 425
            self.base_dmg = 130  # per tick
            self.coefficient = .2

    class MindFlay(DoT):

        def __init__(self, time_inc=None, toon=None, iteration=-1):
            super().__init__()
            self.name = 'Mind Flay'
            self.action_time = 0
            self.duration = -100
            self.base_duration = 3000
            self.max_duration = 3000
            self.mana_cost = 196
            self.base_dmg = 176
            self.coefficient = .19
            self.ticks_base = [0, 1000, 2000]
            self.ticks = self.get_ticks(time_inc, toon, iteration)

        def get_ticks(self, time_inc, toon=None, iteration=-1):
            # so MF by default lasts 3 seconds, and there's a tick at 0, 1, and 2 seconds. Just trying to wrap my head
            # around this
            ticks = [0, utils.round_to_base(self.max_duration * (1 / 3), time_inc),
                     utils.round_to_base(self.max_duration * (2 / 3), time_inc)]
            if toon is not None:
                tick_diff = ticks[2] - ticks[1]
                if tick_diff < 1000 and toon.meta_gem.active is False:
                    print('Iteration {}: Time between MF ticks is {} with {}% haste.'.format(iteration, tick_diff,
                                                                                             toon.spell_haste * 100))
            return ticks

        def reset_time(self, toon=None, time_inc=100, debug=False, iteration=-1):
            self.max_duration = utils.haste_spell(self.base_duration, time_inc, toon.spell_haste)
            self.duration = self.max_duration
            if debug is True:
                self.ticks = self.get_ticks(time_inc, toon, iteration)
            else:
                self.ticks = self.get_ticks(time_inc)

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
