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


def print_in_file(ka, filename="lab1/output.txt"):
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