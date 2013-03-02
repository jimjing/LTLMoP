
import java.util.Iterator;
import java.util.Stack;
import java.util.Vector;

import net.sf.javabdd.BDD;
import net.sf.javabdd.BDDVarSet;
import net.sf.javabdd.BDD.BDDIterator;
import edu.wis.jtlv.env.Env;
import edu.wis.jtlv.env.module.ModuleWithWeakFairness;
import edu.wis.jtlv.env.module.Module;
import edu.wis.jtlv.lib.FixPoint;
import edu.wis.jtlv.old_lib.games.GameException;
import edu.wis.jtlv.env.module.ModuleBDDField;
import java.util.ArrayList;
import java.util.TreeMap;

/** 
 * <p>
 * To execute, create an object with two Modules, one for the system and the
 * other for the environment, and then just extract the strategy/counterstrategy 
 * via the printWinningStrategy() and printLosingStrategy() methods.
 * </p>
 * 
 * @author Yaniv Sa'ar, Vasumathi Raman, Cameron Finucane, Ruediger Ehlers
 * 
 */
public class GROneGame {

  private ModuleWithWeakFairness env;
  private ModuleWithWeakFairness sys;
  int sysJustNum, envJustNum;
  private BDD player1_winning;
  private BDD player2_winning;
  BDD slowSame, fastSame, envSame;
  BDDVarSet sys_slow_prime;
  BDDVarSet sys_fast_prime;
  TreeMap<Double, BDD> costData;

  // p2_winning in GRGAmes are !p1_winning
  public GROneGame(ModuleWithWeakFairness env, ModuleWithWeakFairness sys, int sysJustNum, int envJustNum, TreeMap<Double, BDD> chosenCostData, boolean fastslow)
          throws GameException {
    if ((env == null) || (sys == null)) {
      throw new GameException(
              "cannot instanciate a GR[1] Game with an empty player.");
    }

    //Define system and environment modules, and how many liveness conditions are to be considered. 
    //The first sysJustNum system livenesses and the first envJustNum environment livenesses will be used
    this.env = env;
    this.sys = sys;
    this.sysJustNum = sysJustNum;
    this.envJustNum = envJustNum;
    this.costData = chosenCostData;

    //
    if (fastslow) {
      System.err.println("HUGE WARNING: Fastslow semantics are not supported with costs. Costs are simply IGNORED!");
      this.player2_winning = this.calculate_win_FS();	//(system winning states)
      this.player1_winning = this.player2_winning.not(); //(environment winning states)
    } else {
      this.player2_winning = this.calculate_win();	//(system winning states)
      this.player1_winning = this.player2_winning.not();   //(environment winning states
    }
    //this.player1_winning = this.player2_winning.not(); //commented out after counterstrategy addition - VR

  }

  static TreeMap<Double, BDD> getDefaultCostMap() {
    TreeMap<Double, BDD> defaultCostMap = new TreeMap<Double, BDD>();
    defaultCostMap.put(0.0, Env.FALSE().id()); // We use below that this entry is guaranteed to exist.
    return defaultCostMap;
  }

  public GROneGame(ModuleWithWeakFairness env, ModuleWithWeakFairness sys, boolean fastslow)
          throws GameException {
    this(env, sys, sys.justiceNum(), env.justiceNum(), getDefaultCostMap(), fastslow);
  }

  public GROneGame(ModuleWithWeakFairness env, ModuleWithWeakFairness sys, int sysJustNum, int envJustNum, boolean fastslow)
          throws GameException {
    this(env, sys, sysJustNum, envJustNum, getDefaultCostMap(), fastslow);
  }

  public GROneGame(ModuleWithWeakFairness env, ModuleWithWeakFairness sys, TreeMap<Double, BDD> costData, boolean fastslow)
          throws GameException {
    this(env, sys, sys.justiceNum(), env.justiceNum(), costData, fastslow);
  }
  
  public ArrayList<ArrayList<BDD> > strategy; // First index: goal, second index: precedence over transitions
  
