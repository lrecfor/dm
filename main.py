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

        self.alphabet = [str(i) for i in lines[1].strip("[]\n").replace(" ", "").split(",")]

        for i in range(2, 2 + self.stats_count):
            line = lines[i].strip("\n ").replace(" ", "").split("=")
            try:
                stat = str(line[0])
                line = line[1].strip("{}").split("],")
                line = [_.replace("[", "").replace("]", "") for _ in line]
                for k in self.alphabet:
                    if str(stat) in self.stats:
                        self.stats[str(stat)] |= ({k: {}})
                    else:
                        self.stats[str(stat)] = ({k: {}})
                for _ in line:
                    _ = _.split(":")
                    if _[0] not in self.alphabet:
                        print("error: wrong stat string")
                        exit(-1)
                    self.stats[stat][str(_[0])] = str(", ".join(_[1].split(",")))
            except IndexError:
                print("error: wrong stat string")
                exit(-1)

        self.start = lines[2 + self.stats_count].strip("\n")
        self.finite_states = lines[2 + self.stats_count + 1].strip("[]").split(",")
        if "e" in self.alphabet:
            self.e_nka = True
            self.alphabet.remove("e")

    def info(self):
        print("Stats count: ", self.stats_count)
        print("Alphabet: ", self.alphabet)
        print("Stats: ", self.stats)
        print("Start stat: ", self.start)
        print("Finite stats: ", self.finite_states)
        print("e-NKA: ", self.e_nka, end="\n\n")

    def e_closure(self):
        e_close = {}

        for q1, v1 in self.stats.items():
            lst = []
            for _ in v1.items():
                lst += self.stats.get(q1)["e"].replace(" ", "").split(",")
            e_close[q1] = list(set(lst + [q1]))

        for e_cl in reversed(self.stats.keys()):
            if "" in e_close[e_cl]:
                e_close[e_cl].remove("")
            for s in e_close[e_cl]:
                if s != e_cl:
                    lst = e_close.get(s)
                    if "" in lst:
                        lst.remove("")
                    if lst is not None:
                        e_close[e_cl] = sorted(list(set(lst + e_close[e_cl])))

        return e_close

    def to_dka(self):
        res_DKA = DKA()
        P = [self.start]
        Qd = [self.start]
        Dd = {}
        e_close = {}

        if self.e_nka:
            e_close = self.e_closure()
            P = [", ".join(e_close.get(P[0]))]

        while P:
            pd = "".join(P.pop(0)).replace(" ", "").split(",")
            for c in self.alphabet:
                qd = list()
                for p in pd:
                    if not p:
                        break
                    if self.stats.get(p)[c] != "" and len(self.stats.get(p)[c]) > 0:
                        qd += self.stats.get(p)[c].replace(" ", "").split(",")
                    if self.e_nka and qd:
                        for q in set(qd):
                            qd += e_close.get(q)
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

        if not filename:
            return
        with open(filename, 'r') as _:
            lines = _.readlines()
        self.stats_count = int(lines[0])

        self.alphabet = [str(i) for i in lines[1].strip("[]\n").replace(" ", "").split(",")]

        for i in range(2, 2 + self.stats_count):
            line = lines[i].strip("\n ").replace(" ", "").split("=")
            try:
                stat = str(line[0])
                line = line[1].strip("{}").split("],")
                line = [_.replace("[", "").replace("]", "") for _ in line]
                for k in self.alphabet:
                    if str(stat) in self.stats:
                        self.stats[str(stat)] |= ({k: {}})
                    else:
                        self.stats[str(stat)] = ({k: {}})
                for _ in line:
                    _ = _.split(":")
                    if _[0] not in self.alphabet:
                        print("error: wrong stat string")
                        exit(-1)
                    self.stats[stat][str(_[0])] = str(", ".join(_[1].split(",")))
            except IndexError:
                print("error: wrong stat string")
                exit(-1)

        self.start = lines[2 + self.stats_count].strip("\n")
        self.finite_states = lines[2 + self.stats_count + 1].strip("[]").split(",")

    def info(self):
            print("Stats count: ", self.stats_count)
            print("Alphabet: ", self.alphabet)
            print("Stats: ", self.stats)
            print("Start stat: ", self.start)
            print("Finite stats: ", self.finite_states, end="\n\n")

    def chk(self, chain):
        if set(chain).difference(set(self.alphabet)):
            return 0

        k = list(self.stats.keys())
        cur_stat = self.start

        for symb in chain:
            cur_stat = self.stats[cur_stat][symb]

        if cur_stat not in self.finite_states:
            return 0
        return 1


def print_(ka):
    keys_ = [_ for _, __ in ka.stats.items()]
    print("{:20}".format(""), end="")
    for _ in ka.alphabet:
        if _ != "e":
            print("{:10} {:10}".format("|", _), end="")
    print()
    sep = "-"
    mul = len(ka.alphabet) + 1
    sep *= ((20 * mul) + mul)
    print(sep)
    for k in keys_:
        if k in ka.finite_states:
            print("{:20}".format("*{" + k + "}"), end='')
        else:
            print("{:20}".format("{" + k + "}"), end='')
        for _ in list(ka.stats[k].values()):
            print("{:} {:19}".format("|", "{" + _ + "}"), end="")
        print()
    print(end="\n")


def print_in_file(ka, filename="output.txt"):
    file = open(filename, "w")
    keys_ = [_ for _, __ in ka.stats.items()]
    file.write(str("{:20}".format("")))
    for _ in ka.alphabet:
        if _ != "e":
            file.write(str("{:10} {:10}".format("|", _)))
    file.write("\n")
    sep = "-"
    mul = len(ka.alphabet) + 1
    sep *= ((20 * mul) + mul)
    file.write(sep + "\n")
    for k in keys_:
        if k in ka.finite_states:
            file.write(str("{:20}".format("*{" + k + "}")))
        else:
            file.write(str("{:20}".format("{" + k + "}")))
        for _ in list(ka.stats[k].values()):
            file.write(str("{:} {:19}".format("|", "{" + _ + "}")))
        file.write("\n")


def test(ka):
    number = 1023
    length = number.bit_length()
    results = []

    while number >= 0:
        chain = bin(number)[2:]
        if len(chain) < length:
            chain = str('0' * (length - len(chain))) + chain
        results.append({chain: ka.chk(chain)})
        number -= 1

    return results


if __name__ == '__main__':
    n = NKA("file2.txt")
    n.info()

    d = DKA("dka1.txt")
    d.info()
    print_(d)
    print(d.chk("101001"))

    out = test(d)
    exit(1)

# В качестве проверки нужно взять все цепочки
# в алфавите длины не более 10 и применить к ним оба автомата.