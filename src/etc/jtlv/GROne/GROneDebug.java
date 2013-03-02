import net.sf.javabdd.BDD;
import net.sf.javabdd.BDDVarSet;
import net.sf.javabdd.BDD.BDDIterator;
import edu.wis.jtlv.env.Env;
import edu.wis.jtlv.env.module.SMVModule;
import edu.wis.jtlv.env.spec.Spec;
import java.io.File;
import java.io.PrintStream;
import java.io.OutputStream;
import java.io.FileWriter;
import java.io.BufferedWriter;
import edu.wis.jtlv.lib.FixPoint;
import edu.wis.jtlv.old_lib.games.GameException;
import edu.wis.jtlv.env.spec.SpecBDD;
import edu.wis.jtlv.lib.AlgRunnerThread;
import edu.wis.jtlv.lib.AlgResultI;
import edu.wis.jtlv.lib.mc.tl.LTLModelCheckAlg;

// Class containing methods for performing unsatisfiability and unrealizability checks on a specification 
// Spec consists of environment and system modules (env, sys)

public class GROneDebug {

	/**
	 * @param args
	 * @throws Exception
	 */
	public static void main(String[] args) throws Exception {
		// uncomment to use a C BDD package
		//System.setProperty("bdd", "buddy");

		GROneParser.just_initial = true;
		// GRParser.just_safety = true;

        // Check that we have enough arguments
        // This class takes the same arguments as GROneMain.
		if (args.length < 2) {
            System.err.println("Usage: java GROneDebug [smv_file] [ltl_file]");
            System.exit(1);
        }
		
        Env.loadModule(args[0]);
        Spec[] spcs = Env.loadSpecFile(args[1]);

        // Figure out the name of our output file by stripping the spec filename extension and adding .aut
        String out_filename = args[1].replaceAll("\\.[^\\.]+$",".aut");

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
		
		//Prints the results of analyzing the specification
		System.out.println(analyze(env, sys));		
	}
	
	public static String analyze(SMVModule env, SMVModule sys) {
		return "Unsupported.";
	}
	
	public static class NOPPrintStream extends PrintStream
	{
	    public NOPPrintStream() { super((OutputStream)null); }

	    public void println(String s) { /* Do nothing */ }
	    // You may or may not have to override other methods
	}
	
	public static String justiceChecks(SMVModule env, SMVModule sys, int explainSys, int explainEnv) throws GameException  {
    return "Unsupported";
  }
}