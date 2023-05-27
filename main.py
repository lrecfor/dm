import os


class NKA:
    def __init__(self, filename):
        self.stats_count = 0
        self.alphabet = list()
        self.stats = dict()
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
                stat = line[0]
                line = line[1].strip("{}").split("],")
                line = [_.replace("[", "").replace("]", "") for _ in line]
                for _ in line:
                    _ = _.split(":")
                    if str(stat) not in self.stats:
                        self.stats[str(stat)] = [[str(_[0]), str(", ".join(_[1].split(",")))]]
                    else:
                        self.stats[str(stat)].append([str(_[0]), str(", ".join(_[1].split(",")))])
            except IndexError:
                print("error: wrong stat string")

        self.start = lines[2 + self.stats_count].strip("\n")
        self.finite_states = lines[2 + self.stats_count + 1].strip("[]").split(",")
        if "e" in self.alphabet:
            self.e_nka = True

    def info(self):
        print("Stats count: ", self.stats_count)
        print("Alphabet: ", self.alphabet)
        print("Stats: ", self.stats)
        print("Start stat: ", self.start)
        print("Finite stats: ", self.finite_states)
        print("e-NKA: ", self.e_nka)

    def e_closure(self, Q):
        ReachableStates = None
        nextStates = None

        for q in Q:
            nextStates = e_closure(q)
            if nextStates:
                if nextStates not in ReachableStates:
                    ReachableStates = ReachableStates + nextStates
        return ReachableStates

    def to_dka(self):
        # alphabet, Q =  состояния, s = старт
        #T = конечные, D = функции переходов
        res_DKA = DKA()
        P = list(self.start)
        Qd = list()
        Dd = dict()

        while P:
            pd = P.pop(0)
            for c in self.alphabet:
                qd = list()
                for p in pd:
                    if not self.alphabet[0].isdigit():
                        qd = qd + self.stats.get(p)[self.alphabet.index(c)][1]
                    # else:
                    #    qd = qd + self.stats.get(p)[int(c)][1]
                Dd[str(pd)] = [[c, qd]]
                if qd not in Qd:
                    P.append(qd)
                    Qd.append(qd)
        # Td =

        return res_DKA


class DKA:
    def __init__(self, filename=None):
        self.stats_count = 0
        self.alphabet = list()
        self.stats = dict()
        self.start = None
        self.finite_states = list()

        if filename is not None:
            with open(filename, 'r') as _:
                lines = _.readlines()
            self.stats_count = int(lines[0])

            self.alphabet = [i for i in lines[1].strip("[]\n").split(",")]

            for i in range(2, 2 + self.stats_count):
                line = lines[i].strip("\n ").replace(" ", "").split("=")
                try:
                    stat = line[0]
                    line = line[1].strip("{}").split("],")
                    line = [_.replace("[", "").replace("]", "") for _ in line]
                    for _ in line:
                        _ = _.split(":")
                        if str(stat) not in self.stats:
                            self.stats[str(stat)] = [_[0], _[1].split(",")]
                        else:
                            self.stats[str(stat)].append([_[0], _[1].split(",")])
                except IndexError:
                    print("error: wrong stat string")

            self.start = lines[2 + self.stats_count].strip("\n")
            self.finite_states = lines[2 + self.stats_count + 1].strip("[]").split(",")

    def info(self):
            print("Stats count: ", self.stats_count)
            print("Alphabet: ", self.alphabet)
            print("Stats: ", self.stats)
            print("Start stat: ", self.start)
            print("Finite stats: ", self.finite_states)


if __name__ == '__main__':
    n = NKA("file3.txt")
    n.info()

    d = n.to_dka()
    d.info()