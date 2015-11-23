import lib.createMLibrary
import lib.libraryToLTL
import lib.createPropMapping

#LC = lib.createMLibrary.LibraryCreator()
#LC.CreateLibrary()
#LC.SaveLibrary()
#print "Done"

LTLC = lib.libraryToLTL.LTLCreator()
LTLC.FindEntries()
LTLC.CreateLTL("stay")
for ltl in LTLC.LTL_formula_list:
    print ltl
