import player
from openpyxl import load_workbook


class ParseFile:

    def __init__(self, fn):
        # TODO overhaul this code to read from a txt file rather than a spreadsheet. Maybe. I'm not sure how comparisons
        #  would work with this?
        self.wb = load_workbook(fn)
        self.sheet = self.wb['data']
        self.player = player.Player("priest", 'base')
        col = 2
        self.toons = [self.parse_toon(self.player, col)]

        if self.check_comparison() is True:
            col = 3
            comp_num = 1
            while self.sheet.cell(2, col).value is not None:
                new_toon = player.Player("priest", comp_num)
                self.toons.append(self.parse_toon(new_toon, col))

                comp_num = comp_num + 1
                col = col + 1

    def check_comparison(self):
        col = 3
        if self.sheet.cell(1, col).value is not None:
            return True
        else:
            return False

    def parse_toon(self, toon, col):
        # first set baseline stats
        stats_dict = {}
        row = 2
        string = string = self.sheet.cell(row, 1).value

        while string != '###talents':
            stats_dict[self.sheet.cell(row, 1).value] = self.sheet.cell(row, col).value
            row += 1
            string = self.sheet.cell(row, 1).value
        toon.assign_dict_stats(stats_dict)
        return toon
