import net.sf.javabdd.BDD;
import edu.wis.jtlv.env.Env;
import edu.wis.jtlv.env.module.ModuleBDDField;
import edu.wis.jtlv.env.module.SMVModule;
import edu.wis.jtlv.env.spec.Spec;
import java.io.File;
import java.io.PrintStream;
import java.io.BufferedReader;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.Map;
import java.util.TreeMap;
 
/**
 * Main class for GR(1) synthesis - reads the input instance and starts the game.
 * Game solving itself is done in another class.
 * @author Many people
 */
public class GROneMain {

    // Read the transition cost list from the cost file.
    private static TreeMap<Double,BDD> readCostInfo(String inFile) throws Exception {
      
      // Prepare reading the cost list
      TreeMap<Double,BDD> dataRead = new TreeMap<Double,BDD>();
      dataRead.put(0.0, Env.FALSE().id()); // We use below that this entry is guaranteed to exist.
      BufferedReader reader = new BufferedReader(new FileReader(inFile));
      ArrayList<BDD> careSetVariables = new ArrayList<BDD>();
        
      // Read the list of BDD variables that we care about
      String variableList = null;
      do {
        variableList = reader.readLine();
        if (variableList == null) {
          throw new Error("Error: Expecting list of BDD variables that we care about when determining the cost of a transition as the first line in the cost file.");
        } else {
          variableList = variableList.trim();
        }
      } while ((variableList.length()==0) || (variableList.substring(0,1).equals("#")));
          
      String[] variables = variableList.split("\\s");
      for (String a : variables) {
         ModuleBDDField field;
         field = Env.getVar("main.s", a);
         if (field==null) {
           field = Env.getVar("main.e", a);
           if (field==null) {
             System.err.println("Error while working through the variable list in the cost file. Did not find "+a);
             System.err.println("Global Unprimed Variables Availble: " + Env.globalUnprimeVars().toString());
             System.err.println("Global Primed Variable Variable: " + Env.globalPrimeVars().toString());
             throw new Error("Fatal Error.");
           }
         }
         careSetVariables.add(field.support().toBDD());
      }

      String costLine = reader.readLine();
      while (costLine!=null) {
        
        // Split into bits
        if ((costLine.length() > 0) && (!(variableList.substring(0,1).equals("#")))) { // Ignore empty lines
          String[] costLineParts = costLine.trim().split("\\s");
        
        
          if (costLineParts.length <= careSetVariables.size()) {
            System.err.println("Error in the cost file. The following line simply has the wrong number of elements that are seperated by spaces: ");
            System.err.println(costLine);
            System.err.println("Expected are one element of the form '0', '1', or '*' per variable and finally a cost value. Everythin else that is on a line is ignored.");
            throw new Error("Input file reading failed");
          }
          
          BDD currentBDD = Env.TRUE().id();
          for (int i=0;i<careSetVariables.size();i++) {
            if (costLineParts[i].equals("1")) {
              currentBDD = currentBDD.and(careSetVariables.get(i));
            } else if (costLineParts[i].equals("0")) {
              currentBDD = currentBDD.and(careSetVariables.get(i).not());
            } else if (costLineParts[i].equals("*")) {
              // Nothing to be done. Good!
            } else {
              System.err.println("Error in the following line of the cost file:");
              System.err.println(costLine);
              System.err.println("The element "+costLineParts[i]+" is neither of the form '1','0', or '*' for don't care.");
              throw new Error("Input file reading failed");
            }
          }

          double cost;
          try {
            cost = Double.parseDouble(costLineParts[careSetVariables.size()]);
          } catch (NumberFormatException e) {
            System.err.println("Error in the following line of the cost file:");
            System.err.println(costLine);
            System.err.println("The last element in the line is not a valid cost value (which should be a floating point number that is parseable by Java into a 'double').");
            throw new Error("Input file reading failed");
          }
          
          if (cost < 0.0) {
            System.err.println("Error in the following line of the cost file:");
            System.err.println(costLine);
            System.err.println("The cost must not be negative.");
            throw new Error("Input file reading failed");
          }
          
          if (dataRead.containsKey(cost)) {
            dataRead.put(cost, currentBDD.or(dataRead.get(cost)));
          } else {
            dataRead.put(cost, currentBDD.id());
          }
        } 
        
        costLine = reader.readLine();
      }
      
      if (dataRead.size()==0) {
        System.err.println("Warning: Didn't find a single cost line. Will assume a transition cost of 0 for all transitions.");
      }
      
      // Sanity check for the cost values. Check that there is no transition that has two different cost
      // values
      for (Map.Entry<Double, BDD> entry1 : dataRead.entrySet()) {
        for (Map.Entry<Double, BDD> entry2 : dataRead.entrySet()) {
          if (entry1.getKey()>entry2.getKey()) {
            if (!(entry1.getValue().and(entry2.getValue()).isZero())) {
              System.err.println("Error in the cost file: There is at least one transition that has cost "+entry1.getKey().toString()+" and "+entry2.getKey().toString()+" at the same time. Sorry, but this is not supported!");
              throw new Error("Cost file sanity check failed.");
            }
          }
        }
      }
          
      // All transitions without a given cost have cost 0
      BDD noCost = Env.TRUE().id();
      for (Map.Entry<Double, BDD> entry1 : dataRead.entrySet()) {
        noCost = noCost.and(entry1.getValue().not());
      }
      dataRead.put(0.0, dataRead.get(0.0).or(noCost));
        
      // Done.
      return dataRead;
    }



