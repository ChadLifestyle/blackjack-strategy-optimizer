"""
Expected Value (EV) calculation module.
Computes optimal decisions based on exact shoe composition.
Uses dynamic programming and recursive game tree evaluation.
"""

from typing import Dict, Tuple, Optional
from hand import Hand, DealerHand, HandType
from shoe import Shoe
from functools import lru_cache
import math


class EVCalculator:
    """
    Calculates expected value for each possible action in blackjack.
    Considers exact shoe composition for accurate probability calculations.
    """
    
    def __init__(self, shoe: Shoe, dealer_upcard: int):
        """
        Initialize EV calculator.
        
        Args:
            shoe: Shoe object with current card composition
            dealer_upcard: Dealer's visible card (2-11)
        """
        self.shoe = shoe
        self.dealer_upcard = dealer_upcard
        self.cache: Dict = {}
    
    def calculate_player_ev(self, player_hand: Hand, 
                           dealer_hand: DealerHand,
                           can_double: bool = True,
                           can_split: bool = True,
                           can_surrender: bool = True) -> Dict[str, float]:
        """
        Calculate expected value for all available actions.
        
        Args:
            player_hand: Player's current hand
            dealer_hand: Dealer's hand (upcard and hole card)
            can_double: Whether doubling down is allowed
            can_split: Whether splitting is allowed
            can_surrender: Whether surrender is allowed
            
        Returns:
            Dictionary of action -> EV value
        """
        ev_dict = {}
        
        # Hit EV
        ev_dict['hit'] = self._calculate_hit_ev(player_hand, dealer_hand)
        
        # Stand EV
        ev_dict['stand'] = self._calculate_stand_ev(player_hand, dealer_hand)
        
        # Double Down EV (if allowed and possible)
        if can_double and player_hand.can_double():
            ev_dict['double'] = self._calculate_double_ev(player_hand, dealer_hand)
        
        # Split EV (if allowed and possible)
        if can_split and player_hand.can_split():
            ev_dict['split'] = self._calculate_split_ev(player_hand, dealer_hand)
        
        # Surrender EV (if allowed and hand is not blackjack)
        if can_surrender and len(player_hand.cards) == 2 and not player_hand.is_blackjack():
            ev_dict['surrender'] = -0.5  # Surrender always returns -0.5
        
        return ev_dict
    
    def get_best_action(self, player_hand: Hand,
                       dealer_hand: DealerHand,
                       can_double: bool = True,
                       can_split: bool = True,
                       can_surrender: bool = True) -> Tuple[str, float]:
        """
        Get the action with highest expected value.
        
        Args:
            player_hand: Player's current hand
            dealer_hand: Dealer's hand
            can_double: Whether doubling down is allowed
            can_split: Whether splitting is allowed
            can_surrender: Whether surrender is allowed
            
        Returns:
            Tuple of (best_action, ev_value)
        """
        ev_dict = self.calculate_player_ev(
            player_hand, dealer_hand,
            can_double, can_split, can_surrender
        )
        
        if not ev_dict:
            return ('stand', 0.0)
        
        best_action = max(ev_dict, key=ev_dict.get)
        return (best_action, ev_dict[best_action])
    
    def _calculate_hit_ev(self, player_hand: Hand, dealer_hand: DealerHand) -> float:
        """
        Calculate expected value of hitting.
        
        Args:
            player_hand: Player's current hand
            dealer_hand: Dealer's hand
            
        Returns:
            EV of hitting (weighted average over all possible next cards)
        """
        if player_hand.is_bust():
            return -1.0
        
        probs = self.shoe.get_all_probabilities()
        total_ev = 0.0
        
        for next_card in range(2, 12):
            prob = probs.get(next_card, 0.0)
            
            if prob > 0:
                # Create new hand with the drawn card
                new_hand = Hand(player_hand.cards + [next_card])
                
                if new_hand.is_bust():
                    # Bust is -1
                    total_ev += prob * (-1.0)
                elif new_hand.get_value() >= 17:
                    # Must stand now
                    ev = self._calculate_stand_ev(new_hand, dealer_hand)
                    total_ev += prob * ev
                else:
                    # Recursively calculate hit EV
                    ev = self._calculate_hit_ev(new_hand, dealer_hand)
                    total_ev += prob * ev
        
        return total_ev
    
    def _calculate_stand_ev(self, player_hand: Hand, dealer_hand: DealerHand) -> float:
        """
        Calculate expected value of standing.
        
        Args:
            player_hand: Player's current hand
            dealer_hand: Dealer's hand
            
        Returns:
            EV of standing (based on dealer's likely outcome)
        """
        player_value = player_hand.get_value()
        
        if player_value > 21:
            return -1.0  # Player bust
        
        # Calculate dealer's outcome probabilities
        dealer_ev = self._calculate_dealer_ev(dealer_hand)
        
        # Compare outcomes
        total_ev = 0.0
        
        for dealer_value, prob in dealer_ev.items():
            if dealer_value > 21:
                # Dealer bust, player wins
                total_ev += prob * 1.0
            elif dealer_value > player_value:
                # Dealer wins
                total_ev += prob * (-1.0)
            elif dealer_value == player_value:
                # Push (tie)
                total_ev += prob * 0.0
            else:
                # Player wins
                total_ev += prob * 1.0
        
        return total_ev
    
    def _calculate_double_ev(self, player_hand: Hand, dealer_hand: DealerHand) -> float:
        """
        Calculate expected value of doubling down.
        
        Args:
            player_hand: Player's current hand
            dealer_hand: Dealer's hand
            
        Returns:
            EV of doubling (returns 2x payout)
        """
        probs = self.shoe.get_all_probabilities()
        total_ev = 0.0
        
        for next_card in range(2, 12):
            prob = probs.get(next_card, 0.0)
            
            if prob > 0:
                new_hand = Hand(player_hand.cards + [next_card])
                # After double, player must stand
                ev = self._calculate_stand_ev(new_hand, dealer_hand)
                # Double means return is 2x
                total_ev += prob * (2.0 * ev)
        
        return total_ev
    
    def _calculate_split_ev(self, player_hand: Hand, dealer_hand: DealerHand) -> float:
        """
        Calculate expected value of splitting.
        
        Args:
            player_hand: Player's current hand (must be a pair)
            dealer_hand: Dealer's hand
            
        Returns:
            EV of splitting (average EV of two hands)
        """
        if not player_hand.is_pair():
            return 0.0
        
        card_value = player_hand.cards[0]
        probs = self.shoe.get_all_probabilities()
        
        # Expected value for one split hand
        single_hand_ev = 0.0
        
        for next_card in range(2, 12):
            prob = probs.get(next_card, 0.0)
            
            if prob > 0:
                new_hand = Hand([card_value, next_card])
                
                if new_hand.is_blackjack() and card_value == 11:
                    # Aces split gives 21, not blackjack (typically 1:1)
                    ev = 1.0
                else:
                    # Recursively calculate optimal play for split hand
                    ev_dict = self.calculate_player_ev(
                        new_hand, dealer_hand,
                        can_double=True,
                        can_split=False,  # Usually can't resplit
                        can_surrender=False
                    )
                    best_ev = max(ev_dict.values()) if ev_dict else 0.0
                    ev = best_ev
                
                single_hand_ev += prob * ev
        
        # Split creates two hands, so total EV is 2x single hand EV
        # But we use initial bet on each hand
        return 2.0 * single_hand_ev
    
    def _calculate_dealer_ev(self, dealer_hand: DealerHand) -> Dict[int, float]:
        """
        Calculate probability distribution of dealer's final hand value.
        
        Args:
            dealer_hand: Dealer's hand (must have at least upcard)
            
        Returns:
            Dictionary of final_value -> probability
        """
        dealer_upcard = dealer_hand.get_upcard()
        
        # Use memoization for dealer outcomes
        cache_key = tuple(sorted(dealer_hand.cards))
        if cache_key in self.cache:
            return self.cache[cache_key].copy()
        
        # Simulate all possible dealer outcomes
        outcomes = {}
        self._dealer_recurse(dealer_hand, outcomes)
        
        # Convert counts to probabilities
        total = sum(outcomes.values())
        prob_dict = {value: count / total for value, count in outcomes.items()}
        
        self.cache[cache_key] = prob_dict
        return prob_dict
    
    def _dealer_recurse(self, dealer_hand: DealerHand, 
                       outcomes: Dict[int, float]) -> None:
        """
        Recursively calculate dealer's hand outcomes.
        
        Args:
            dealer_hand: Current dealer hand
            outcomes: Dictionary to accumulate outcome probabilities
        """
        dealer_value = dealer_hand.get_value()
        
        # Dealer must hit on 16 or less, stand on 17+
        if dealer_value >= 17:
            # Terminal state
            outcomes[dealer_value] = outcomes.get(dealer_value, 0.0) + 1.0
            return
        
        # Dealer must hit - iterate through all possible cards
        probs = self.shoe.get_all_probabilities()
        
        for next_card in range(2, 12):
            prob = probs.get(next_card, 0.0)
            
            if prob > 0:
                new_hand = DealerHand(dealer_hand.cards + [next_card])
                self._dealer_recurse(new_hand, outcomes)
    
    def clear_cache(self) -> None:
        """Clear the memoization cache."""
        self.cache.clear()
