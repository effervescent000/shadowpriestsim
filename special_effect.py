import utils


class SpecialEffect:
    def __init__(self, name):
        self.name = name.lower()
        self.max_cooldown = 0
        self.cooldown = -100
        self.active = False
        self.duration = 0
        self.max_duration = 0
        self.proc_chance = 0
        self.stat = [0, None]  # valid options are spp, spc, sph (haste), spi, int
        self.on_use = True

    def trigger_effect(self):
        self.cooldown = self.max_cooldown
        self.duration = self.max_duration
        self.active = True

    def increment_time(self, time_inc):
        self.cooldown = self.cooldown - time_inc
        self.duration = self.duration - time_inc

    def reset_item(self):
        self.active = False
        self.cooldown = 0
        self.duration = 0
