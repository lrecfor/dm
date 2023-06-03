import print as p


class NKA:
    def __init__(self, filename=None):
        self.stats_count = 0
        self.alphabet = list()
        self.stats = dict()
        self.start = None
        self.finite_states = list()
        self.e_nka = False
        self.cur_stat = "x"

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
            self.alphabet.remove("e")

    def info(self):
        print("Stats count: ", self.stats_count)
        print("Alphabet: ", self.alphabet)
        print("Stats: ", self.stats)
        print("Start stat: ", self.start)
        print("Finite stats: ", self.finite_states)
        print("e-NKA: ", self.e_nka, end="\n\n")

    def chk(self, chain_):
        def chk_(chain, indx=0, cur_stat=self.start):
            if self.e_nka:
                e_close = self.e_closure()

            if indx == len(chain):
                self.__returns.append(0)
                return 0

            if self.e_nka == 1:
                cur_stat = [", ".join(set(_).union(set(e_close[_]))) for _ in cur_stat]
                cur_stat = list(set((", ".join(cur_stat)).replace(" ", "").split(",")))
                cur_stat = ", ".join(set([self.stats[_][chain[indx]] for _ in cur_stat
                                          if self.stats[_][chain[indx]] != ""]))
            else:
                cur_stat = self.stats[cur_stat][chain[indx]]
            if cur_stat == "":
                self.__returns.append(0)
                return 0
            if ", " in cur_stat:
                cur_stat = cur_stat.replace(" ", "").split(",")
                for _ in cur_stat:
                    chk_(chain, indx + 1, _)
                    if _ in self.finite_states and indx == len(chain) - 1:
                        self.__returns.append(1)
                        return 1
            else:
                chk_(chain, indx + 1, cur_stat)
                if cur_stat in self.finite_states and indx == len(chain) - 1:
                    self.__returns.append(1)
                    return 1

        chk_(chain_)
        if 1 in self.__returns:
            self.__returns = []
            return 1
        self.__returns = []
        return 0

    def e_closure(self):
        e_close = {}

        graph = {
            'A': ['B', 'C'],
            'B': ['D', 'E'],
            'C': ['F'],
            'D': [],
            'E': ['F'],
            'F': []
        }
        visited = []  # List to keep track of visited nodes.
        queue = []  # Initialize a queue

        def bfs(visited, graph, node):
            visited.append(node)
            queue.append(node)
            while queue:
                s = queue.pop(0)
                for neighbour in graph[s]:
                    if neighbour not in visited:
                        visited.append(neighbour)
                        queue.append(neighbour)

        # Driver Code
        bfs(visited, self.stats, 1)

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
                for p_ in pd:
                    if not p_:
                        break
                    if self.stats.get(p_)[c] != "" and len(self.stats.get(p_)[c]) > 0:
                        qd += self.stats.get(p_)[c].replace(" ", "").split(",")
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

        if self.start not in Dd:
            for _ in Dd.keys():
                if self.start in list(_):
                    res_DKA.start = _
                    break
        else:
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
        cur_stat = self.start

        for symb in chain:
            cur_stat = self.stats[cur_stat][symb]

        if cur_stat not in self.finite_states:
            return 0
        return 1

    def minimize(self):
        tbl = {i: {j: "o" if j != i and j < i else "-" for j in list(self.stats.keys())}
               for i in list(self.stats.keys())}
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

        # p.print_tbl(tbl)

        def chg_stats():
            new_stats = []
            for i in tbl:
                for j in tbl:
                    if tbl.get(i)[j] == 'o' or tbl.get(i)[j] == 'o':
                        new_stats.append([j, i])

            n_st = list(tbl.keys())
            for i in range(0, len(n_st)):
                for j in new_stats:
                    if set(n_st[i]).intersection(set(j)):
                        n_st[i] = set(n_st[i]).union(set(j))
                n_st[i] = ", ".join(sorted(n_st[i]))
            n_st = list(set(n_st))

            temp_stats = self.stats.copy()
            self.stats = {}
            for i in n_st:
                nst_stat = temp_stats.get(i[0])
                for k in self.alphabet:
                    n_val = nst_stat[k]
                    for stat in n_st:
                        if n_val in stat:
                            n_val = stat
                            break
                    if i in self.stats:
                        self.stats[i] |= ({k: n_val})
                    else:
                        self.stats[i] = ({k: n_val})
            if self.start not in self.stats:
                for _ in self.stats.keys():
                    if self.start in list(_):
                        self.start = _
                        break

            new_fin_stats = []
            for _ in self.stats.keys():
                for f in self.finite_states:
                    if f in list(_):
                        new_fin_stats.append(_)
            self.finite_states = new_fin_stats

        chg_stats()


if __name__ == '__main__':
    n = NKA()
    n.info()

    d = DKA()
    d.info()
