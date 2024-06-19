import argparse
import copy

class Variable:
    letter = None
    domain = None
    valueAssigned = None

def main(varFile, conFile, consistencyEnforcingProcedure):
    # we are using a global counter
    global glCounter  
    # the global counter is initially set to zero (0)
    glCounter = 0  
    varInfoDict = {}
    with open(varFile, 'r') as vF:
        # read lines and remove trailing newline characters
        formattedRead = [line.rstrip('\n') for line in vF.readlines()]
        for i in formattedRead:
            varInfo = Variable()
            copyDomain = []
            doubleDigit = False
            tempNb = "None"
            for j in i:
                if j.isalpha():
                    varInfo.letter = j
                elif j.isdigit():
                    # assume the nb is more than one digit
                    doubleDigit = True  
                    if tempNb == "None":
                        tempNb = str(j)
                    else:
                        tempNb += str(j)
                elif j.isspace() and doubleDigit:
                    copyDomain.append(int(tempNb))
                    tempNb = "None"
                    doubleDigit = False
                    continue
            # if the last number in the domain is more than one digit, we didn't reach a space to append that value in the for loop
            if doubleDigit:  
                copyDomain.append(int(tempNb))
                tempNb = "None"
                doubleDigit = False
            varInfo.domain = copyDomain
            # the variable is not assigned a value yet
            varInfo.valueAssigned = None 
           # Now we can access all the information about a variable from knowing its
            varInfoDict[varInfo.letter] = varInfo  
             # print(varInfo.letter)
             # print(varInfo.domain)
             # print(varInfo.valueAssigned)
            

    constraintsList = []
    with open(conFile, 'r') as cF:
        # read lines and remove trailing newline characters
        formattedRead = [line.rstrip('\n') for line in cF.readlines()]
        for i in formattedRead:
            constraintsList.append((i[0], i[2], i[4]))
          
    # none
    if consistencyEnforcingProcedure == "none":  
        fc = False
    # forward checking
    elif consistencyEnforcingProcedure == "fc":  
        fc = True
    # if the CEP is invalid, throw an error
    else: 
        exit("Invalid consistencyEnforcingProcedure! Options are \"none\" or \"fc\"")

    # start the backtracking from an empty assignedDic dictionary, when recursively calling this function, the assignedDic dictionary will be populated
    # backtracking will be recursive because this way, when one of the recursively called functions fail for example, we can backtrack to the function
    # where we still had more variables to try out, and we will have our assignedDic dictionary and the varInfoDict that are specific for that branch still intact
    # fc is the flag that lets us know if we are doing forwardChecking or not.
    solution = backtracking({}, varInfoDict, constraintsList, fc)
    # printing the solution branch if one was found (not False)
    if solution is not False:  
        # current node index being expanded to compare with nbNodes
        currNode = 0  
        # number of nodes visited in the solution branch
        nbNodes = len(solution.keys())  
        # if solution exists, then it is a new branch to be printed, so increase the global counter
        glCounter += 1  
        print(str(glCounter) + ". ", end="")
        # iterate through solution nodes
        for key in solution.keys():  
            # NOT last node in solution list
            if currNode < nbNodes - 1:  
                currNode += 1
                print(str(key) + "=" + str(solution[key]) + ", ", end="")
            # last node in solution list. Different output format.
            else: 
                print(str(key) + "=" + str(solution[key]) + " solution", end="")

