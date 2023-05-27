import os


class NKA:
    def __init__(self, filename):
        self.stats_count = 0
        self.alphabet = list()
        self.stats = dict()
        self.start = None
        self.finite_states = list()
        self.e_nka = False

        if not filename:
            return
        with open(filename, 'r') as _:
            lines = _.readlines()
        self.stats_count = int(lines[0])

        self.alphabet = [i for i in lines[1].strip("[]\n").replace(" ", "").split(",")]

        for i in range(2, 2 + self.stats_count):
            line = lines[i].strip("\n ").replace(" ", "").split("=")
            try:
                stat = line[0]
                line = line[1].strip("{}").split("],")
                line = [_.replace("[", "").replace("]", "") for _ in line]
                for _ in line:
                    _ = _.split(":")
                    if str(stat) in self.stats:
                        self.stats[str(stat)] |= ({str(_[0]): str(", ".join(_[1].split(",")))})
                    else:
                        self.stats[str(stat)] = {str(_[0]): str(", ".join(_[1].split(",")))}
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
        print("e-NKA: ", self.e_nka, end="\n\n")

    def to_dka(self):
        # alphabet, Q =  состояния, s = старт
        #T = конечные, D = функции переходов
        res_DKA = DKA()
        P = [self.start]
        Qd = [self.start]
        Dd = {}

        while P:
            pd = "".join(P.pop(0)).replace(" ", "").split(",")
            for c in self.alphabet:
                qd = list()
                for p in pd:
                    if not p:
                        Dd[""] = {"": ""}
                        continue
                    if self.stats.get(p)[c] != "":
                        qd += self.stats.get(p)[c].replace(" ", "").split(",")
                # qd = [_ for _ in qd if _.isdigit() or _.isalpha()]
                qd = ", ".join(list(sorted(set(qd)))).strip()
                if ", ".join(pd) in Dd:
                    Dd[", ".join(pd)] |= ({c: qd})
                else:
                    Dd[", ".join(pd)] = {c: qd}
                if qd not in Qd:
                    P.append(qd)
                    Qd.append(qd)

        Td = []
        for qd in Qd:
            Td += [qd for s in self.finite_states if s in qd]

        res_DKA.start = self.start
        res_DKA.alphabet = self.alphabet
        res_DKA.stats = Dd
        res_DKA.stats_count = self.stats_count
        res_DKA.finite_states = Td
        return res_DKA


class DKA:
    def __init__(self, filename=None):
        self.stats_count = 0
        self.alphabet = list()
        self.stats = dict()
        self.start = None
        self.finite_states = list()
        self.e_nka = False

        if not filename:
            return
        with open(filename, 'r') as _:
            lines = _.readlines()
        self.stats_count = int(lines[0])

        self.alphabet = [i for i in lines[1].strip("[]\n").replace(" ", "").split(",")]

        for i in range(2, 2 + self.stats_count):
            line = lines[i].strip("\n ").replace(" ", "").split("=")
            try:
                stat = line[0]
                line = line[1].strip("{}").split("],")
                line = [_.replace("[", "").replace("]", "") for _ in line]
                for _ in line:
                    _ = _.split(":")
                    if str(stat) in self.stats:
                        self.stats[str(stat)] |= ({str(_[0]): str(", ".join(_[1].split(",")))})
                    else:
                        self.stats[str(stat)] = {str(_[0]): str(", ".join(_[1].split(",")))}
            except IndexError:
                print("error: wrong stat string")

        self.start = lines[2 + self.stats_count].strip("\n")
        self.finite_states = lines[2 + self.stats_count + 1].strip("[]").split(",")

    def info(self):
        print("Stats count: ", self.stats_count)
        print("Alphabet: ", self.alphabet)
        print("Stats: ", self.stats)
        print("Start stat: ", self.start)
        print("Finite stats: ", self.finite_states, end="\n\n")


def print_stats(ka):
    keys_ = [_ for _, __ in ka.stats.items()]
    print("{:20}".format(""), end="")
    for _ in ka.alphabet:
        print("{:10} {:10}".format("|", _), end="")
    print()
    sep = "-"
    sep *= (20 * 4) - 18
    print(sep)
    for k in keys_:
        if k in ka.finite_states:
            print("{:20}".format("*{" + k + "}"), end='')
        else:
            print("{:20}".format("{" + k + "}"), end='')
        for _ in list(ka.stats[k].values()):
            print("{:} {:19}".format("|", "{" + _ + "}"), end="")
        print()


if __name__ == '__main__':
    n = NKA("file5.txt")
    n.info()

    d = n.to_dka()
    d.info()

    print_stats(d)
