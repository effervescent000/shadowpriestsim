class Trinket:
    def __init__(self, name):
        self.name = name.lower()
        self.stat = [0, None]  # valid options are spp, spc, sph (haste), spi, int
        self.max_cooldown = 0
        self.cooldown = 0
        self.max_duration = 0
        self.duration = 0
        self.on_use = True
        self.proc_chance = 0
        self.active = False

        self.get_trinket()

    def get_trinket(self):
        if self.name == 'vengeance of the illidari':
            self.stat = [120, 'spp']
            self.max_cooldown = 90000
            self.max_duration = 15000
        elif self.name == 'glowing crystal insignia':
            self.stat = [104, 'spp']
            self.max_cooldown = 120000
            self.max_duration = 20000
        elif self.name == "quagmirran's eye":
            self.stat = [320, 'sph']
            self.max_cooldown = 45000
            self.max_duration = 6000
            self.on_use = False
            self.proc_chance = .1
        elif self.name == 'icon of the silver crescent':
            self.stat = [155, 'spp']
            self.max_cooldown = 120000
            self.max_duration = 20000
        elif self.name == 'living ruby serpent' or self.name == 'figurine - living ruby serpent':
            self.stat = [150, 'spp']
            self.max_cooldown = 5 * 60 * 1000
            self.max_duration = 20000

    def use_trinket(self):
        self.cooldown = self.max_cooldown
        self.duration = self.max_duration
        self.active = True

    def increment_time(self, time_inc):
        self.cooldown = self.cooldown - time_inc
        self.duration = self.duration - time_inc

    def reset_trinket(self):
        self.active = False
        self.cooldown = 0
        self.duration = 0
