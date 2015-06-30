""" 
    ===============================================
    createJTLVinput.py - LTL Pre-Processor Routines
    ===============================================
    
    Module that creates the input files for the JTLV based synthesis algorithm.
    Its functions create the skeleton .smv file and the .ltl file which
    includes the topological relations and the given spec.
"""
import math
import parseEnglishToLTL
import textwrap
from LTLParser.LTLFormula import LTLFormula, LTLFormulaType, treeToString
import logging

onDebugMode = False

def createSMVfile(fileName, sensorList, robotPropList):
    ''' This function writes the skeleton SMV file.
    It takes as input a filename, the number of regions, the list of the
    sensor propositions and the list of robot propositions (without the regions).
    '''

    fileName = fileName + '.smv'
    smvFile = open(fileName, 'w')

    # Write the header
    smvFile.write(textwrap.dedent("""
    -- Skeleton SMV file
    -- (Generated by the LTLMoP toolkit)


    MODULE main
        VAR
            e : env();
            s : sys();
    """));

    # Define sensor propositions
    smvFile.write(textwrap.dedent("""
    MODULE env -- inputs
        VAR
    """));
    for sensor in sensorList:
        smvFile.write('\t\t')
        smvFile.write(sensor)
        smvFile.write(' : boolean;\n')

    smvFile.write(textwrap.dedent("""
    MODULE sys -- outputs
        VAR
    """));

    # Define robot propositions
    for robotProp in robotPropList:
        smvFile.write('\t\t')
        smvFile.write(robotProp)
        smvFile.write(' : boolean;\n')

    # close the file
    smvFile.close()

# -------------- fastslow ---------------- #
#  IA stands for instantaneous actions --- #

def createIASysPropImpliesEnvPropLivenessFragment(sysProp, regions, envProp, adjData, use_bits=True, other_robot_name = ''):
    """
    Obtain for region: "[]<>((regionProp & regionProp_rc(envProp)) | (regionProp & !next(regionProp)))"
    Obtain for actions:"[]<>((actionProp & next(actionProp_ac(envProp))) |
                            (!actionProp & !next(actionProp_ac(envProp))) |
                            (actionProp & !next(actionProp)) |
                            (!actionProp & next(actionProp)) )"
    """
    if use_bits:
        numBits = int(math.ceil(math.log(len(adjData),2)))
        # TODO: only calc bitencoding once
        bitEncode = parseEnglishToLTL.bitEncoding(len(adjData), numBits)
        currBitEnc = bitEncode['current']
        nextBitEnc = bitEncode['next']
        envBitEnc = bitEncode['env']
        envNextBitEnc = bitEncode['envNext']

    # The topological relation (adjacency)
    adjFormulas = []

    adjFormula = '\t\t\t []<>( '
    adjSubFormulaArray = []
    for Origin in range(len(regions)):
        # skip boundary and obstacles
        if (regions[Origin].name == 'boundary' or regions[Origin].isObstacle):
            continue

        curProp = (currBitEnc[Origin] if use_bits else "s." +regions[Origin].name)
        nextProp = (nextBitEnc[Origin] if use_bits else "next(s."+regions[Origin].name+")")
        # TODO: maybe pass in env region list and use it here instead
        nextEnvProp = (envNextBitEnc[Origin] if use_bits else "next(e."+ regions[Origin].name+"_rc)")
        adjSubFormulaArray.append('('+curProp+' & '+nextEnvProp+') | ('+curProp+' & !'+nextProp+')\n')

    # closing the formula
    adjFormula = adjFormula + "\t\t\t\t| ".join(adjSubFormulaArray)
    adjFormula = adjFormula + ' ) '

    adjFormulas.append(adjFormula)

    if len(sysProp):
        adjFormula = '\t\t\t []<>( '
        adjSubFormulaArray = []
        for idx in range(len(sysProp)):
            # from action to action completion
            if sysProp[idx]+"_ac" in envProp:

                curActProp = 's.' + sysProp[idx]
                nextActProp = 'next(s.' + sysProp[idx] + ')'
                nextEnvActProp = 'next(e.' + sysProp[idx] + '_ac)'
                # from region i we can stay in region i
                adjSubFormulaArray.append('('+curActProp+' & '+nextEnvActProp+') | (!'+curActProp+' & !'+nextEnvActProp+') | ('+curActProp+' & !'+nextActProp+') | (!'+curActProp+' & '+nextActProp+')\n')

        # closing the formula
        adjFormula = adjFormula + "\t\t\t\t| ".join(adjSubFormulaArray)
        adjFormula = adjFormula + ' ) '

        adjFormulas.append(adjFormula)

    if onDebugMode:
        logging.debug(" & \n".join(adjFormulas))

    return " & \n".join(adjFormulas)

