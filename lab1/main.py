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
            e_close = None

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

    def plus(self, R, T):
        self.stats["Q" + str(self.stats_count)] = {str("e"): ["Q" + str(self.stats_count + 1),
                                                              "Q" + str(self.stats_count + 2)]}

        self.stats["Q" + str(self.stats_count + 1)] = {R: ["Q" + str(self.stats_count + 3)]}
        self.stats["Q" + str(self.stats_count + 2)] = {T: ["Q" + str(self.stats_count + 4)]}

        self.stats["Q" + str(self.stats_count + 3)] = {str("e"): ["Q" + str(self.stats_count + 5)]}
        self.stats["Q" + str(self.stats_count + 4)] = {str("e"): ["Q" + str(self.stats_count + 5)]}

        self.stats_count += 5

    def mul(self, R, T):
        self.stats["Q" + str(self.stats_count)] = {str("e"): ["Q" + str(self.stats_count + 1)]}
        self.stats["Q" + str(self.stats_count + 1)] = {R: ["Q" + str(self.stats_count + 2)]}
        self.stats["Q" + str(self.stats_count + 2)] = {str("e"): ["Q" + str(self.stats_count + 3)]}
        self.stats["Q" + str(self.stats_count + 3)] = {T: ["Q" + str(self.stats_count + 4)]}
        self.stats["Q" + str(self.stats_count + 4)] = {str("e"): ["Q" + str(self.stats_count + 5)]}

        self.stats_count += 5

    def iter(self, R):
        self.stats["Q" + str(self.stats_count)] = {str("e"): ["Q" + str(self.stats_count + 1)]}
        self.stats["Q" + str(self.stats_count + 1)] = {R: ["Q" + str(self.stats_count + 2)]}
        self.stats["Q" + str(self.stats_count + 2)] = {str("e"): ["Q" + str(self.stats_count + 3)]}

        self.stats["Q" + str(self.stats_count)] = {str("e"): ["Q" + str(self.stats_count + 3)]}
        self.stats["Q" + str(self.stats_count + 2)] = {str("e"): ["Q" + str(self.stats_count + 1)]}

        self.stats_count += 3

    def fr_rv(self, rv, start_stat, end_start):
        i = 0
        while i < len(rv):
            if rv[i] == '(':
                start_stat = self.stats_count
                substring = get_substring(rv, i + 1)
                self.solve_bracket(substring)

                # states["S" + str(next_state)].update({"ε": "S" + str(prev)})
                # update the states indices
                # next_state = end
                # start_state = next_state
                # prev_state = prev
                # continue looping over the regex after that bracket
                i = i + len(substring) + 2
                end_start = self.stats_count

            elif rv[i] == '|' or rv[i] == '+':
                # OrSolver here takes i+1 as an argument for the index parameter
                # Where the '+' '|' represents the current index (i).
                # 'i' represents the index that we will continue working from
                # it takes the regex starting from the element after the '+' operation
                # and operates on i

                i = self.solve_or(i + 1, rv[i + 1:])
                self.plus("1", "0")

                # i, prev, start, end = self.OrSolver(
                #     i + 1, rv[i + 1:], states, next_state)
                # create new 2 states to connect the oring branches
                # states.update({"S" + str(end + 1): {"terminalState": False,
                #                                     "     ε     ": "S" + str(prev_start),
                #                                     "      ε       ": "S" + str(prev)}})
                # states.update({"S" + str(end + 2): {"terminalState": False}})
                # states["S" + str(end)].update({"ε": "S" + str(end + 2)})
                # states["S" + str(next_state)].update({"ε": "S" + str(end + 2)})
                # update the state indices
                # prev_state = end + 1
                # next_state = end + 2
                # start_state = next_state
                # prev_start = end + 1

            elif rv[i] == '*':
                self.iter(rv[i + 1])
                # next_state, start_state, prev_state, prev_start = self.CreateState(
                #    rv, i, next_state, start_state, prev_state, prev_start, states)
                i += 1
            else:
                i += 1

    def solve_bracket(self, substring):
        self.fr_rv(substring)

    def solve_or(self, index, regex):
        self.fr_rv(regex)
        return index + len(regex)


def get_substring(regex, index):
    startingBrackets = 1
    closingBrackets = 0
    substring = ""
    regex = regex[index:]

    for j in range(len(regex)):
        if regex[j] == "(":
            startingBrackets += 1
        elif regex[j] == ")":
            closingBrackets += 1
        if startingBrackets == closingBrackets:
            break
        substring += regex[j]
    return substring