# reset number of branches/recursive calls
glCounter = 0  
def backtracking(assignedDic, varInfoDict, constraintsList, fc):
    global glCounter
    # assume all variables have been assigned a value
    allAssigned = True  
    # check each variable
    for var in varInfoDict.values(): 
        # if any variable has not been assigned a value yet
        if var.valueAssigned is None:  
            # set allAssigned flag to False
            allAssigned = False  
            break 
          
    if allAssigned:
        return assignedDic

    # find next variable to expand
    var = next_variable_selection(varInfoDict, constraintsList)  

    # returns the domain values as tuples sorted in increasing order of nb of constraints violated
    # (values with equal nb of constraints violations are in the same tuple, so we pick them starting with the smallest value)
    domTuples = constraints_based_domain_sort(varInfoDict, constraintsList, var)

    for valuesTuple in domTuples:
        # check if val is consistent with chosen variable constraints
        for value in valuesTuple:  
            isConsistent = True
            value = int(value)
            for constraintTuple in constraintsList:
                compareOP = constraintTuple[1]
                # check if 1st operand (VAR1) in "VAR1 OP VAR2" is the chosen variable
                if (constraintTuple[0] is var) and (varInfoDict[constraintTuple[2]].valueAssigned is not None):
                    if compareOP == '=':
                        isConsistent = (value == int(varInfoDict[constraintTuple[2]].valueAssigned))
                    elif compareOP == '!':
                        isConsistent = (value != int(varInfoDict[constraintTuple[2]].valueAssigned))
                    elif compareOP == '>':
                        isConsistent = (value > int(varInfoDict[constraintTuple[2]].valueAssigned))
                    elif compareOP == '<':
                        isConsistent = (value < int(varInfoDict[constraintTuple[2]].valueAssigned))
                # check if 2nd operand (VAR2) in "VAR1 OP VAR2" is the chosen variable
                elif (constraintTuple[2] is var) and (varInfoDict[constraintTuple[0]].valueAssigned is not None):
                    if compareOP == '=':
                        isConsistent = (int(varInfoDict[constraintTuple[0]].valueAssigned) == value)
                    if compareOP == '!':
                        isConsistent = (int(varInfoDict[constraintTuple[0]].valueAssigned) != value)
                    if compareOP == '>':
                        isConsistent = (int(varInfoDict[constraintTuple[0]].valueAssigned) > value)
                    if compareOP == '<':
                        isConsistent = (int(varInfoDict[constraintTuple[0]].valueAssigned) < value)

                # the chosen variable is not consistent with the constraints, it fails
                if isConsistent is False:
                    # current node index being expanded to compare with nbNodes
                    currNode = 0  
                    # number of nodes visited in the failure branch
                    nbNodes = len(assignedDic.keys()) 
                    # if failure exists, then it is a new branch to be printed, so increase the global counter
                    glCounter += 1  
                    print(str(glCounter) + ". ", end="")
                    # iterate through failure nodes
                    for key in assignedDic.keys():  
                        if currNode < nbNodes - 1:  # NOT last node in solution list
                            currNode += 1
                            print(str(key) + "=" + str(assignedDic[key]) + ", ", end="")
                        # last node in solution list; different output format
                        else: 
                            print(str(key) + "=" + str(assignedDic[key]) + ", ", end="")
                            # print the last node, since we didn't add it to the assigned dictionary so it is not accounted for in nbNodes
                            print(str(var) + "=" + str(value) + " failure")  
                  # to avoid way too long code execution. Value can be increased to give more max runtime
                  if glCounter > 50:  
                        exit("Running for too long error!")
                    # not consistent variable, no need to check further
                    break  

            # the chosen variable is consistent with the constraints, assign it
            if isConsistent is True:
                varInfoDict[var].valueAssigned = value
                assignedDic[var] = value
                # fc when prompted
                if fc is True: 
                    # fc domains based on given constraints
                    sendDic = copy.deepcopy(varInfoDict)
                    resultDict = forward_checking(sendDic, constraintsList, var)
                    # if any domain is empty, return false
                    for fcVariable in resultDict.values():  
                        if len(fcVariable.domain) == 0:
                            # current node index being expanded to compare with nbNodes
                            currNode = 0  
                            # number of nodes visited in the failure branch
                            nbNodes = len(assignedDic.keys())  
                            # if failure exists, then it is a new branch to be printed, so increase the global counter
                            glCounter += 1  
                            print(str(glCounter) + ". ", end="")
                            for key in assignedDic.keys():
                                # NOT last node in solution list
                                if currNode < nbNodes - 1:  
                                    currNode += 1
                                    print(str(key) + "=" + str(assignedDic[key]) + ", ", end="")
                                else:
                                    print(str(var) + "=" + str(value) + " failure")
                            # to avoid way too long code execution, value can be increased to give more max runtime
                            if glCounter > 50:  
                                exit("Running for too long error!")
                            continue
                else:
                    resultDict = varInfoDict

                returnVal = backtracking(assignedDic, resultDict, constraintsList, fc)
                if returnVal is False:
                    varInfoDict[var].valueAssigned = None
                    assignedDic.pop(var)
                else:
                    return returnVal

    return False