def createIASysTopologyFragment(adjData, regions, use_bits=True):
    """
    Obtain []( next(regionProp1_rc) -> (next(regionProp1) | next(regionProp2))
    """
    if use_bits:
        numBits = int(math.ceil(math.log(len(adjData),2)))
        # TODO: only calc bitencoding once
        bitEncode = parseEnglishToLTL.bitEncoding(len(adjData), numBits)
        currBitEnc = bitEncode['current']
        nextBitEnc = bitEncode['next']
        envBitEnc = bitEncode['env']
        envNextBitEnc = bitEncode['envNext']


    # The topological relation (adjacency)
    adjFormulas = []

    for Origin in range(len(adjData)):
        # from region i we can stay in region i
        adjFormula = '\t\t\t []( ('
        adjFormula = adjFormula + (envNextBitEnc[Origin] if use_bits else "next(e."+regions[Origin].name + "_rc)")
        adjFormula = adjFormula + ') -> ( ('
        adjFormula = adjFormula + (nextBitEnc[Origin] if use_bits else "next(s."+regions[Origin].name+")")

        adjFormula = adjFormula + ')'

        for dest in range(len(adjData)):
            if adjData[Origin][dest]:
                # not empty, hence there is a transition
                adjFormula = adjFormula + ' | ('
                adjFormula = adjFormula + (nextBitEnc[dest] if use_bits else "next(s."+regions[dest].name+")")
                adjFormula = adjFormula + ') '

        # closing this region
        adjFormula = adjFormula + ' ) ) '

        adjFormulas.append(adjFormula)

    if onDebugMode:
        logging.debug("[]( next(regionProp1_rc) -> (next(regionProp1) | next(regionProp2))")
        logging.debug(adjFormulas)

    """
    []regionProp1' -> ! (regionProp2' | regionProp3' | regionProp4')
    """
    for Origin in range(len(adjData)):
        # from region i we can stay in region i
        adjFormula = '\t\t\t []( ('
        adjFormula = adjFormula + (nextBitEnc[Origin] if use_bits else "next(s."+regions[Origin].name + ")")
        adjFormula = adjFormula + ') -> ! ( '
        regProps = []
        for Others in range(len(adjData)):
            if not regions[Origin].name == regions[Others].name:
                # not empty, hence there is a transition
                regProps.append(nextBitEnc[Others] if use_bits else "next(s."+regions[Others].name+")")

        adjFormula = adjFormula + " | ".join(regProps)
        # closing this region
        adjFormula = adjFormula + ' ) ) '

        adjFormulas.append(adjFormula)

    if onDebugMode:
        logging.debug("[]regionProp1' -> ! (regionProp2' | regionProp3' | regionProp4')")
        logging.debug(adjFormula)

    """
    [] regionProp1' | regionProp2' | regionProp3'
    """

    # In a BDD strategy, it's best to explicitly exclude these
    adjFormulas.append("[]"+createInitialRegionFragment(regions, use_bits))

    if onDebugMode:
        logging.debug("[] regionProp1' | regionProp2' | regionProp3'")
        logging.debug("[]"+createInitialRegionFragment(regions, use_bits))

    return " & \n".join(adjFormulas)