  /**
   * <p>
   * Calculating Player-2 winning states.
   * </p>
   * 
   * @return The Player-2 winning states for this game.
   */
  private BDD calculate_win() {
    BDD z;
    FixPoint<BDD> iterZ, iterY, iterX;
    
    if (envJustNum==0) throw new RuntimeException("Can only deal with settings that have at least one environment assumption!");
    
    // First compute the winning positions
    z = Env.TRUE();
    for (iterZ = new FixPoint<BDD>(); iterZ.advance(z);) {
      for (int j = 0; j < sysJustNum; j++) {
        BDD y = sys.justiceAt(j).and(z);
        for (iterY = new FixPoint<BDD>(); iterY.advance(y);) {
          for (int i = 0; i < envJustNum; i++) {
            BDD negp = env.justiceAt(i).not();
            BDD x = z.id();
            for (iterX = new FixPoint<BDD>(); iterX.advance(x);) {
              x = env.yieldStates(sys, x.and(negp).or(y));
            }
            y = y.id().or(x);
          }
        }
        z = y.id();
      }
    }
    
    // Now compute a strategy
    strategy = new ArrayList< ArrayList< BDD>>(sysJustNum);
    for (int j = 0; j < sysJustNum; j++) {
      strategy.add(new ArrayList< BDD>());
      
      BDD y = sys.justiceAt(j).and(z);
      for (iterY = new FixPoint<BDD>(); iterY.advance(y);) {
        for (int i = 0; i < envJustNum; i++) {
          BDD negp = env.justiceAt(i).not();
          BDD x = z.id();
          for (iterX = new FixPoint<BDD>(); iterX.advance(x);) {
            x = env.yieldStates(sys, x.and(negp).or(y));
          }
          BDD goodTransitions = Env.prime(x).and(sys.trans());
          strategy.get(j).add(goodTransitions);
          y = y.id().or(x);
        }
      }
    }
    return z;
  }

  private BDD yieldStatesWithRestrictedTransitions(BDD to, BDD systemTransitions) {
    BDDVarSet responder_prime = sys.modulePrimeVars();
    BDDVarSet this_prime = env.modulePrimeVars();
    BDD exy = Env.prime(to).and(systemTransitions).exist(responder_prime);
    return env.trans().imp(exy).forAll(this_prime);
  }

  /**
   * <p>
   * Calculating Player-2 losing states.
   * </p>
   * 
   * @return The Player-2 losing states for this game.
   */
  private BDD calculate_win_FS() {
    throw new RuntimeException("Fast-Slow semantics are not implemented anymore.");
  }

  // COX	

  /*public BDD yieldStates(Module env, Module sys, BDD to) {
  
  BDDVarSet env_prime = env.modulePrimeVars();
  BDDVarSet sys_prime = sys.modulePrimeVars();
  BDD exy1 = (Env.prime(to).and(sys.trans())).exist(sys_slow_prime);		
  BDD exy3 = Env.unprime(Env.prime(to).and(sys.trans()).and(fastSame).exist(sys_prime));		
  BDD exy2 = (sys.trans().and(slowSame.and(exy3))).exist(sys_slow_prime);
  return env.trans().imp((exy1.and(exy2)).exist(sys_fast_prime)).forAll(env_prime);
  }*/
  public BDD controlStates(Module this1, Module responder, BDD to) {
    BDDVarSet responder_prime = responder.modulePrimeVars();
    BDDVarSet this_prime = this1.modulePrimeVars();
    BDD exy = responder.trans().imp(Env.prime(to)).forAll(responder_prime);
    return this1.trans().and(exy).exist(this_prime);
  }

  
  /**
   * <p>
   * Extracting an arbitrary implementation from the set of possible
   * strategies. 
   * The second argument changes the priority of searching for different types of moves in the game
   * </p>
   */
  public void printWinningStrategy(BDD ini) {
    calculate_strategy(ini);
    // return calculate_strategy(3);
    // return calculate_strategy(7);
    // return calculate_strategy(11);
    // return calculate_strategy(15);
    // return calculate_strategy(19);
    // return calculate_strategy(23);
  }


