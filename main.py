import os

class NKA:
    def __init__(self, filename):
        self.stats_count = 0
        self.alphabet = list()
        self.stats = list()
        self.start = None
        self.finite_states = list()
        self.e_nka = 0

        with open(filename, 'r') as _:
            lines = _.readlines()
        self.stats_count = int(lines[0])

        self.alphabet = [i for i in lines[1].strip("[]\n").split(",")]

        for i in range(2, 2 + self.stats_count):
            line = lines[i].strip("}\n").split("{")
            for l in range(1, len(line)):
                print(line[l][(line[l].find('[') + 1):(line[l].find(']'))])


class DKA:
    def __init__(self):
        print()

        # 2  # число состояний НКА
        # [0, 1]  # алфавит
        # Q0 = {0: [Q1], 1: []}  # описание первого состояния
        #  # <символ алфавита>:[<список состояний, в которые переходит автомат по данному символу>]
        # Q1 = {0: [Q0, Q1], 1: [Q1]}  # описание второго состояния
        # Q0  # начальное состояние
        # [Q1]  # список допустимых состояний


if __name__ == '__main__':
    n = NKA("file1.txt")