def createIAEnvTopologyFragment(adjData, regions, actuatorList, use_bits=True):
    """
    Obtain []( (regionProp1_rc & regionProp1) -> (next(regionProp1_rc)))
    """
    if use_bits:
        numBits = int(math.ceil(math.log(len(adjData),2)))
        # TODO: only calc bitencoding once
        bitEncode = parseEnglishToLTL.bitEncoding(len(adjData), numBits)
        currBitEnc = bitEncode['current']
        nextBitEnc = bitEncode['next']
        envBitEnc = bitEncode['env']
        envNextBitEnc = bitEncode['envNext']


    # The topological relation (adjacency)
    adjFormulas = []

    for Origin in range(len(adjData)):
        # from region i we can stay in region i
        adjFormula = '\t\t\t []( ('
        adjFormula = adjFormula + (envBitEnc[Origin] if use_bits else "e."+regions[Origin].name + "_rc")
        adjFormula = adjFormula + ' & '
        adjFormula = adjFormula + (currBitEnc[Origin] if use_bits else "s."+regions[Origin].name)

        adjFormula = adjFormula + ') -> ('

        adjFormula = adjFormula + (envNextBitEnc[Origin] if use_bits else "next(e."+regions[Origin].name+"_rc)")
        adjFormula = adjFormula + ") ) "

        adjFormulas.append(adjFormula)

    if onDebugMode:
        logging.debug("[]( (regionProp1_rc & regionProp1) -> (next(regionProp1_rc)))")
        logging.debug(adjFormulas)

    """
    Obtain []( (regionProp1_rc & regionProp2)) -> (next(regionProp1_rc)|next(regionProp2_rc))
    """
    for Origin in range(len(adjData)):
        for dest in range(len(adjData)):
            if adjData[Origin][dest]:
                # from region i we can head to dest stay in Origin
                adjFormula = '\t\t\t []( ('
                adjFormula = adjFormula + (envBitEnc[Origin] if use_bits else "e."+regions[Origin].name + "_rc")
                adjFormula = adjFormula + ' & '
                adjFormula = adjFormula + (currBitEnc[dest] if use_bits else "s."+regions[dest].name)
                adjFormula = adjFormula + ') -> ('
                # still in the current region
                adjFormula = adjFormula + (envNextBitEnc[Origin] if use_bits else "next(e."+regions[Origin].name + "_rc)")

                # not empty, hence there is a transition
                adjFormula = adjFormula + ' | '
                adjFormula = adjFormula + (envNextBitEnc[dest] if use_bits else "next(e."+regions[dest].name+"_rc)")
                adjFormula = adjFormula + ') )'
                adjFormulas.append(adjFormula)

    if onDebugMode:
        logging.debug("[]( (regionProp1_rc & regionProp2)) -> (next(regionProp1_rc)|next(regionProp2_rc))")
        logging.debug(adjFormula)

    """
    []regionProp1_rc' <-> ! (regionProp2_rc' | regionProp3_rc' | regionProp4_rc')
    """
    for Origin in range(len(adjData)):

        # from region i we can stay in region i
        adjFormula = '\t\t\t []( ('
        adjFormula = adjFormula + (envNextBitEnc[Origin] if use_bits else "next(e."+regions[Origin].name + "_rc)")
        adjFormula = adjFormula + ') <-> ! ( '
        regPropRCs = []
        for Others in range(len(adjData)):
            if not regions[Origin].name == regions[Others].name:
                # not empty, hence there is a transition
                regPropRCs.append(envNextBitEnc[Others] if use_bits else "next(e."+regions[Others].name+"_rc)")

        adjFormula = adjFormula + " | ".join(regPropRCs)
        adjFormula = adjFormula + ") ) "
        adjFormulas.append(adjFormula)

    if onDebugMode:
        logging.debug("[]regionProp1_rc' -> ! (regionProp2_rc' | regionProp3_rc' | regionProp4_rc')")
        logging.debug(adjFormula)

    """
    [](action_ac & action) -> action_ac'
    [](! action_ac & ! action) -> ! action_ac'
    """
    for prop in actuatorList:
        adjFormula = '\t\t\t []( (e.' + prop + '_ac & s.' + prop + ') -> next(e.' + prop + '_ac) )'
        adjFormulas.append(adjFormula)
        adjFormula = '\t\t\t []( (!(e.' + prop + '_ac) & !(s.' + prop + ')) -> !next(e.' + prop + '_ac) )'
        adjFormulas.append(adjFormula)

    """
    [] regionProp1' | regionProp2' | regionProp3'
    """

    # In a BDD strategy, it's best to explicitly exclude these
    adjFormulas.append("\t\t\t []"+createIAInitialEnvRegionFragment(regions, use_bits,True))

    if onDebugMode:
        logging.debug("[] regionProp1' | regionProp2' | regionProp3'")
        logging.debug("[]"+createIAInitialEnvRegionFragment(regions, use_bits,True))

    return " & \n".join(adjFormulas)