	public static void main(String[] args) throws Exception {
		// uncomment to use a C BDD package
		//System.setProperty("bdd", "buddy");

		GROneParser.just_initial = true;
		// GRParser.just_safety = true;

        // Check that we have enough arguments
        if (args.length < 2) {
            System.err.println("Usage: java GROneMain <smv_file> <ltl_file> [--fastslow] [--safety]");
            System.exit(1);
        }                

        // Load SMV and LTL files
        Env.loadModule(args[0]);
        Spec[] spcs = Env.loadSpecFile(args[1]);
        
        // Parse extra command-line switches
        boolean fs = false;
        boolean gen_safety = false;

        for (int i = 2; i < args.length; i++) {
            if (args[i].equals("--fastslow")) {
                fs = true;
            } else if (args[i].equals("--safety")) {
                gen_safety = true;
            } else {
                System.err.println("Unknown option: " + args[i]);
                System.err.println("Usage: java GROneMain <smv_file> <ltl_file> [--fastslow] [--safety]");
                System.exit(1);
            }
        }

        // Figure out the name of our output file by stripping the spec filename extension and adding .aut
        String out_filename = args[1].replaceAll("\\.[^\\.]+$",".aut");
        String cost_filename = args[1].replaceAll("\\.[^\\.]+$",".cost");

		// constructing the environment module.
		SMVModule env = (SMVModule) Env.getModule("main.e");
		Spec[] env_conjuncts = GROneParser.parseConjuncts(spcs[0]);
		GROneParser.addReactiveBehavior(env, env_conjuncts);
		// GRParser.addPureReactiveBehavior(env, env_conjuncts);

		// constructing the system module.
		SMVModule sys = (SMVModule) Env.getModule("main.s");
		Spec[] sys_conjuncts = GROneParser.parseConjuncts(spcs[1]);
		GROneParser.addReactiveBehavior(sys, sys_conjuncts);
		//GROneParser.addPureReactiveBehavior(sys, sys_conjuncts);

    // Read the cost information
    TreeMap<Double,BDD> costData = readCostInfo(cost_filename);

		// env.setFullPrintingMode(true);
		// System.out.println(env);
		// sys.setFullPrintingMode(true);
		// System.out.println(sys);

		// ***** playing the game

		System.out.print("==== Constructing and playing the game ======\n");
		long time = System.currentTimeMillis();		
	
		GROneGame g;
		BDD all_init, counter_exmple;
		
		//If the option is enabled, first try fastslow	
		if (fs) {
			g = new GROneGame(env,sys,costData,true);
			long t1 = (System.currentTimeMillis() - time);
			System.out.println("Games time: " + t1);
      System.out.flush();
			
			//Check that every initial system state is winning for every initial environment state
			 all_init = g.getSysPlayer().initial().and(g.getEnvPlayer().initial());
			 counter_exmple = g.envWinningStates().and(all_init);
			 if (counter_exmple.isZero()) {
				 
				 System.out.println("Specification is realizable with slow and fast actions...");
				 System.out.println("==== Building an implementation =========");
				 System.out.println("-----------------------------------------");
				 PrintStream orig_out = System.out;
				 System.setOut(new PrintStream(new File(out_filename))); // writing the output to a file
				 g.printWinningStrategy(all_init);
				 System.setOut(orig_out); // restore STDOUT
				 System.out.print("-----------------------------------------\n");
				 long t2 = (System.currentTimeMillis() - time);
				 System.out.println("Strategy time: " + t2);
				 System.out.println("===== Done ==============================");
				 System.exit(0);	
				 
			 }
			 else {
				 System.out.println("Specification is unsynthesizable for slow and fast actions...");
				 System.out.println("The env player can win from states:");
				 System.out.println("\t" + counter_exmple);
			 }
		}
		

		g = new GROneGame(env,sys,costData,false);
		long t3 = (System.currentTimeMillis() - time);
		System.out.println("Games time: " + t3);
    System.out.flush();

		// ** Export safety automaton for counterstrategy visualization

		if (gen_safety) {
			System.out.println("Exporting safety constraints automaton...");
			PrintStream orig_out = System.out;
			String safety_filename = args[1].replaceAll("\\.[^\\.]+$","_safety.aut");
			System.setOut(new PrintStream(new File(safety_filename))); // writing the output to a file
			g.generate_safety_aut(g.getEnvPlayer().initial().and(
					g.getSysPlayer().initial()));
			System.setOut(orig_out); // restore STDOUT
			//return;
		}

		// ** Analysis calls

		String debugFile = args[1].replaceAll("\\.[^\\.]+$",".debug");
		GROneDebug.analyze(env,sys);

		///////////////////////////////////////////////
		//Check that every initial system state is winning for every initial environment state
		all_init = g.getSysPlayer().initial().and(g.getEnvPlayer().initial());
		counter_exmple = g.envWinningStates().and(all_init);
		if (!counter_exmple.isZero()) {
			System.out.println("Specification is unsynthesizable even assuming instantaneous actions...");
			System.out.println("The env player can win from states:");
			System.out.println("\t" + counter_exmple);



			// If you only care about the existence of a winning initial system state for every initial environment state
			// (vs. every initial system state being winning for every initial environment state)
			/*	BDD env_ini = g.getEnvPlayer().initial();
					BDDVarSet env_vars = g.getEnvPlayer().moduleUnprimeVars();
					for (BDDIterator it = env_ini.iterator(env_vars); it.hasNext();) {
						BDD eini = (BDD) it.next();
						BDD sys_response = eini.and(g.getSysPlayer().initial()).and(
								g.sysWinningStates());
			            System.out.println("---------------");
			            sys_response.printSet();
						if (sys_response.isZero()) {
							System.out.println("Specification is unrealizable...");
							System.out.println("The env player can win from states:");
							System.out.println("\t" + eini);
							System.out.println("===== Done ==============================");
							return;
						}
				}*/


			System.out.println("==== Computing counterstrategy =========");
			System.out.println("-----------------------------------------");
			PrintStream orig_out = System.out;
			System.setOut(new PrintStream(new File(out_filename))); // writing the output to a file
			g.printLosingStrategy(counter_exmple);
			System.setOut(orig_out); // restore STDOUT
			System.out.print("-----------------------------------------\n");
			long t2 = (System.currentTimeMillis() - time);
			System.out.println("Strategy time: " + t2);
			System.out.println("===== Done ==============================");


			//Error code = 1 on exit
			System.exit(1);
		}


		System.out.println("Specification is realizable assuming instantaneous actions...");
		System.out.println("==== Building an implementation =========");
		System.out.println("-----------------------------------------");
		PrintStream orig_out = System.out;
		System.setOut(new PrintStream(new File(out_filename))); // writing the output to a file
		g.printWinningStrategy(all_init);
		System.setOut(orig_out); // restore STDOUT
		System.out.print("-----------------------------------------\n");
		long t2 = (System.currentTimeMillis() - time);
		System.out.println("Strategy time: " + t2);
		System.out.println("===== Done ==============================");
		System.exit(0);
	
	}
}
