import special_effect


class Trinket(special_effect.SpecialEffect):
    def __init__(self, name):
        super().__init__(name)

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
            self.max_cooldown = 300000
            self.max_duration = 20000