def createIAInitialEnvRegionFragment(regions, use_bits=True, nextProp=False):
    # Setting the system initial formula to allow only valid
    #  region (encoding). This may be redundant if an initial region is
    #  specified, but it is here to ensure the system cannot start from
    #  an invalid, or empty region (encoding).
    if use_bits:
        numBits = int(math.ceil(math.log(len(regions),2)))
        # TODO: only calc bitencoding once
        bitEncode = parseEnglishToLTL.bitEncoding(len(regions), numBits)
        envBitEnc = bitEncode['env']
        envNextBitEnc = bitEncode['envNext']

        if nextProp:
            initreg_formula = '( ' + envNextBitEnc[0] + ' \n'
            for regionInd in range(1,len(envNextBitEnc)):
                initreg_formula = initreg_formula + '\t\t\t\t | ' + envNextBitEnc[regionInd] + '\n'
            initreg_formula = initreg_formula + '\t\t\t) \n'
        else:
            initreg_formula = '( ' + envBitEnc[0] + ' \n'
            for regionInd in range(1,len(envBitEnc)):
                initreg_formula = initreg_formula + '\t\t\t\t | ' + envBitEnc[regionInd] + '\n'
            initreg_formula = initreg_formula + '\t\t\t) \n'
    else:
        if nextProp:
            initreg_formula = "\n\t({})".format(" | ".join(["({})".format(" & ".join(["next(e."+r2.name+"_rc)" if r is r2 else "!next(e."+r2.name+"_rc)" for r2 in regions])) for r in regions]))
        else:
            initreg_formula = "\n\t({})".format(" | ".join(["({})".format(" & ".join(["e."+r2.name+"_rc" if r is r2 else "!e."+r2.name+"_rc" for r2 in regions])) for r in regions]))

    return initreg_formula

#---------------------#