  /**
   * <p>
   * Extracting an implementation from the set of possible strategies with the
   * given priority to the next step, following the approach outlined in	
   * </p>
   * <p>
   * Nir Piterman, Amir Pnueli, and Yaniv Sa'ar. Synthesis of Reactive(1) Designs.
   * In VMCAI 2006, pp. 364-380.
   * </p>
   * <p>
   * Possible priorities are:<br>
   * 3 - Z Y X.<br>
   * 7 - Z X Y.<br>
   * 11 - Y Z X.<br>
   * 15 - Y X Z.<br>
   * 19 - X Z Y.<br>
   * 23 - X Y Z.<br>
   * </p>
   * 
   * @param kind
   *            The priority kind.
   * @param det
   *            true if a deterministic strategy is desired, otherwise false
   */
  public boolean calculate_strategy(BDD ini) {
    
    
    Stack<BDD> st_stack = new Stack<BDD>();
    Stack<Integer> j_stack = new Stack<Integer>();
    Stack<RawState> aut = new Stack<RawState>();
    boolean result;
    if (ini.isZero()) {
      result = false;
    } else {
      result = true;
    }

    
    BDDIterator ini_iterator = ini.iterator(env.moduleUnprimeVars().union(sys.moduleUnprimeVars()));
    while (ini_iterator.hasNext()) {
      BDD this_ini = (BDD) ini_iterator.next();

      RawState test_st = new RawState(aut.size(), this_ini, 0);

      int idx = -1;
      for (RawState cmp_st : aut) {
        if (cmp_st.equals(test_st, false)) { // search ignoring rank
          idx = aut.indexOf(cmp_st);
          break;
        }
      }

      if (idx != -1) {
        // This initial state is already in the automaton
        continue;
      }

      // Otherwise, we need to attach this initial state to the automaton

      st_stack.push(this_ini);
      j_stack.push(new Integer(0)); // TODO: is there a better default j?
      //this_ini.printSet();

      // iterating over the stacks.
      while (!st_stack.isEmpty()) {
        // making a new entry.
        BDD p_st = st_stack.pop();
        int p_j = j_stack.pop().intValue();

        /* 
         * Create a new automaton state for our current state 
         * (or use a matching one if it already exists) 
         * p_st is the current state value,
         * and p_j is the system goal currently being pursued.
         * cf. RawState class definition below.
         */
        RawState new_state = new RawState(aut.size(), p_st, p_j);
        int nidx = aut.indexOf(new_state);
        if (nidx == -1) {
          aut.push(new_state);
        } else {
          new_state = aut.elementAt(nidx);
        }
        
        
        
        for (BDDIterator all_states = Env.TRUE().iterator(env.modulePrimeVars()); all_states.hasNext();) {
          BDD nextInput = (BDD) all_states.next();
          BDD searchingForOutputFrom = nextInput.and(p_st);
          
          boolean done=false; 
          for (int k=0;(k<strategy.get(p_j).size()) && !done;k++) {
            BDD conjunction = strategy.get(p_j).get(k).and(searchingForOutputFrom);
            if (!(conjunction.isZero())) {
              // Successor found
              done = true;
              BDD nextStatePossitibilities = Env.unprime(conjunction.exist(env.moduleUnprimeVars().union(sys.moduleUnprimeVars())));
              BDD nextStatePossibilitiesThatSatisfyLivenessGoal = nextStatePossitibilities.and(sys.justiceAt(p_j));
              if (!(nextStatePossibilitiesThatSatisfyLivenessGoal.isZero())) {
                BDDIterator candIter = nextStatePossibilitiesThatSatisfyLivenessGoal.iterator(env.moduleUnprimeVars().union(
                  sys.moduleUnprimeVars()));
                BDD one_cand = (BDD) candIter.next();
                
                int next_p_j = (p_j + 1) % sysJustNum;
                // Cycle through goals that are trivially satisfied by staying in the exact same state.
                // (This is essentially stutter-state removal)
                while (!one_cand.and(sys.justiceAt(next_p_j)).isZero() && next_p_j != p_j) {
                  next_p_j = (next_p_j + 1) % sysJustNum;
                }
            
                RawState gsucc = new RawState(aut.size(), one_cand, next_p_j);
                idx = aut.indexOf(gsucc); // the equals doesn't consider
                // the id number.
                if (idx == -1) {
                  st_stack.push(one_cand);
                  j_stack.push(next_p_j);
                  aut.add(gsucc);
                  idx = aut.indexOf(gsucc);
                }
                new_state.add_succ(aut.elementAt(idx));
                
              } else {
                BDDIterator candIter = nextStatePossitibilities.iterator(env.moduleUnprimeVars().union(
                  sys.moduleUnprimeVars()));
                BDD one_cand = (BDD) candIter.next();
                
                RawState gsucc = new RawState(aut.size(), one_cand, p_j);
                idx = aut.indexOf(gsucc); // the equals doesn't consider
                // the id number.
                if (idx == -1) {
                  st_stack.push(one_cand);
                  j_stack.push(p_j);
                  aut.add(gsucc);
                  idx = aut.indexOf(gsucc);
                }
                new_state.add_succ(aut.elementAt(idx));
              }
            }
            
            
          }
          if (!done) {
            throw new RuntimeException("Found no successor.");
          }
        }
      }
    }

    /* Print output */
    String res = "";

    for (RawState state : aut) {
      if (state.get_rank() != -1) {
        res += state + "\n";
      }
    }

    System.out.print("\n\n");
    System.out.print(res);
    // return null; // res;
    System.out.print("\n\n");
    return result;
  }

 
  /**
   * <p>
   * Extracting a safety automaton characterizing all allowed system moves. 
   * Used to restrict the user during counterstrategy visualization with Mopsy.	 
   */
  public void generate_safety_aut(BDD ini) {
    Stack<BDD> st_stack = new Stack<BDD>();
    Stack<RawState> aut = new Stack<RawState>();

    BDDIterator ini_iterator = ini.iterator(env.moduleUnprimeVars().union(sys.moduleUnprimeVars()));

    while (ini_iterator.hasNext()) {

      BDD this_ini = (BDD) ini_iterator.next();

      RawState test_st = new RawState(aut.size(), this_ini, 0);

      int idx = -1;
      for (RawState cmp_st : aut) {
        if (cmp_st.equals(test_st, false)) { // search ignoring rank
          idx = aut.indexOf(cmp_st);
          break;
        }
      }

      if (idx != -1) {
        // This initial state is already in the automaton
        continue;
      }

      // Otherwise, we need to attach this initial state to the automaton

      st_stack.push(this_ini);

      // iterating over the stacks.
      while (!st_stack.isEmpty()) {
        // making a new entry.
        BDD p_st = st_stack.pop();

        /* Create a new automaton state for our current state 
        (or use a matching one if it already exists) */
        RawState new_state = new RawState(aut.size(), p_st, 0);
        int nidx = aut.indexOf(new_state);
        if (nidx == -1) {
          aut.push(new_state);
        } else {
          new_state = aut.elementAt(nidx);
        }

        BDD next_op = Env.unprime(sys.trans().and(p_st).exist(env.moduleUnprimeVars().union(sys.moduleUnprimeVars())));

        BDDIterator next_iterator = next_op.iterator(env.moduleUnprimeVars().union(sys.moduleUnprimeVars()));
        while (next_iterator.hasNext()) {

          BDD this_next = (BDD) next_iterator.next();
          //this_next.printSet();
          RawState gsucc = new RawState(aut.size(), this_next, 0);
          idx = aut.indexOf(gsucc); // the equals doesn't consider
          // the id number.
          if (idx == -1) {
            st_stack.push(this_next);
            aut.add(gsucc);
            idx = aut.indexOf(gsucc);
          }
          new_state.add_succ(aut.elementAt(idx));
        }

        //System.out.print("------------\n");
      }
    }

    /* Print output */

    String res = "";
    for (RawState state : aut) {
      if (state.get_rank() != -1) {
        res += state + "\n";
      }
    }

    System.out.print("\n\n");
    System.out.print(res);
    // return null; // res;
  }