def forward_checking(varInfoDict, constraintsList, currVariable):
    # our varInfoDic is a copy of the original one, so we can change it without worrying
    assignedValue = varInfoDict[currVariable].valueAssigned
    # (FIX ME)
    tempVariable = None  
    # remove values that contradict the constraints
    for constraintTuple in constraintsList: 
        # currVariable OP VAR2
        if constraintTuple[0] == currVariable:
            if varInfoDict[constraintTuple[2]].valueAssigned is not None:
                # skip this current constraint if the other variable in the constraint is already assigned
                continue  
            # copy the domains into a temp list.of
            tempList = varInfoDict[constraintTuple[2]].domain[:]  
            for value in tempList:
                compareOP = constraintTuple[1]
                if compareOP == '=':
                    if not (assignedValue == value):
                      # constraint violation
                        varInfoDict[constraintTuple[2]].domain.remove(value) 
                elif compareOP == '!':
                    if not (assignedValue != value):
                      # constraint violation
                        varInfoDict[constraintTuple[2]].domain.remove(value)  
                elif compareOP == '>':
                    if not (assignedValue > value):
                      # constraint violation
                        varInfoDict[constraintTuple[2]].domain.remove(value) 
                elif compareOP == '<':
                    if not (assignedValue < value):
                      # constraint violation
                        varInfoDict[constraintTuple[2]].domain.remove(value)  
        # VAR1 OP currVariable
        elif constraintTuple[2] is currVariable:
            if varInfoDict[constraintTuple[0]].valueAssigned is not None:
                 # skip this current constraint if the other variable in the constraint is already assigned
                continue 
            # copy the domains into a temp list.of
            tempList = varInfoDict[constraintTuple[2]].domain[:]  
            for value in varInfoDict[constraintTuple[0]].domain:
                compareOP = constraintTuple[1]
                if compareOP == '=':
                    if not (value == assignedValue):
                      # constraint violation
                        varInfoDict[constraintTuple[0]].domain.remove(value)  
                elif compareOP == '!':
                    if not (value != assignedValue):
                      # constraint violation
                        varInfoDict[constraintTuple[0]].domain.remove(value)  
                elif compareOP == '>':
                    if not (value > assignedValue):
                      # constraint violation
                        varInfoDict[constraintTuple[0]].domain.remove(value) 
                elif compareOP == '<':
                    if not (value < assignedValue):
                        # constraint violation
                        varInfoDict[constraintTuple[0]].domain.remove(value)  

    return varInfoDict


def next_variable_selection(varDic, constraintsList):
    # our current best variable
    bestVariable = None  
    domainSizeBest = 0
    domainSizeKey = 0
    # safety measure from a logical error where we call select_variable function when all the variables have been assigned a value
    allAssignedError = True  
    # for variable ties
    multipleBestValueList = []  
    for key in varDic.keys():
        # only check the variable if it has not been assigned a value yet
        if varDic[key].valueAssigned is None:
            # update domain size of the current variable (key)
            domainSizeKey = len(varDic[key].domain)  
            allAssignedError = False  
            # if bestVariable is still unassigned a variable (1st unassigned variable encountered)
            if bestVariable is None:
                bestVariable = key
                domainSizeBest = len(varDic[bestVariable].domain)
                multipleBestValueList.append(key)
                continue

            # check for most constrained
            # current variable has smaller domain
            if domainSizeKey < domainSizeBest:  
                # found new best variable
                bestVariable = key  
                multipleBestValueList = [key]
                domainSizeBest = len(varDic[bestVariable].domain)
            # if equal domain, pick most constraining variable
            elif domainSizeBest == domainSizeKey:
                # variables to count the number of constraints on each variable
                nbConstraintsBest = 0
                nbConstraintsKey = 0
                
                # count the number of constraints on the current best variable
                for constraint in constraintsList:
                    # skip this current constraint if either of the variables in it is assigned a value
                    if varDic[constraint[0]].valueAssigned is not None or varDic[constraint[2]].valueAssigned is not None:
                        continue
                    # count the number of constraints on the curr best variable
                    if constraint[0] == bestVariable or constraint[2] == bestVariable:
                        nbConstraintsBest += 1
                    # count the number of constraints on the key variable
                    if constraint[0] == key or constraint[2] == key:
                        nbConstraintsKey += 1
                # pick the variable with the higher constraints
                if nbConstraintsKey > nbConstraintsBest:
                    bestVariable = key
                    multipleBestValueList = [key]
                    domainSizeBest = len(varDic[bestVariable].domain)
                # add to list if equal constraints
                elif nbConstraintsBest == nbConstraintsKey:  
                    if key < bestVariable:
                        bestVariable = key
                        multipleBestValueList = [key]
                        domainSizeBest = len(varDic[bestVariable].domain)

    if allAssignedError:
        exit("All Values are assigned, yet select_variable was still called!!")
    return bestVariable


