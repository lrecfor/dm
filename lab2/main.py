import copy


class NKA:
    def __init__(self, filename=None):
        self.stats_count = 0
        self.alphabet = list()
        self.stats = dict()
        self.start = None
        self.finite_states = list()
        self.e_nka = False
        self.e_close = []

        self.__returns = []

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
                        self.stats[str(stat)] |= ({k: []})
                    else:
                        self.stats[str(stat)] = ({k: []})
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
            self.e_close = self.e_closure()

    def info(self):
        print("Stats count: ", self.stats_count)
        print("Alphabet: ", self.alphabet)
        print("Stats: ", self.stats)
        print("Start stat: ", self.start)
        print("Finite stats: ", self.finite_states)
        print("e-NKA: ", self.e_nka, end="\n\n")

    def chk(self, chain):
        if len(list(set(chain).difference(set(self.alphabet)))) != 0 and \
                (self.e_nka and list(set(chain).difference(set(self.alphabet))) != "e"):
            return 0
        cur_stat = [self.start]

        for symb in chain:
            if self.e_nka:
                cur_stat_cpy = list(set((", ".join(cur_stat)).replace(" ", "").split(",")))
                cur_stat = [", ".join(set(_).union(set(self.e_close[_]))) for _ in cur_stat_cpy]
                cur_stat = list(set((", ".join(cur_stat)).replace(" ", "").split(",")))
            cur_stat_cpy = list(set((", ".join(cur_stat)).replace(" ", "").split(",")))
            cur_stat = list(set([self.stats[_][symb] for _ in cur_stat_cpy if self.stats[_][symb] != ""]))
            if len(cur_stat) == 0:
                return 0
            if self.e_nka:
                cur_stat_cpy = list(set((", ".join(cur_stat)).replace(" ", "").split(",")))
                cur_stat = [", ".join(set(_).union(set(self.e_close[_]))) for _ in cur_stat_cpy]
                cur_stat = list(set((", ".join(cur_stat)).replace(" ", "").split(",")))
                if len(cur_stat) == 0:
                    return 0

        if len(list(set(self.finite_states) & set(cur_stat))) != 0:
            return 1
        return 0

    def e_closure(self):
        e_close = {}

        def bfs(graph, node):
            visited = []
            queue = []
            visited.append(node)
            queue.append(node)
            while queue:
                s = queue.pop(0)
                for neighbour in graph[s]["e"]:
                    if neighbour not in visited:
                        visited.append(neighbour)
                        queue.append(neighbour)
            return list(sorted(visited))

        for stat in self.stats:
            e_close[stat] = bfs(self.stats, stat)

        return e_close

    def to_dka(self):
        res_DKA = DKA()
        P = [self.start]
        Qd = [self.start]
        Dd = {}

        if self.e_nka:
            P = [", ".join(self.e_close.get(P[0]))]

        while P:
            pd = "".join(P.pop(0)).replace(" ", "").split(",")
            for c in list(set(self.alphabet).difference(set("e"))):
                qd = list()
                for p_ in pd:
                    if not p_:
                        break
                    if self.stats.get(p_)[c] != "" and len(self.stats.get(p_)[c]) > 0:
                        qd += self.stats.get(p_)[c].replace(" ", "").split(",")
                    if self.e_nka and qd:
                        for q in set(qd):
                            qd += self.e_close.get(q)
                qd = ", ".join(list(sorted(set(qd)))).strip()
                if ", ".join(pd) in Dd:
                    Dd[", ".join(pd)] |= ({c: qd})
                else:
                    Dd[", ".join(pd)] = {c: qd}
                if qd not in Qd:
                    P.append(qd)
                    Qd.append(qd)

        Td = []
        for qd in list(Dd.keys()):
            Td += [qd for s in self.finite_states if s in qd]

        if self.start not in Dd:
            for _ in Dd.keys():
                if self.start in list(_):
                    res_DKA.start = _
                    break
        else:
            res_DKA.start = self.start
        res_DKA.alphabet = list(set(self.alphabet).difference(set("e")))
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
        cur_stat = self.start

        for symb in chain:
            try:
                cur_stat = self.stats[cur_stat][symb]
            except KeyError:
                return 0

        if cur_stat not in self.finite_states:
            return 0
        return 1


if __name__ == '__main__':
    n = NKA("file.txt")
    # d = n.to_dka()

    d = DKA("dka_2.txt")
    d.info()


