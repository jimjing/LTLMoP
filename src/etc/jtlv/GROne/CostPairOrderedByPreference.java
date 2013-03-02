/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

/**
 *
 * @author ruedi
 */
public class CostPairOrderedByPreference implements Comparable <CostPairOrderedByPreference> {
  private int waitingCost;
  private double transitionCost;
  
  public CostPairOrderedByPreference(int _waitingCost, double _transitionCost) {
    waitingCost = _waitingCost;
    transitionCost = _transitionCost;
  }

  /**
   * @return the waitingCost
   */
  public int getWaitingCost() {
    return waitingCost;
  }

  /**
   * @return the transitionCost
   */
  public double getTransitionCost() {
    return transitionCost;
  }

  @Override
  public int compareTo(CostPairOrderedByPreference arg0) {
    if (waitingCost<arg0.waitingCost) return -2;
    if (waitingCost>arg0.waitingCost) return 2;
    if (transitionCost<arg0.transitionCost) return -1;
    if (transitionCost>arg0.transitionCost) return 1;
    return 0;
  }
  
  
  
}