  //method for adding stated to the aut and state stack, based on whether we want a deterministic or nondet automaton
  private void addState(RawCState new_state, BDD input, int new_i, int new_j, Stack<RawCState> aut, Stack<BDD> st_stack, Stack<Integer> i_stack, Stack<Integer> j_stack, boolean det) {
    for (BDDIterator inputIter = input.iterator(env.modulePrimeVars()); inputIter.hasNext();) {

      BDD inputOne = (BDD) inputIter.next();
      while (det && inputOne.and(env.trans()).isZero() && inputIter.hasNext()) {
        inputOne = (BDD) inputIter.next();
      }
      if (inputOne.and(env.trans()).isZero()) {
        break;
      }


      // computing the set of system possible successors.
      Vector<BDD> sys_succs = new Vector<BDD>();
      BDD all_sys_succs = sys.succ(new_state.get_state().and(inputOne));

      int idx = -1;

      if (all_sys_succs.equals(Env.FALSE())) {
        RawCState gsucc = new RawCState(aut.size(), Env.unprime(inputOne), new_j, new_i, inputOne);
        idx = aut.indexOf(gsucc); // the equals doesn't consider
        // the id number.
        if (idx == -1) {
          aut.add(gsucc);
          idx = aut.indexOf(gsucc);
        }
        new_state.add_succ(aut.elementAt(idx));

        continue;
      }


      for (BDDIterator all_sys_states = all_sys_succs.iterator(sys.moduleUnprimeVars().union(env.moduleUnprimeVars())); all_sys_states.hasNext();) {
        BDD sin = (BDD) all_sys_states.next();
        sys_succs.add(sin);
      }



      // For each system successor, find a strategy successor
      for (Iterator<BDD> iter_succ = sys_succs.iterator(); iter_succ.hasNext();) {
        BDD sys_succ = iter_succ.next().and(Env.unprime(inputOne));

        //Make sure this is a safe successor state
        if (!sys_succ.and(sys.trans()).isZero()) {

          RawCState gsucc = new RawCState(aut.size(), sys_succ, new_j, new_i, inputOne);
          idx = aut.indexOf(gsucc); // the equals doesn't consider
          // the id number.
          if (idx == -1) {
            //System.out.println("Adding system successor = " + sys_succ + " of " + new_state.get_state());

            st_stack.push(sys_succ);
            i_stack.push(new_i);
            j_stack.push(new_j);
            aut.add(gsucc);
            idx = aut.indexOf(gsucc);
          }
          new_state.add_succ(aut.elementAt(idx));
        }
      }
      if (det) {
        break;
      }
    }
  }