# ------ two_robot_negotiation ------------#  
def createEnvTopologyFragment(adjData, regions, use_bits=True, other_robot_name = ''):
    if not other_robot_name:
        logging.info('robot_name not provided!')
        return

    # The topological relation (adjacency)
    adjFormulas = []
    suffix = '_rc'

    """
    Obtain []( (robotName_regionProp1_rc & robotName_regionProp1) -> (next(robotName_regionProp1_rc))) 
    """
    for Origin in range(len(adjData)):
        # skip boundary and obstacles
        if (regions[Origin].name == 'boundary' or regions[Origin].isObstacle):
            continue

        # still in the current region
        adjFormula = '\t\t\t []( ('
        adjFormula = adjFormula + (envBitEnc[Origin] if use_bits else "e."+ other_robot_name + '_' +regions[Origin].name + suffix)
        adjFormula = adjFormula + ' & '
        adjFormula = adjFormula + (currBitEnc[Origin] if use_bits else "e."+ other_robot_name + '_' +regions[Origin].name)
        adjFormula = adjFormula + ') -> ('
        adjFormula = adjFormula + (envNextBitEnc[Origin] if use_bits else "next(e."+ other_robot_name + '_' +regions[Origin].name + suffix + ')')
        adjFormula = adjFormula + ') )'
        adjFormulas.append(adjFormula)

    """
    Obtain []( (robotName_regionProp1_rc & robotName_regionProp2)) -> (next(robotName_regionProp1_rc)|next(robotName_regionProp2_rc))

    """
    for Origin in range(len(adjData)):
        # skip boundary and obstacles
        if (regions[Origin].name == 'boundary' or regions[Origin].isObstacle):
            continue

        for dest in range(len(adjData)):
            if adjData[Origin][dest] and not (regions[dest].name == 'boundary' or regions[dest].isObstacle):
                # from region i we can head to dest stay in Origin
                adjFormula = '\t\t\t []( ('
                adjFormula = adjFormula + (envBitEnc[Origin] if use_bits else "e."+ other_robot_name + '_' +regions[Origin].name + suffix)
                adjFormula = adjFormula + ' & '
                adjFormula = adjFormula + (currBitEnc[dest] if use_bits else "e."+ other_robot_name + '_' +regions[dest].name)
                adjFormula = adjFormula + ') -> ('
                # still in the current region
                adjFormula = adjFormula + (envNextBitEnc[Origin] if use_bits else "next(e."+ other_robot_name + '_' +regions[Origin].name + suffix + ')')

                # not empty, hence there is a transition
                adjFormula = adjFormula + ' | '
                adjFormula = adjFormula + (envNextBitEnc[dest] if use_bits else "next(e."+ other_robot_name + '_' +regions[dest].name + suffix + ')')
                adjFormula = adjFormula + ') )'
                adjFormulas.append(adjFormula)

    """
    Obtain []( next(robotName_regionProp1_rc) -> (next(robotName_regionProp1)|next(robotName_regionProp2))
    """
    for Origin in range(len(adjData)):
        # skip boundary and obstacles
        if (regions[Origin].name == 'boundary' or regions[Origin].isObstacle):
            continue

        # from region i we can stay in region i
        adjFormula = '\t\t\t []( ('
        adjFormula = adjFormula + (currBitEnc[Origin] if use_bits else "next(e."+ other_robot_name + '_' +regions[Origin].name + suffix+ ")")
        adjFormula = adjFormula + ') -> ( ('
        adjFormula = adjFormula + (nextBitEnc[Origin] if use_bits else "next(e."+ other_robot_name + '_' +regions[Origin].name + ")")
        adjFormula = adjFormula + ')'

        for dest in range(len(adjData)):
            # skip boundary and obstacles
            if adjData[Origin][dest] and not (regions[dest].name == 'boundary' or regions[dest].isObstacle):
                # not empty, hence there is a transition
                adjFormula = adjFormula + '\n\t\t\t\t\t\t\t\t\t| ('
                adjFormula = adjFormula + (nextBitEnc[dest] if use_bits else "next(e."+other_robot_name + '_' + regions[dest].name + ")")

                adjFormula = adjFormula + ') '

        # closing this region
        adjFormula = adjFormula + ' ) ) '

        adjFormulas.append(adjFormula)

    """
    Obtain [](next(robotName_regionProp1)-> (robotName_regionProp1 | robotName_regionProp2 | robotName_regionProp3))
    """
    for Origin in range(len(adjData)):
        # skip boundary and obstacles
        if (regions[Origin].name == 'boundary' or regions[Origin].isObstacle):
            continue

        # from region i we can stay in region i
        adjFormula = '\t\t\t []( ('
        adjFormula = adjFormula + (currBitEnc[Origin] if use_bits else "next(e."+ other_robot_name + '_' +regions[Origin].name + ')')
        adjFormula = adjFormula + ') -> ( ('
        adjFormula = adjFormula + (nextBitEnc[Origin] if use_bits else "next(e."+ other_robot_name + '_' +regions[Origin].name + ")")
        adjFormula = adjFormula + ')'

        for dest in range(len(adjData)):
            # skip boundary and obstacles
            if adjData[Origin][dest] and not (regions[dest].name == 'boundary' or regions[dest].isObstacle):
                # not empty, hence there is a transition
                adjFormula = adjFormula + '\n\t\t\t\t\t\t\t\t\t| ('
                adjFormula = adjFormula + (nextBitEnc[dest] if use_bits else "next(e."+other_robot_name + '_' + regions[dest].name + ")")

                adjFormula = adjFormula + ') '

        # closing this region
        adjFormula = adjFormula + ' ) ) '
        adjFormulas.append(adjFormula)

    """
    Obtain [](next(robotName_regionProp1_rc) & ! next(robotName_regionProp2_rc))|()|()
    """
    # In a BDD strategy, it's best to explicitly exclude these
    adjFormulas.append("[]"+createInitialEnvRegionFragment(regions, use_bits, True, other_robot_name, suffix))

    """
    Obtain [](next(robotName_regionProp1) & ! next(robotName_regionProp2))|()|()
    """
    # In a BDD strategy, it's best to explicitly exclude these
    adjFormulas.append("[]"+createInitialEnvRegionFragment(regions, use_bits, True, other_robot_name))

    return " & \n".join(adjFormulas)

