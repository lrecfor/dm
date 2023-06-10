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

    def to_reg(self):
        def to_reg_():
            keys_cpy = sorted(copy.deepcopy(list(self.stats.keys())), reverse=True)
            for stat in keys_cpy:
                if stat != self.start and stat not in self.finite_states:
                    del_stat = stat     # состояние, которое следует удалить
                    stats_lst = {}  # список переходов из удаляемого состояния
                    stats_to = []   # список состояний, в которые можно перейти из удаляемого
                    stats_from = []     # список состояний, из которых можно перейти в удаляемое
                    # цикл для заполнения выше описанных списков
                    for s in self.stats:
                        tmp_s = list(list(self.stats.values())[list(self.stats.keys()).index(s)].values())
                        if s == del_stat:
                            vals = list(self.stats[del_stat].values())
                            stats_lst[(del_stat, vals[0])] = list(self.stats[s].keys())[tmp_s.index(vals[0])]
                            stats_to += vals[0]
                            for _ in vals.pop():
                                stats_to += _
                                stats_lst[(del_stat, _)] = list(self.stats[s].keys())[tmp_s.index(_)]
                        if del_stat in self.stats[s].values():
                            stats_from += s

                    # для каждого перехода s из списка переходов из удаляемого состояния
                    # s(удаляемое состояние, состояние)
                    for s in stats_lst:
                        # если s это переход в себя же, переходим к следующему элементу
                        if s == (del_stat, del_stat):
                            continue
                        # для каждого состояния из списка состояний, из которых можно перейти в удаляемое
                        for chg_st in stats_from:
                            R, P, S, Q = "", "", "", ""
                            # если встретилось удаляемое состояние - переходим к следующему
                            if chg_st == del_stat:
                                continue
                            # переменные для доступа к элементам словаря
                            tmp_s = list(list(self.stats.values())[list(self.stats.keys()).index(chg_st)].values())
                            tmp_del = list(list(self.stats.values())[list(self.stats.keys()).index(del_stat)].values())
                            if s[1] in self.stats[chg_st].values():
                                # R - переход между обрабатываемым состоянием(chg_stat) и удаляемым
                                R = list(self.stats[chg_st].keys())[tmp_s.index(s[1])] + "+"
                                # удаляем из обрабатываемого состояния переход в удаляемое
                                self.stats[chg_st].pop(list(self.stats[chg_st].keys())[tmp_s.index(s[1])])
                                # обновляем переменную для доступа к элементам словаря
                                tmp_s = list(list(self.stats.values())[list(self.stats.keys()).index(chg_st)].values())
                            # если из обрабатываемого состояния можно перейти в удаляемое, сохраняем этот переход в Q
                            if del_stat in self.stats[chg_st].values():
                                Q = list(self.stats[chg_st].keys())[tmp_s.index(del_stat)]
                            # Р - переход из удаляемого состояния в состояние, в которое можно перейти из удаляемого
                            P = stats_lst[(del_stat, s[1])]
                            # если из удаляемого состояния можно перейти в него же, найдем S*
                            if del_stat in stats_from:
                                S = "".join(list(self.stats[del_stat].keys())[tmp_del.index(del_stat)])
                                # если длина S больше 1, заключаем S в скобки
                                if len(S) > 1:
                                    S = "(" + S + ")*"
                                else:
                                    S += "*"
                            # добавляем новый переход в таблицу переходов обрабатываемого состояния
                            # если переход из R существует, то добавляем скобки в начале и конце
                            if R != "":
                                self.stats[chg_st] |= {"(" + R + Q + S + P + ")": s[1]}
                            else:
                                # если не существует, то записываем без скобок
                                self.stats[chg_st] |= {R + Q + S + P: s[1]}
                    # удаляем состояние
                    self.stats.pop(del_stat)
                    # для каждого состояния, удаляем оставшиеся переходы в удаляемое состояние
                    for _ in self.stats.keys():
                        try:
                            tmp = list(list(self.stats.values())[list(self.stats.keys()).index(_)].values())
                            self.stats[_].pop(list(self.stats[_].keys())[tmp.index(del_stat)])
                        except ValueError:
                            continue

            P, Q, S, T = "", "", "", ""
            # если начальное состояние равно финальному, возвращаем его переход в себя с * на конце
            if len(list(self.stats.keys())) == 1:
                S = "(" + str(list(self.stats[list(self.stats.keys())[0]].keys())[list(self.stats.get(
                    list(self.stats.keys())[0]).values()).index(list(self.stats.keys())[0])]) + ")" + "*"
                return str(S)
            try:    # переход из начального в начальное
                P = list(self.stats[list(self.stats.keys())[0]].keys())[list(self.stats.get(
                    list(self.stats.keys())[0]).values()).index(list(self.stats.keys())[0])]
            except ValueError:
                pass
            try:    # переход из начального состояния в финальное
                Q = "(" + str(list(self.stats[list(self.stats.keys())[0]].keys())[list(self.stats.get(
                    list(self.stats.keys())[0]).values()).index(list(self.stats.keys())[1])]) + ")"
            except ValueError:
                pass
            try:    # переход их финального в финальный
                S = "(" + str(list(self.stats[list(self.stats.keys())[1]].keys())[list(self.stats.get(
                    list(self.stats.keys())[1]).values()).index(list(self.stats.keys())[1])]) + ")" + "*"
            except ValueError:
                pass
            try:    # переход из финального в начальное
                T = "(" + str(list(self.stats[list(self.stats.keys())[1]].keys())[list(self.stats.get(
                    list(self.stats.keys())[1]).values()).index(list(self.stats.keys())[0])]) + ")"
            except ValueError:
                pass
            if T == "" or Q == "":
                if P != "":
                    return "(" + str(P) + ")*" + str(Q) + str(S)
                else:
                    return str(Q) + str(S)
            return "(" + str(P) + "+" + str(Q) + str(S) + str(T) + ")*" + str(Q) + str(S)

        # если количество финальных состояний больше 1
        if len(self.finite_states) > 1:
            stats = copy.deepcopy(self.stats)   # изначальная таблица переходов
            finite_states = copy.deepcopy(list(self.finite_states))     # изначальный список финальных состояний

            to_reg_()   # вызываем функцию преобразования единожды для
            # удаления всех состояний, кроме начального и финальных
            R_ = []     # список получаемых регулярных выражений
            stats_cpy = copy.deepcopy(self.stats)   # копия таблицы переходов после удаления
            # копия списка финальных состояний
            finite_states_cpy = sorted(copy.deepcopy(list(self.finite_states)), reverse=True)
            # присваиваем таблице состояний дка полученную после удаления таблицу
            self.stats = copy.deepcopy(stats_cpy)
            # для каждого финального состояния из копии изначальных
            for _ in finite_states_cpy:
                # удаляем все состояния, кроме _
                for __ in finite_states:
                    if __ != _:
                        self.finite_states.remove(__)
                # вызываем функцию и записываем полученное регулярное выражение в R_
                R_ += [to_reg_()]
                # возвращаем изначальный список финальных состояний
                self.finite_states = finite_states
                # присваиваем таблице состояний значение таблицы переходов после удаления
                self.stats = copy.deepcopy(stats_cpy)
            # возвращаем изначальную таблицу переходов
            self.stats = copy.deepcopy(stats)
            # возвращаем склеенный список полученных регулярных выражений
            return "+".join(R_)
        else:
            return to_reg_()


if __name__ == '__main__':
    n = NKA("file.txt")
    d = n.to_dka()

    # d = DKA("dka_2.txt")
    d.info()

    print(d.to_reg())
