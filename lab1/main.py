import print as p
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
        # если в строке есть символы, отличные от алфавита возвращаем False
        if len(list(set(chain).difference(set(self.alphabet)))) != 0 and \
                (self.e_nka and list(set(chain).difference(set(self.alphabet))) != "e"):
            return 0
        # текущее состояние равно начальному
        cur_stat = [self.start]

        # цикл по каждому символу из строки
        for symb in chain:
            # если это е-нка, то объединяем состояния с е-замыканием до перехода,
            # чтобы исключить переход в пустое множество при наличии других состояний в е-замыкании текущего состояния
            if self.e_nka:
                # если cur_stat это строка из нескольких состояний, преобразуем ее в список отдельных состояний
                cur_stat_cpy = list(set((", ".join(cur_stat)).replace(" ", "").split(",")))
                # для каждого состояния из cur_stat объединяем его с е-замыканием
                cur_stat = [", ".join(set(_).union(set(self.e_close[_]))) for _ in cur_stat_cpy]
                # если получили несколько состояний - преобразуем их в список состояний
                cur_stat = list(set((", ".join(cur_stat)).replace(" ", "").split(",")))
            # делаем переход
            # если получили несколько состояний - преобразуем их в список состояний
            cur_stat_cpy = list(set((", ".join(cur_stat)).replace(" ", "").split(",")))
            # для каждого состояния находим переход
            cur_stat = list(set([self.stats[_][symb] for _ in cur_stat_cpy if self.stats[_][symb] != ""]))
            # если переход осуществлен в пустое множество возвращаем False
            if len(cur_stat) == 0:
                return 0
            # если это е-нка объединяем состояния после перехода с е-замыканием
            if self.e_nka:
                cur_stat_cpy = list(set((", ".join(cur_stat)).replace(" ", "").split(",")))
                cur_stat = [", ".join(set(_).union(set(self.e_close[_]))) for _ in cur_stat_cpy]
                cur_stat = list(set((", ".join(cur_stat)).replace(" ", "").split(",")))
                if len(cur_stat) == 0:
                    return 0

        # если текущее состояние находится в числе конечных - возвращаем True
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
        P = [self.start]    # список состояний, по которому мы будем итерироваться
        Qd = [self.start]   # список состояний дка
        Dd = {}             # таблица переходов дка

        # если это е-нка, объединяем начальное состояние с e-замыканием
        if self.e_nka:
            P = [", ".join(self.e_close.get(P[0]))]

        # пока Р не пустое множество
        while P:
            # выталкиваем из P очередное состояние
            pd = "".join(P.pop(0)).replace(" ", "").split(",")
            # проходим в цикле для каждого возможного для перехода состояния
            for c in list(set(self.alphabet).difference(set("e"))):
                qd = list()
                for p_ in pd:
                    if not p_:
                        break
                    # в qd накапливаем все возможные для перехода состояния
                    if self.stats.get(p_)[c] != "" and len(self.stats.get(p_)[c]) > 0:
                        qd += self.stats.get(p_)[c].replace(" ", "").split(",")
                    # если это е-нка, то объединяем каждое состояние qd с е-замыканием
                    if self.e_nka and qd:
                        for q in set(qd):
                            qd += self.e_close.get(q)
                # переводим список qd в строку состояний
                qd = ", ".join(list(sorted(set(qd)))).strip()
                # добавляем в таблицу переходов запись qd
                if ", ".join(pd) in Dd:
                    Dd[", ".join(pd)] |= ({c: qd})
                else:
                    Dd[", ".join(pd)] = {c: qd}
                if qd not in Qd:
                    P.append(qd)    # добавляем следующее состояние для вычисления в Р
                    Qd.append(qd)   # добавляем в список состояний полученный qd

        # находим финальные состояния Td из списка состояний Qd
        Td = []
        for qd in list(Dd.keys()):
            Td += [qd for s in self.finite_states if s in qd]

        # изменяем начальное состояние в соответствие с построенным дка
        if self.start not in Dd:
            for _ in Dd.keys():
                if self.start in list(_):
                    res_DKA.start = _
                    break
        else:
            res_DKA.start = self.start
        res_DKA.alphabet = list(set(self.alphabet).difference(set("e")))    # добавляем алфавит
        res_DKA.stats = Dd                                                  # добавляем таблицу состояний
        res_DKA.stats_count = self.stats_count                              # добавляем количество состояний
        res_DKA.finite_states = Td                                          # добавляем список финальных состояний

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
    # n = NKA("lab1/file5.txt")
    # n.info()
    #
    # d = DKA("lab1/dka_1.txt")
    # d.info()

    # f = open("lab1/rv1.txt", "r")
    # print(d.to_reg())

    n = NKA("lab1/file.txt")
    n.info()
    p.print_(n)

    print("nka to dka: ")
    # p.print_in_file(n.to_dka())
    d_test = n.to_dka()
    p.print_(d_test)
    print(n.chk("0"))

    # out1 = p.test(d_test)
    # out2 = p.test(n)
    # print("checking chains: ", out1 == out2)