def createSysMutualExclusion(regionMapping, regions, use_bits=True, other_robot_name = ''):

    # skip any boundary or obstacles
    regions_old = regions
    regions = []
    for reg in regions_old:
        if reg.name == 'boundary' or reg.isObstacle:
            continue
        else:
            regions.append(reg)

    if use_bits:
        numBits = int(math.ceil(math.log(len(regions),2)))
        # TODO: only calc bitencoding once
        bitEncode = parseEnglishToLTL.bitEncoding(len(regions), numBits)
        currBitEnc = bitEncode['current']
        nextBitEnc = bitEncode['next']
        
    # The topological relation (adjacency)
    adjFormulas = []
    
    if not other_robot_name:
        logging.info('robot_name not provided!')
        return
        
    for Origin in range(len(regions)):
        
        # skip boundary and obstacles
        if (regions[Origin].name == 'boundary' or regions[Origin].isObstacle):
            continue
            
        # from region i we can stay in region i
        adjFormula = '\t\t\t []( ('
        adjFormula = adjFormula + "next(e."+ other_robot_name + '_' +regions[Origin].name + ")"
        adjFormula = adjFormula + ') -> ( !('
        first = True
        for subreg in regionMapping[str(regions[Origin].name)]:
            if first:
                first  = False
            else:
                adjFormula = adjFormula + '\n\t\t\t\t\t\t\t\t\t| ('
                
            adjFormula = adjFormula + (nextBitEnc[Origin] if use_bits else "next(s."+ subreg +")")
            adjFormula = adjFormula + ')'

        # closing this region
        adjFormula = adjFormula + ' ) ) '

        adjFormulas.append(adjFormula)

    return " & \n".join(adjFormulas)
    

def createInitialEnvRegionFragment(regions, use_bits=True, nextProp = True, other_robot_name = '', suffix = ''):
    # Setting the system initial formula to allow only valid
    #  region (encoding). This may be redundant if an initial region is
    #  specified, but it is here to ensure the system cannot start from
    #  an invalid, or empty region (encoding).
    
    # skip boundary and obstacles
    regions_old = regions
    regions = []
    for reg in regions_old:
        if reg.name == 'boundary' or reg.isObstacle:
            continue
        else:
            regions.append(reg)
    
    if use_bits:
        numBits = int(math.ceil(math.log(len(regions),2)))
        # TODO: only calc bitencoding once
        bitEncode = parseEnglishToLTL.bitEncoding(len(regions), numBits)
        currBitEnc = bitEncode['current']
        nextBitEnc = bitEncode['next']

        initreg_formula = '\t\t\t( ' + currBitEnc[0] + ' \n'
        for regionInd in range(1,len(currBitEnc)):
            initreg_formula = initreg_formula + '\t\t\t\t | ' + currBitEnc[regionInd] + '\n'
        initreg_formula = initreg_formula + '\t\t\t) \n'
    else:
        if nextProp:
            initreg_formula = "\n\t({})".format(" |\n ".join(["({})".format(" & ".join(["next(e."+other_robot_name + '_' +r2.name + suffix + ')' if r is r2 else "!next(e."+other_robot_name + '_' +r2.name + suffix +")" for r2 in regions])) for r in regions]))
        else:
            initreg_formula = "\n\t({})".format(" |\n ".join(["({})".format(" & ".join(["e."+other_robot_name + '_' +r2.name + suffix if r is r2 else "!e."+other_robot_name + '_' +r2.name + suffix for r2 in regions])) for r in regions]))
        
    return initreg_formula