  @SuppressWarnings("unused")
  //Class for a state of the STRATEGY automaton. 
  //The "rank" is the system goal currently being pursued.
  private class RawState {

    private int id;
    private int rank;
    private BDD state;
    private Vector<RawState> succ;

    public RawState(int id, BDD state, int rank) {
      this.id = id;
      this.state = state;
      this.rank = rank;
      succ = new Vector<RawState>(10);
    }

    public void add_succ(RawState to_add) {
      succ.add(to_add);
    }

    public void del_succ(RawState to_del) {
      succ.remove(to_del);
    }

    public BDD get_state() {
      return this.state;
    }

    public int get_rank() {
      return this.rank;
    }

    public void set_rank(int rank) {
      this.rank = rank;
    }

    public Vector<RawState> get_succ() {
      //RawState[] res = new RawState[this.succ.size()];
      //this.succ.toArray(res);
      return this.succ;
    }

    public boolean equals(Object other) {
      return this.equals(other, true);
    }

    public boolean equals(Object other, boolean use_rank) {
      if (!(other instanceof RawState)) {
        return false;
      }
      RawState other_raw = (RawState) other;
      if (other_raw == null) {
        return false;
      }

      if (use_rank) {
        return ((this.rank == other_raw.rank) & (this.state.equals(other_raw.state)));
      } else {
        return (this.state.equals(other_raw.state));
      }
    }

