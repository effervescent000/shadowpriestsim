import utils
import special_effect


class MetaGem(special_effect.SpecialEffect):
    def __init__(self, name):
        super().__init__(name)

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