def constraints_based_domain_sort(varInfoDict, constraintsList, selectedVar):
    # dictionary for the nb of constraints violated per value, it is used to do chose the least constraining value later on
    nbConstViolatedPerValueDic = {}
    for selectedVarValue in varInfoDict[selectedVar].domain:
        nbViolations = 0
        selectedVarValue = int(selectedVarValue)
        for constraintTuple in constraintsList:
            if constraintTuple[0] is selectedVar:
                if varInfoDict[constraintTuple[2]].valueAssigned is not None:
                    # skip this current constraint if the other variable in the constraint is already assigned
                    continue  
                for otherVarValue in varInfoDict[constraintTuple[2]].domain:
                    compareOP = constraintTuple[1]
                    if compareOP == '=':
                        if not (selectedVarValue == int(otherVarValue)):
                            # constraint violation
                            nbViolations += 1  
                    elif compareOP == '!':
                        if not (selectedVarValue != int(otherVarValue)):
                            # constraint violation
                            nbViolations += 1 
                    elif compareOP == '>':
                        if not (selectedVarValue > int(otherVarValue)):
                            # constraint violation
                            nbViolations += 1  
                    elif compareOP == '<':
                        if not (selectedVarValue < int(otherVarValue)):
                            # constraint violation
                            nbViolations += 1  
                    # placeholder for (FIX ME)
                    else:  
                        pass
            elif varInfoDict[constraintTuple[0]].valueAssigned is None and constraintTuple[2] == selectedVar:
                for otherVarValue in varInfoDict[constraintTuple[0]].domain:
                    compareOP = constraintTuple[1]
                    if compareOP == '=':
                        if not (int(otherVarValue) == selectedVarValue):
                            # constraint violation
                            nbViolations += 1  
                    elif compareOP == '!':
                        if not (int(otherVarValue) != selectedVarValue):
                            # constraint violation
                            nbViolations += 1  
                    elif compareOP == '>':
                        if not (int(otherVarValue) > selectedVarValue):
                            # constraint violation
                            nbViolations += 1  
                    elif compareOP == '<':
                        if not (int(otherVarValue) < selectedVarValue):
                            # constraint violation
                            nbViolations += 1  

        if nbViolations not in nbConstViolatedPerValueDic:
            nbConstViolatedPerValueDic[nbViolations] = [int(selectedVarValue)]
        else:
            nbConstViolatedPerValueDic[nbViolations].append(int(selectedVarValue))

    returnList = []
    # sort based on the number of constraints violated (ascending order)
    sortedKeys = sorted(nbConstViolatedPerValueDic.keys())  
    # starting with the least constraining set of values
    for key in sortedKeys:  
        # sort the values present in each set of values so that when we pick the first value of the set, we get the smallest value out of the equally constraining values
        appendList = sorted(nbConstViolatedPerValueDic[key])  
        returnList.append(appendList)

    return returnList


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Example script with command-line arguments")
    parser.add_argument("varFile", help="Path to the variable file")
    parser.add_argument("conFile", help="Path to the constraints file")
    parser.add_argument("consistencyEnforcingProcedure", help="The consistency enforcing procedure")

    args = parser.parse_args()
    main(args.varFile, args.conFile, args.consistencyEnforcingProcedure)
