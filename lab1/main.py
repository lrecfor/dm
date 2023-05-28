import print as p


class NKA:
    def __init__(self, filename):
        self.stats_count = 0
        self.alphabet = list()
        self.stats = dict()
        self.start = None
        self.finite_states = list()
        self.e_nka = False
        self.cur_stat = "x"

        self.__shiza = []

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

    def chk(self, chain_):
        def chk_(chain, indx=0, cur_stat='x'):
            if set(chain).difference(set(self.alphabet)):
                return 0

            if indx == len(chain):
                self.__shiza.append(0)
                return 0

            cur_stat = self.stats[cur_stat][chain[indx]]
            if cur_stat == "":
                self.__shiza.append(0)
                return 0
            if ", " in cur_stat:
                cur_stat = cur_stat.replace(" ", "").split(",")
                for _ in cur_stat:
                    chk_(chain, indx + 1, _)
                    if _ in self.finite_states and indx == len(chain) - 1:
                        self.__shiza.append(1)
                        return 1
            else:
                chk_(chain, indx + 1, cur_stat)
                if cur_stat in self.finite_states and indx == len(chain) - 1:
                    self.__shiza.append(1)
                    return 1

        chk_(chain_)
        if 1 in self.__shiza:
            return 1
        return 0

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
        self.finite_states = lines[2 + self.stats_count + 1].strip("[]").replace(" ", "").split(",")

    def info(self):
        print("Stats count: ", self.stats_count)
        print("Alphabet: ", self.alphabet)
        print("Stats: ", self.stats)
        print("Start stat: ", self.start)
        print("Finite stats: ", self.finite_states, end="\n\n")

    def chk(self, chain):
        if set(chain).difference(set(self.alphabet)):
            return 0

        cur_stat = self.start

        for symb in chain:
            cur_stat = self.stats[cur_stat][symb]

        if cur_stat not in self.finite_states:
            return 0
        return 1

    def minimize(self):
        tbl = {i: {j: "o" if j != i and j < i else "-" for j in list(self.stats.keys())} for i in list(self.stats.keys())}
        for i in tbl:
            for j in tbl.get(i):
                if (i in self.finite_states and j < i) or (j in self.finite_states and i > j):
                    if i in self.finite_states and j in self.finite_states:
                        continue
                    tbl.get(i)[j] = "x"

        for _ in range(0, 2):
            stop_fl = 0
            for i in tbl:
                if stop_fl == 1:
                    break
                for j in list(tbl.keys())[list(tbl.keys()).index(i) + 1:]:
                    stop_fl = 1
                    frst = self.stats.get(i)
                    scnd = self.stats.get(j)
                    for st in self.alphabet:
                        if tbl.get(frst[st])[scnd[st]] == "x" or tbl.get(scnd[st])[frst[st]] == "x":
                            if j > i:
                                tbl.get(j)[i] = "x"
                            else:
                                tbl.get(i)[j] = "x"
                        stop_fl = 0
        p.print_tbl(tbl)

        # temp_stats = self.stats.copy()
        # self.stats = {}
        new_stats = []

        for i in tbl:
            for j in tbl:
                if tbl.get(i)[j] == 'o' or tbl.get(i)[j] == 'o':
                    new_stats.append([j, i])
        print(new_stats)
        n_st = list(tbl.keys())
        for i in range(0, len(n_st)):
            for j in new_stats:
                if set(n_st[i]).intersection(set(j)):
                    n_st[i] = set(n_st[i]).union(set(j))
            n_st[i] = ", ".join(sorted(n_st[i]))
        n_st = list(set(n_st))
        print(n_st)


if __name__ == '__main__':
    n = NKA("lab1/nka1.txt")
    n.info()
    # p.print_in_file(n.to_dka())

    d = DKA("lab1/dka3.txt")
    d.info()
    p.print_(d)

    # print("checking chains: ")
    # print("DKA(): ", d.chk("101001"))
    # print("NKA(): ", n.chk("0100100"))

    # out = p.test(d)
    # exit(1)

    d.minimize()
    # p.print_(d)
