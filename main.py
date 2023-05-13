import os


class NKA:
    def __init__(self, filename):
        self.stats_count = 0
        self.alphabet = list()
        self.stats = list()
        self.start = None
        self.finite_states = list()
        self.e_nka = False

        with open(filename, 'r') as _:
            lines = _.readlines()
        self.stats_count = int(lines[0])

        self.alphabet = [i for i in lines[1].strip("[]\n").split(",")]

        for i in range(2, 2 + self.stats_count):
            line = lines[i].strip("\n ").replace(" ", "").split("=")
            try:
                line = line[1].strip("{}").split("],")
                line = [_.replace("[", "").replace("]", "") for _ in line]
                for _ in line:
                    _ = _.split(":")
                    self.stats.append([_[0], _[1].split(",")])
            except IndexError:
                print("error: wrong stat string")

        self.start = lines[2 + self.stats_count].strip("\n")
        self.finite_states = lines[2 + self.stats_count + 1].strip("[]").split(",")
        if "e" in self.alphabet:
            self.e_nka = True

    def nkainfo(self):
        print(self.stats_count)
        print(self.alphabet)
        print(self.stats)
        print(self.start)
        print(self.finite_states)
        print(self.e_nka)

class DKA:
    def __init__(self):
        print()


if __name__ == '__main__':
    n = NKA("file1.txt")
    n.nkainfo()
