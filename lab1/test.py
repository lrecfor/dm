def OrSolver(index, regex, states, o_nextState):
    # Create states for the oring operation by incrementing one to the next_state
    # Which was passed as an argument from the previous operation.
    # Here we work with the Oring as a separate operation apart from
    # The previous states
    o_startState = o_nextState + 1
    o_prevStart = o_nextState + 1
    o_prevState = o_nextState + 1
    o_nextState = o_nextState + 1
    # create new state to indicate we are working with oring regex
    states.update({"S"+str(o_nextState): {"terminalState": False}})
    _, o_nextState, o_startState, o_prevState, o_prevStart, _ = regex2nfa(
        regex, states, o_nextState, o_startState, o_prevState, o_prevStart)

    return index+len(regex), o_prevStart, o_startState, o_nextState



def Bracketsolver(substring, next_state, states):
    b_currentState = next_state+1
    b_nextState = next_state+1
    b_prevState = next_state+1
    b_prevStart = next_state+1

    states.update({"S"+str(b_currentState): {"terminalState": False}})
    _, b_nextState, _, _, b_prevStart, _, = regex2nfa(
        substring, states, b_nextState, b_currentState, b_prevState, b_prevStart)
    return b_prevStart, b_nextState


def getSubString(regex, index):
    startingBrackets = 1
    closingBrackets = 0
    subString = ""
    regex = regex[index:]

    for j in range(len(regex)):
        if regex[j] == "(":
            startingBrackets += 1
        elif regex[j] == ")":
            closingBrackets += 1
        if(startingBrackets == closingBrackets):
            break
        subString += regex[j]
    print(subString)
    return subString


def transformAux(regex):
    next_state = 0  # next state
    start_state = 0  # current state
    prev_state = 0  # prev state index, state before reptition that allows looping over the repeated expression
    prev_start = 0  # New initial state
    flag = False
    states = {"S0": {"terminalState": False}}
    _, next_state, _, _, prev_start, i = regex2nfa(
        regex, states, next_state, start_state, prev_state, prev_start)
    print(states, end="\n\n")


def CreateState(regex, index, next_state, start_state, prev_state, prev_start, states):
        if regex[index] == "*":
            # create two state and connect between them using tompthon rule as decribed in the slides
            next_state += 1
            states["S" + str(start_state)].update({"   ε  ": "S" +
                                                             str(prev_state), "ε    ": "S" + str(next_state)})
            states["S" + str(prev_state)].update({"ε     ": "S" + str(next_state - 1)})
            states.update({"S" + str(next_state): {"terminalState": False}})
            start_state = next_state
        else:
            next_state += 1
            states["S" + str(start_state)
                   ].update({"Transition " + regex[index]: "S" + str(next_state)})
            states.update({"S" + str(next_state): {"terminalState": False}})
            prev_state = start_state
            start_state = next_state
        return next_state, start_state, prev_state, prev_start


def regex2nfa(regex, states, next_state, start_state, prev_state, prev_start):

    i = 0
    while i < len(regex):
        if regex[i] == "\\":
            #Taking the element after the backslash
            i += 1
            next_state, start_state, prev_state, prev_start,  = CreateState(
                regex, i, next_state, start_state, prev_state, prev_start, states)
            i += 1

        elif regex[i] == '(':
            # Get the substring of the starting regex
            subString = getSubString(regex, i+1)
            prev, end = Bracketsolver(
                subString, next_state, states)

            states["S"+str(next_state)].update({"ε": "S"+str(prev)})
            # update the states indices
            next_state = end
            start_state = next_state
            prev_state = prev
            # continue looping over the regex after that bracket
            i = i + len(subString) + 2

        elif regex[i] == '|' or regex[i] == '+':
            # OrSolver here takes i+1 as an argument for the index parameter
            # Where the '+' '|' represents the current index (i).
            # 'i' represents the index that we will continue working from
            # it takes the regex starting from the element after the '+' operation
            # and operates on i
            #
            i, prev, start, end = OrSolver(
                i+1, regex[i+1:], states, next_state)
            # create new 2 states to connect the oring branches
            states.update({"S"+str(end+1): {"terminalState": False,
                          "     ε     ": "S"+str(prev_start), "      ε       ": "S"+str(prev)}})
            states.update({"S"+str(end+2): {"terminalState": False}})
            states["S"+str(end)].update({"ε": "S"+str(end+2)})
            states["S"+str(next_state)].update({"ε": "S"+str(end+2)})
            # update the state indices
            prev_state = end + 1
            next_state = end + 2
            start_state = next_state
            prev_start = end + 1

        elif regex[i] == '*':
            next_state, start_state, prev_state, prev_start = CreateState(
                regex, i, next_state, start_state, prev_state, prev_start, states)
            i += 1
        else:
            next_state, start_state, prev_state, prev_start = CreateState(
                regex, i, next_state, start_state, prev_state, prev_start, states)
            i += 1
    return states, next_state, start_state, prev_state, prev_start, i


if __name__ == '__main__':
    transformAux("(0+1)*1(0+1)")
