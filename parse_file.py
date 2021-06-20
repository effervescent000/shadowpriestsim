import player
from openpyxl import load_workbook


class ParseFile:

    def __init__(self, fn):
        # TODO rehaul this code to read from a txt file rather than a spreadsheet
        self.wb = load_workbook(fn)
        self.sheet = self.wb['data']
        self.player = player.Player("priest", 'base')
        row = 2
        self.toons = [self.parse_toon(self.player, row)]

        if self.check_comparison() is True:
            row = 3
            comp_num = 1
            while self.sheet.cell(row, 1).value is not None:
                new_toon = player.Player("priest", comp_num)
                self.toons.append(self.parse_toon(new_toon, row))

                comp_num = comp_num + 1
                row = row + 1

    def check_comparison(self):
        row = 3
        if self.sheet.cell(row, 1).value is not None:
            return True
        else:
            return False

    def parse_toon(self, toon, row):
        # first set baseline stats
        stats_dict = {}
        for x in range(1, 11):
            stats_dict[self.sheet.cell(1, x).value] = self.sheet.cell(row, x).value
        toon.assign_dict_stats(stats_dict)
        return toon
