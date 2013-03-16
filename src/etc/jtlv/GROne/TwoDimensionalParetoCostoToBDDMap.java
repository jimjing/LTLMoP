import edu.wis.jtlv.env.Env;
import java.util.ArrayList;
import java.util.Map;
import java.util.TreeMap;
import java.util.TreeSet;
import net.sf.javabdd.BDD;

/**
 * A class that is used as a "todo and best-results-so-far" keeper. In the GR(1)
 * synthesis algorithm, for every combination
 * of waiting + transition cost, it keeps the set of of positions from which.
 * we can reach the goal with at most that cost. Combinations that are subsumed
 * by strictly better cost tuples are removed (at least if they lie on the same level of waiting costs).
 * 
 * @author ruedi
 */
class TwoDimensionalParetoCostoToBDDMap {
  
  ArrayList< TreeMap< Double, BDD > > storage; // Outer index: waiting cost (always a natural number), then the accumulated transition cost
  
  /**
   * Add newly found states. Only introduce a new element in the two-dimensional
   * storage table if we actually found some new state. Always add all newly found states to states that are stricly
   * "worse" in the Pareto-Front, i.e., that have a higher cost.
   * @param waitingCost The discrete waiting cost under which the new states can be reached
   * @param transitionCost The continuous transition cost (e.g., distance to be traveled by the robot)
   * @param unprimedStates The new states
   * @return If any new state was actually added - sometimes, all states were already covered by lower
   *         cost tuples and then this function returns false
   */
  public boolean add(int waitingCost, double transitionCost, BDD unprimedStates) {
    BDD oldStates = Env.FALSE().id();
    for (int i=0;(i<storage.size() && (i<=waitingCost));i++) {
      for (Map.Entry<Double, BDD> a : storage.get(i).entrySet()) {
        if (a.getKey()<=transitionCost) {
          oldStates = oldStates.or(a.getValue());
        }
      }
    }
    if (!(unprimedStates.and(oldStates.not()).isZero())) {
      // We found some new element.
      while (storage.size()<=waitingCost) storage.add(new TreeMap<Double, BDD>());
      
      // Add an element to ensure that we can add the optimum in the following loop
      if (!(storage.get(waitingCost).containsKey(transitionCost))) {
        storage.get(waitingCost).put(transitionCost,Env.FALSE());
      }
        
      // Update the states with higher cost values
      for (int i=waitingCost;i<storage.size();i++) {
        BDD lastElement = Env.FALSE();
        TreeSet<Double> listOfNowSuperfluousElements = new TreeSet<Double>();
        for (Map.Entry<Double, BDD> a : storage.get(i).entrySet()) {
          if (a.getKey()>=transitionCost) {
            BDD oldData = a.getValue();
            BDD newData = oldData.or(unprimedStates);
            if (lastElement.equals(newData)) {
              listOfNowSuperfluousElements.add(a.getKey());
            } else {
              lastElement = newData;
              a.setValue(newData);
            }
          }
        }
        for (Double a : listOfNowSuperfluousElements) {
          storage.get(i).remove(a);
        }
      }
    
      return true;
    } else {
      return false;
    }
  }
  
  BDD getBDD(int waitingCost, double transitionCost) {
    if (storage.size()<=waitingCost) throw new RuntimeException("Illegal discrete cost.");
    TreeMap< Double, BDD > weightMap = storage.get(waitingCost);
    if (!(weightMap.containsKey(transitionCost))) throw new RuntimeException("Illegal continuous cost.");
    return weightMap.get(transitionCost);
  }
  
  int getMaxDiscreteCost() {
    return storage.size()-1;
  }
  
  /**
   * 
   * @param waitingCost
   * @param previousTransitionCost
   * @return Null if no more key element at this discrete cost level exists
   */
  Double getNextTransitionCostAtDiscreteLevel(int waitingCost, double previousTransitionCost) {
    if (storage.size()<=waitingCost) throw new RuntimeException("Illegal discrete cost.");
    TreeMap< Double, BDD > weightMap = storage.get(waitingCost);
    return weightMap.higherKey(previousTransitionCost);
  }
  
  
  /**
   * Just the constructor. Nothing special.
   */
  TwoDimensionalParetoCostoToBDDMap() {
    storage = new ArrayList< TreeMap< Double, BDD > > ();
  }
  
}
