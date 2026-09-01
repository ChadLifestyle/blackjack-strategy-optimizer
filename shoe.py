"""
Shoe tracking module for exact card counting and state management.
Maintains the exact composition of remaining cards in the shoe.
"""

from typing import Dict, List, Tuple
from collections import defaultdict


class Shoe:
    """
    Represents a blackjack shoe with exact card tracking.
    Maintains a state vector of remaining cards for each denomination.
    """
    
    def __init__(self, num_decks: int = 6):
        """
        Initialize a shoe with the specified number of decks.
        
        Args:
            num_decks: Number of standard 52-card decks in the shoe (default 6)
        """
        self.num_decks = num_decks
        self.total_cards = num_decks * 52
        
        # State vector: card value -> count remaining
        # Aces are represented as 11 (for tracking purposes)
        self.state: Dict[int, int] = {
            2: num_decks * 4,
            3: num_decks * 4,
            4: num_decks * 4,
            5: num_decks * 4,
            6: num_decks * 4,
            7: num_decks * 4,
            8: num_decks * 4,
            9: num_decks * 4,
            10: num_decks * 4,  # 10, J, Q, K all count as 10
            11: num_decks * 4,  # Aces
        }
    
    def remove_card(self, card_value: int) -> bool:
        """
        Remove a card from the shoe.
        
        Args:
            card_value: Card value (2-10, 11 for Ace)
            
        Returns:
            True if card was removed, False if card not available
        """
        if card_value not in self.state or self.state[card_value] <= 0:
            return False
        
        self.state[card_value] -= 1
        return True
    
    def add_card(self, card_value: int) -> bool:
        """
        Add a card back to the shoe (for undo operations).
        
        Args:
            card_value: Card value (2-10, 11 for Ace)
            
        Returns:
            True if card was added, False if invalid
        """
        if card_value not in self.state:
            return False
        
        if self.state[card_value] >= self.num_decks * 4:
            return False
        
        self.state[card_value] += 1
        return True
    
    def get_state_vector(self) -> Dict[int, int]:
        """
        Get a copy of the current state vector.
        
        Returns:
            Dictionary of card value -> count
        """
        return self.state.copy()
    
    def get_remaining_cards(self) -> int:
        """
        Get total number of remaining cards in shoe.
        
        Returns:
            Total cards remaining
        """
        return sum(self.state.values())
    
    def get_penetration(self) -> float:
        """
        Get shoe penetration (percentage of cards dealt).
        
        Returns:
            Penetration as float between 0 and 1
        """
        remaining = self.get_remaining_cards()
        return 1.0 - (remaining / self.total_cards)
    
    def reset_shoe(self):
        """Reset the shoe to its initial state."""
        for card_value in self.state:
            self.state[card_value] = self.num_decks * 4
    
    def get_card_probability(self, card_value: int) -> float:
        """
        Get probability of drawing a specific card value.
        
        Args:
            card_value: Card value (2-10, 11 for Ace)
            
        Returns:
            Probability as float between 0 and 1
        """
        remaining = self.get_remaining_cards()
        if remaining <= 0:
            return 0.0
        
        return self.state.get(card_value, 0) / remaining
    
    def get_all_probabilities(self) -> Dict[int, float]:
        """
        Get probability distribution for all card values.
        
        Returns:
            Dictionary of card value -> probability
        """
        remaining = self.get_remaining_cards()
        if remaining <= 0:
            return {k: 0.0 for k in range(2, 12)}
        
        return {
            card_value: self.state.get(card_value, 0) / remaining
            for card_value in range(2, 12)
        }
    
    def __repr__(self) -> str:
        """String representation of shoe state."""
        remaining = self.get_remaining_cards()
        penetration = self.get_penetration()
        return (f"Shoe({self.num_decks} decks): {remaining} cards remaining "
                f"({penetration*100:.1f}% penetration)")
