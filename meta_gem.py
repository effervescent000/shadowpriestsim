import utils


class MetaGem:
    def __init__(self, name):
        self.name = name.lower()
        self.max_cooldown = 0
        self.cooldown = -100
        self.active = False
        self.duration = 0
        self.max_duration = 0
        self.proc_chance = 0
        self.stat = [0, None]  # valid options are spp, spc, sph (haste), spi, int

        self.get_meta_gem()

    def get_meta_gem(self):
        if 'mystical' in self.name:
            self.name = 'MSD'
            self.max_cooldown = 45000
            self.max_duration = 10000
            self.proc_chance = .15
            self.stat = [utils.convert_spell_haste(320), 'sph']
        if 'chaotic' in self.name:
            self.name = 'CSD'

    def start_effect(self):
        self.cooldown = self.max_cooldown
        self.duration = self.max_duration
        self.active = True