def pars_str(x):
    res = []
    for i in range(len(x) - 1):
        res.insert(len(res), x[i])
        if ord(x[i]) and ord(x[i + 1]):
            res.insert(len(res), '.')
        elif x[i] == ')' and x[i + 1] == '(':
            res.insert(len(res), '.')
        elif ord(x[i + 1]) and x[i] == ')':
            res.insert(len(res), '.')
        elif x[i + 1] == '(' and ord(x[i]):
            res.insert(len(res), '.')
        elif x[i] == '*' and (ord(x[i + 1] or x[i + 1] == '(')):
            res.insert(len(res), '.')
    check = x[len(x) - 1]
    if check != res[len(res) - 1]:
        res += check
    return ''.join(res)


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

    def to_regex_(self):
        keys_cpy = copy.deepcopy(list(self.stats.keys()))
        for stat in keys_cpy:
            if stat != self.start and stat not in self.finite_states:
                del_stat = stat
                stat_from = set()
                stat_to = set()
                for _ in self.alphabet:
                    if self.stats[del_stat][_] == del_stat:
                        stat_from.add((self.stats[del_stat][_], _, "="))
                    elif list(self.stats.keys()).index(del_stat) < \
                            list(self.stats.keys()).index(self.stats[del_stat][_]):
                        stat_from.add((self.stats[del_stat][_], _, "->"))
                    else:
                        stat_from.add((self.stats[del_stat][_], _, "<-"))
                for stat2 in self.stats.keys():
                    keys_ = list(list(self.stats.values())[list(self.stats.keys()).index(stat2)].keys())
                    for _ in keys_:
                        if self.stats[stat2][_] == del_stat:
                            stat_to.add((stat2, _))
                # R + PS*Q
                # for _ in list(stat_from):
                #     if _[2] == "<-":
                #         tmp = list(list(self.stats.values())[list(self.stats.keys()).index(_[0])].values())
                #         in_ = ""
                #         if _[0] is self.start:
                #             if _[0] in tmp:
                #                 in_ = list(self.stats[_[0]].keys())[tmp.index(_[0])] + "+"
                #         to_ = ""
                #         for __ in list(stat_to):
                #             if __[0] != _[0]:
                #                 to_ += __[1]
                #         self.stats[_[0]] |= {in_ + _[1] + to_: _[0]}
                #         self.stats[_[0]].pop(list(self.stats[_[0]].keys())[tmp.index(_[0])])
                #     if _[2] == "->":
                #         tmp = list(list(self.stats.values())[list(self.stats.keys()).index(_[0])].values())
                #         to_ = ""
                #         st_to = []
                #         for __ in list(stat_to):
                #             if __[0] != _[0] and list(self.stats.keys()).index(__[0]) < \
                #                     list(self.stats.keys()).index(_[0]):
                #                 st_to.append(__[0])
                #                 to_ += __[1]
                #         self.stats[_[0]] |= {_[1] + to_: st_to[0]}
                #         try:
                #             self.stats[_[0]].pop(list(self.stats[_[0]].keys())[tmp.index(st_to[0])])
                #         except ValueError:
                #             continue

                for _ in sorted(list(stat_to), key=lambda x: x[0]):
                    tmp = list(list(self.stats.values())[list(self.stats.keys()).index(_[0])].values())
                    in_ = ""
                    if _[0] is self.start and _[0] in ''.join([''.join(__) for __ in list(stat_from)]):
                        if _[0] in tmp:
                            in_ = list(self.stats[_[0]].keys())[tmp.index(_[0])] + "+"
                    to_ = ""
                    st_del_stat = ""
                    for __ in sorted(list(stat_to), key=lambda x: x[0]):
                        if __ != _:
                            try:
                                if list(self.stats[_[0]].keys())[tmp.index(__[0])] != "":
                                    continue
                            except ValueError:
                                if __ != _:
                                    to_ += list(self.stats[_[0]].keys())[tmp.index(del_stat)]
                                try:
                                    st_del_stat = list(self.stats[del_stat].keys())[tmp.index(_[0])]
                                except ValueError:
                                    st_del_stat = ""
                    if in_ or st_del_stat or to_:
                        self.stats[_[0]] |= {in_ + st_del_stat + to_: _[0]}
                        self.stats[_[0]].pop(list(self.stats[_[0]].keys())[tmp.index(_[0])])
                    for __ in sorted(list(stat_from), key=lambda x: x[0]):
                        if __[2] == "->":
                            to_ = ""
                            to_ += list(self.stats[_[0]].keys())[tmp.index(del_stat)]
                            st_del_stat = ""
                            st_del_stat += __[1]
                            self.stats[_[0]] |= {st_del_stat + to_: __[0]}
                            try:
                                self.stats[_[0]].pop(list(self.stats[_[0]].keys())[tmp.index(__[0])])
                            except ValueError:
                                continue
                        if __[2] == "<-":
                            st_del_stat = ""
                            st_del_stat += __[1]
                            for st in stat_to:
                                if st[0] != _[0]:
                                    if list(self.stats[st[0]].keys())[tmp.index(del_stat)] != "":
                                        try:
                                            st_del_stat += "+" + list(self.stats[st[0]].keys())[tmp.index(del_stat)] + \
                                                           list(self.stats[del_stat].keys())[tmp.index(_[0])]
                                        except ValueError:
                                            continue
                                        try:
                                            self.stats[st[0]].pop(list(self.stats[st[0]].keys())[tmp.index(_[0])])
                                        except ValueError:
                                            pass
                                        self.stats[st[0]] |= {st_del_stat: __[0]}
                self.stats.pop(del_stat)
                for _ in self.stats.keys():
                    try:
                        tmp = list(list(self.stats.values())[list(self.stats.keys()).index(_)].values())
                        self.stats[_].pop(list(self.stats[_[0]].keys())[tmp.index(del_stat)])
                    except ValueError:
                        continue
        P, Q, S, T = "", "", "", ""
        return "(" + str(P) + "+" + str(Q) + str(S) + "*" + str(T) + ")*" + str(Q) + str(S) + "*"

    def to_regex(self):
        R = [["∅" for i in range(self.stats_count)] for i in range(self.stats_count)]
        states = list(self.stats.keys())
        for i in self.stats.keys():
            R[states.index(i)][states.index(i)] = "e"
            for j in self.alphabet:
                if R[states.index(i)][states.index(self.stats[i][j])] != "∅":
                    R[states.index(i)][states.index(self.stats[i][j])] += ("+" + j)
                elif states.index(i) == states.index(self.stats[i][j]):
                    R[states.index(i)][states.index(self.stats[i][j])] = j + "+e"
                else:
                    R[states.index(i)][states.index(self.stats[i][j])] = j
                if len(R[states.index(i)][states.index(self.stats[i][j])]) > 1:
                    if "(" in R[states.index(i)][states.index(self.stats[i][j])]:
                        R[states.index(i)][states.index(self.stats[i][j])] = \
                            R[states.index(i)][states.index(self.stats[i][j])].replace(")", "").replace("(", "")
                    R[states.index(i)][states.index(self.stats[i][j])] = \
                        "(" + R[states.index(i)][states.index(self.stats[i][j])] + ")"

        def to_regex_(k):
            # R[i][j] = R[i][j] + "+" + R[i][k+1] + "(" + R[k+1][k+1] + ")*" + R[k+1][j]
            while k != self.stats_count - 1:
                R_cpy = copy.deepcopy(R)
                for i in self.stats.keys():
                    for j in self.stats.keys():
                        j = states.index(j)
                        if "(" in R_cpy[k + 1][k + 1]:
                            R[states.index(i)][j] = R_cpy[states.index(i)][j] + "+" + R_cpy[states.index(i)][k + 1] + \
                                                    R_cpy[k + 1][k + 1] + "*" + R_cpy[k + 1][j]
                        else:
                            R[states.index(i)][j] = R_cpy[states.index(i)][j] + "+" + R_cpy[states.index(i)][k + 1] + \
                                                    "(" + R_cpy[k + 1][k + 1] + ")*" + R_cpy[k + 1][j]
                        # substr = ""
                        # for _ in reversed(range(0, len(R[states.index(i)][j].split("*")[0]))):
                        #    substr = R[states.index(i)][j].split("*")[0][_] + substr
                        #    if R[states.index(i)][j].split("*")[0][_] == "(":
                        #        break
                        if "∅(" in R[states.index(i)][j]:
                            R[states.index(i)][j] = R[states.index(i)][j][:R[states.index(i)][j].find("∅(")]
                            R[states.index(i)][j] += "∅"
                        if "*∅" in R[states.index(i)][j]:
                            for indx in reversed(range(0, len(R[states.index(i)][j]))):
                                if R[states.index(i)][j][indx] == "+" and \
                                        R[states.index(i)][j][indx + 1] == "(":
                                    R[states.index(i)][j] = R[states.index(i)][j][:indx]
                        if "+∅+" in R[states.index(i)][j]:
                            R[states.index(i)][j] = R[states.index(i)][j].replace("+∅+", "")
                        if "∅+" in R[states.index(i)][j]:
                            R[states.index(i)][j] = R[states.index(i)][j].replace("∅+", "")
                        if "+∅" in R[states.index(i)][j]:
                            R[states.index(i)][j] = R[states.index(i)][j].replace("+∅", "")
                        print()

                k += 1

        to_regex_(-1)
        print(R)


if __name__ == '__main__':
    n = NKA("lab1/file5.txt")
    n.info()

    d = DKA("lab1/dka_1.txt")
    d.info()

    f = open("lab1/rv1.txt", "r")
    # n.fr_rv(f.readline().replace(" ", ""))

    print(d.to_regex_())