    public String toString() {
      String res = "State " + id + " with rank " + rank + " -> "
              + state.toStringWithDomains(Env.stringer) + "\n";
      if (succ.isEmpty()) {
        res += "\tWith no successors.";
      } else {
        RawState[] all_succ = new RawState[succ.size()];
        succ.toArray(all_succ);
        res += "\tWith successors : " + all_succ[0].id;
        for (int i = 1; i < all_succ.length; i++) {
          res += ", " + all_succ[i].id;
        }
      }
      return res;
    }
  }

  //Class for a state of the COUNTERSTRATEGY automaton.  
  //"rank_i" is the environment goal currently being pursued, 
  //and "rank_j" is the system goal currently being prevented.
  private class RawCState {

    private int id;
    private int rank_i;
    private int rank_j;
    private BDD input;
    private BDD state;
    private Vector<RawCState> succ;

    public RawCState(int id, BDD state, int rank_j, int rank_i, BDD input) {
      this.id = id;
      this.state = state;
      this.rank_i = rank_i;
      this.rank_j = rank_j;
      this.input = input;
      succ = new Vector<RawCState>(10);
    }

    public void add_succ(RawCState to_add) {
      succ.add(to_add);
    }

    public void del_succ(RawCState to_del) {
      succ.remove(to_del);
    }

    public BDD get_input() {
      return this.input;
    }

    public void set_input(BDD input) {
      this.input = input;
    }

    public BDD get_state() {
      return this.state;
    }

    public int get_rank_i() {
      return this.rank_i;
    }

    public void set_rank_i(int rank) {
      this.rank_i = rank;
    }

    public int get_rank_j() {
      return this.rank_j;
    }

    public void set_rank_j(int rank) {
      this.rank_j = rank;
    }

    public boolean equals(Object other) {
      return this.equals(other, true);
    }

    public boolean equals(Object other, boolean use_rank) {
      if (!(other instanceof RawCState)) {
        return false;
      }
      RawCState other_raw = (RawCState) other;
      if (other_raw == null) {
        return false;
      }
      if (use_rank) {
        return ((this.rank_i == other_raw.rank_i) & (this.rank_j == other_raw.rank_j)
                & (this.state.equals(other_raw.state)));
      } else {
        return ((this.state.equals(other_raw.state)));
      }
    }

    public String toString() {
      String res = "State " + id + " with rank (" + rank_i + "," + rank_j + ") -> "
              + state.toStringWithDomains(Env.stringer) + "\n";
      if (succ.isEmpty()) {
        res += "\tWith no successors.";
      } else {
        RawCState[] all_succ = new RawCState[succ.size()];
        succ.toArray(all_succ);
        res += "\tWith successors : " + all_succ[0].id;
        for (int i = 1; i < all_succ.length; i++) {
          res += ", " + all_succ[i].id;
        }
      }
      return res;
    }
  }

  /**
   * <p>
   * Getter for the environment player.
   * </p>
   * 
   * @return The environment player.
   */
  public ModuleWithWeakFairness getEnvPlayer() {
    return env;
  }

  /**
   * <p>
   * Getter for the system player.
   * </p>
   * 
   * @return The system player.
   */
  public ModuleWithWeakFairness getSysPlayer() {
    return sys;
  }

  /**
   * <p>
   * Getter for the environment's winning states.
   * </p>
   * 
   * @return The environment's winning states.
   */
  public BDD sysWinningStates() {
    return player2_winning;
  }

  /**
   * <p>
   * Getter for the system's winning states.
   * </p>
   * 
   * @return The system's winning states.
   */
  public BDD envWinningStates() {
    return player2_winning.not();
  }

  public BDD gameInitials() {
    return getSysPlayer().initial().and(getEnvPlayer().initial());
  }

  public BDD[] playersWinningStates() {
    return new BDD[]{envWinningStates(), sysWinningStates()};
  }

  public BDD firstPlayersWinningStates() {
    return envWinningStates();
  }

  public BDD secondPlayersWinningStates() {
    return sysWinningStates();
  }
}
