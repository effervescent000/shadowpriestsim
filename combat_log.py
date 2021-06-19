def format_time(time):
    return time / 1000


class CombatLog:
    def __init__(self, fn=None, mode=None):
        if fn is None:
            fn = 'output.txt'
        self.fn = fn
        self.log = open(fn, 'w')
        if mode is None or mode == 'verbose' or mode == 'v':
            self.mode = 'verbose'
        elif mode == 'stats' or mode == 's':
            self.mode = 'stats'
        else:
            print('Invalid mode passed!')

    def add_other(self, time, txt):
        if self.mode == 'verbose':
            self.log.write('{0}: {1}\n'.format(format_time(time), txt))

    def add_damage(self, spell, amt, time):
        if self.mode == 'verbose':
            self.log.write('{0}: {1} deals {2} damage.\n'.format(format_time(time), spell.name, amt))
        elif self.mode == 'stats':
            self.log.write('{}\t{}\t{}\n'.format(format_time(time), spell.name, amt))

    def add_wand(self, amt, time):
        if self.mode == 'verbose':
            self.log.write('{0}: Wand deals {1} damage.\n'.format(format_time(time), amt))
        elif self.mode == 'stats':
            self.log.write('Wand\t{}\t{}'.format(format_time(time), amt))

    def add_miss(self, spell, time):
        if self.mode == 'verbose':
            self.log.write('{0}: {1} missed.\n'.format(format_time(time), spell.name))
        elif self.mode == 'stats':
            pass

    def add_dot_application(self, spell, time):
        if self.mode == 'verbose':
            self.log.write('{0}: {1} is applied.\n'.format(format_time(time), spell.name))
        elif self.mode == 'stats':
            pass

    def add_mana_regen(self, amt, time):
        if self.mode == 'verbose':
            self.log.write('{0}: {1} mana gained.\n'.format(format_time(time), amt))
        elif self.mode == 'stats':
            pass

    def clip_mind_flay(self, time):
        if self.mode == 'verbose':
            self.log.write('{0}: Mind Flay clipped.\n'.format(format_time(time)))
        elif self.mode == 'stats':
            pass

    def finalize_log(self):
        self.log.close()