def createIASysMutualExclusion(regionMapping, regions, use_bits=True, other_robot_name = ''):
    """
    []( (next(e.other_robot_name_reg)) -> ( !(next(e.reg_rc))))
    """
    # skip any boundary or obstacles
    regions_old = regions
    regions = []
    for reg in regions_old:
        if reg.name == 'boundary' or reg.isObstacle:
            continue
        else:
            regions.append(reg)

    if use_bits:
        numBits = int(math.ceil(math.log(len(regions),2)))
        # TODO: only calc bitencoding once
        bitEncode = parseEnglishToLTL.bitEncoding(len(regions), numBits)
        currBitEnc = bitEncode['current']
        nextBitEnc = bitEncode['next']
        envBitEnc = bitEncode['env']
        envNextBitEnc = bitEncode['envNext']
        
    # The topological relation (adjacency)
    adjFormulas = []
    
    if not other_robot_name:
        logging.info('robot_name not provided!')
        return

    # retrieve only the region names
    regionNames = [x.name for x in regions]

    for reg, subregList in regionMapping.iteritems():
        reg = reg.encode('ascii','ignore')

        # skip boundary and obstacles
        skipRegion = False
        for subReg in subregList:
            if regions[regionNames.index(subReg)].isObstacle:
                skipRegion = True
                continue

        if reg == 'boundary' or reg == 'others' or skipRegion:
            continue

        # from region i we can stay in region i
        adjFormula = '\t\t\t []( ('
        adjFormula = adjFormula + "next(e."+ other_robot_name + '_' + reg + "_rc)"
        adjFormula = adjFormula + ') -> ( !('
        first = True
        for subReg in subregList:
            subRegIdx = regionNames.index(subReg)
            if first:
                first  = False
            else:
                adjFormula = adjFormula + '\n\t\t\t\t\t\t\t\t\t| ('
                
            adjFormula = adjFormula + (envNextBitEnc[subRegIdx] if use_bits else "next(e."+ subReg+ "_rc)")
            adjFormula = adjFormula + ')'

        # closing this region
        adjFormula = adjFormula + ' ) )'
        adjFormulas.append(adjFormula)

    return " & \n".join(adjFormulas)

# ----------------------------------------------------#

def createTopologyFragment(adjData, regions, use_bits=True):
    if use_bits:
        numBits = int(math.ceil(math.log(len(adjData),2)))
        # TODO: only calc bitencoding once
        bitEncode = parseEnglishToLTL.bitEncoding(len(adjData), numBits)
        currBitEnc = bitEncode['current']
        nextBitEnc = bitEncode['next']

    # The topological relation (adjacency)
    adjFormulas = []

    for Origin in range(len(adjData)):
        # from region i we can stay in region i
        adjFormula = '\t\t\t []( ('
        adjFormula = adjFormula + (currBitEnc[Origin] if use_bits else "s."+regions[Origin].name)
        adjFormula = adjFormula + ') -> ( ('
        adjFormula = adjFormula + (nextBitEnc[Origin] if use_bits else "next(s."+regions[Origin].name+")")
        adjFormula = adjFormula + ')'
        
        for dest in range(len(adjData)):
            if adjData[Origin][dest]:
                # not empty, hence there is a transition
                adjFormula = adjFormula + '\n\t\t\t\t\t\t\t\t\t| ('
                adjFormula = adjFormula + (nextBitEnc[dest] if use_bits else "next(s."+regions[dest].name+")")
                adjFormula = adjFormula + ') '

        # closing this region
        adjFormula = adjFormula + ' ) ) '

        adjFormulas.append(adjFormula)

    # In a BDD strategy, it's best to explicitly exclude these
    adjFormulas.append("[]"+createInitialRegionFragment(regions, use_bits))

    return " & \n".join(adjFormulas)

def createInitialRegionFragment(regions, use_bits=True):
    # Setting the system initial formula to allow only valid
    #  region (encoding). This may be redundant if an initial region is
    #  specified, but it is here to ensure the system cannot start from
    #  an invalid, or empty region (encoding).
    if use_bits:
        numBits = int(math.ceil(math.log(len(regions),2)))
        # TODO: only calc bitencoding once
        bitEncode = parseEnglishToLTL.bitEncoding(len(regions), numBits)
        currBitEnc = bitEncode['current']
        nextBitEnc = bitEncode['next']

        initreg_formula = '\t\t\t( ' + currBitEnc[0] + ' \n'
        for regionInd in range(1,len(currBitEnc)):
            initreg_formula = initreg_formula + '\t\t\t\t | ' + currBitEnc[regionInd] + '\n'
        initreg_formula = initreg_formula + '\t\t\t) \n'
    else:
        initreg_formula = "\n\t({})".format(" | ".join(["({})".format(" & ".join(["s."+r2.name if r is r2 else "!s."+r2.name for r2 in regions])) for r in regions]))
        
    return initreg_formula

def createNecessaryFillerSpec(spec_part):
    """ Both assumptions guarantees need to have at least one each of
        initial, safety, and liveness.  If any are not present,
        create trivial TRUE ones. """

    if spec_part.strip() == "":
        filler_spec = ["TRUE", "[](TRUE)", "[]<>(TRUE)"]
    else:
        formula = LTLFormula.fromString(spec_part)
        filler_spec = []
        ############## ENV ASSUMPTIOn MINING #######################
        """
        if not formula.getConjunctsByType(LTLFormulaType.INITIAL):
            filler_spec.append("TRUE")
        """
        ############################################################
        if not formula.getConjunctsByType(LTLFormulaType.SAFETY):
            filler_spec.append("[](TRUE)")
        if not formula.getConjunctsByType(LTLFormulaType.LIVENESS):
            filler_spec.append("[]<>(TRUE)")

    return " & ".join(filler_spec) 

def flattenLTLFormulas(f):
    if isinstance(f, LTLFormula):
        return str(f)

    # If we've received a list of LTLFormula, assume that they should be conjoined
    if isinstance(f, list) and all((isinstance(sf, LTLFormula) for sf in f)):
        return " & \n".join([treeToString(sf.tree, top_level=False) for sf in f])

    if isinstance(f, basestring):
        return f

    raise ValueError("Invalid formula type: must be either string, LTLFormula, or LTLFormula list")

def createLTLfile(fileName, spec_env, spec_sys):
    ''' This function writes the LTL file. It encodes the specification and 
    topological relation. 
    It takes as input a filename, the list of the
    sensor propositions, the list of robot propositions (without the regions),
    the adjacency data (transition data structure) and
    a specification
    '''

    spec_env = flattenLTLFormulas(spec_env)
    spec_sys = flattenLTLFormulas(spec_sys)

    # Force .ltl suffix
    if not fileName.endswith('.ltl'):
        fileName = fileName + '.ltl'

    ltlFile = open(fileName, 'w')

    # Write the header and begining of the formula
    ltlFile.write(textwrap.dedent("""
    -- LTL specification file
    -- (Generated by the LTLMoP toolkit)

    """))
    ltlFile.write('LTLSPEC -- Assumptions\n')
    ltlFile.write('\t(\n')

    filler = createNecessaryFillerSpec(spec_env) 
    if filler: 
        ltlFile.write('\t' + filler)

    # Write the environment assumptions
    # from the 'spec' input 
    if spec_env.strip() != "":
        if filler:
            ltlFile.write('& \n')
        ltlFile.write(spec_env)
    ltlFile.write('\n\t);\n\n')

    ltlFile.write('LTLSPEC -- Guarantees\n')
    ltlFile.write('\t(\n')

    filler = createNecessaryFillerSpec(spec_sys) 
    if filler: 
        ltlFile.write('\t' + filler)

    # Write the desired robot behavior
    if spec_sys.strip() != "":
        if filler:
            ltlFile.write('& \n')
        ltlFile.write(spec_sys)

    # Close the LTL formula
    ltlFile.write('\n\t);\n')

    # close the file
    ltlFile.close()


