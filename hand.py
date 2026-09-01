"""
Hand representation and evaluation module.
Handles blackjack hand composition and value calculations.
"""

from typing import List, Tuple, Dict
from enum import Enum


class HandType(Enum):
    """Classification of hand types."""
    HARD = "Hard"           # No aces or only aces counted as 1
    SOFT = "Soft"           # Contains ace(s) counted as 11
    BLACKJACK = "Blackjack" # Natural 21 (two cards)
    BUST = "Bust"           # Over 21


class Hand:
    """
    Represents a blackjack hand with composition tracking.
    Supports composition-dependent strategy decisions.
    """
    
    def __init__(self, cards: List[int] = None):
        """
        Initialize a hand with cards.
        
        Args:
            cards: List of card values (2-10, 11 for Ace)
        """
        self.cards = cards if cards else []
    
    def add_card(self, card_value: int) -> None:
        """
        Add a card to the hand.
        
        Args:
            card_value: Card value (2-10, 11 for Ace)
        """
        self.cards.append(card_value)
    
    def get_cards(self) -> List[int]:
        """Get list of cards in hand."""
        return self.cards.copy()
    
    def get_hand_composition(self) -> Dict[int, int]:
        """
        Get composition breakdown of hand.
        
        Returns:
            Dictionary of card value -> count
        """
        composition = {}
        for card in self.cards:
            composition[card] = composition.get(card, 0) + 1
        return composition
    
    def count_aces(self) -> int:
        """Count number of aces in hand."""
        return sum(1 for card in self.cards if card == 11)
    
    def get_values(self) -> Tuple[int, int]:
        """
        Get minimum and maximum possible values for hand.
        
        Returns:
            Tuple of (min_value, max_value)
        """
        total = sum(self.cards)
        num_aces = self.count_aces()
        
        # Start with all aces as 11
        min_value = total
        
        # Convert aces from 11 to 1 until hand is 21 or below
        for _ in range(num_aces):
            if min_value > 21:
                min_value -= 10  # Convert one ace from 11 to 1
            else:
                break
        
        return (min_value, total)
    
    def get_value(self) -> int:
        """
        Get the optimal value for the hand (used for play decisions).
        
        Returns:
            Hand value (respects blackjack rules)
        """
        min_val, max_val = self.get_values()
        
        if max_val <= 21:
            return max_val
        else:
            return min_val
    
    def get_hand_type(self) -> HandType:
        """
        Classify the hand type.
        
        Returns:
            HandType enum value
        """
        if len(self.cards) == 2 and self.get_value() == 21:
            return HandType.BLACKJACK
        elif self.get_value() > 21:
            return HandType.BUST
        elif self._is_soft():
            return HandType.SOFT
        else:
            return HandType.HARD
    
    def _is_soft(self) -> bool:
        """Check if hand is soft (has usable ace)."""
        if self.count_aces() == 0:
            return False
        
        # Sum all cards except one ace
        total = sum(self.cards) - 10  # Treat one ace as 1 instead of 11
        
        # If this results in 21 or less, we have a usable ace
        return total <= 21
    
    def is_pair(self) -> bool:
        """Check if hand is a pair (two cards of same value)."""
        return len(self.cards) == 2 and self.cards[0] == self.cards[1]
    
    def get_pair_value(self) -> int:
        """
        Get value if hand is a pair.
        
        Returns:
            Card value of pair, or -1 if not a pair
        """
        if self.is_pair():
            return self.cards[0]
        return -1
    
    def is_blackjack(self) -> bool:
        """Check if hand is a natural blackjack."""
        return self.get_hand_type() == HandType.BLACKJACK
    
    def is_bust(self) -> bool:
        """Check if hand is bust."""
        return self.get_value() > 21
    
    def can_double(self) -> bool:
        """Check if hand can be doubled (two cards, value 9-11)."""
        if len(self.cards) != 2:
            return False
        value = self.get_value()
        return 9 <= value <= 11
    
    def can_split(self) -> bool:
        """Check if hand can be split."""
        return len(self.cards) == 2 and self.is_pair()
    
    def get_soft_value(self) -> int:
        """
        Get soft value (with ace as 11 if possible).
        
        Returns:
            Hand value with ace counted as 11
        """
        total = sum(self.cards)
        num_aces = self.count_aces()
        
        if num_aces > 0 and total - 10 <= 21:
            return total - 10  # Keep one ace as 11, rest as 1
        else:
            return total
    
    def get_hard_value(self) -> int:
        """
        Get hard value (all aces as 1).
        
        Returns:
            Hand value with all aces counted as 1
        """
        total = sum(self.cards)
        num_aces = self.count_aces()
        return total - (10 * num_aces)
    
    def __repr__(self) -> str:
        """String representation of hand."""
        composition = self.get_hand_composition()
        value = self.get_value()
        hand_type = self.get_hand_type().value
        
        cards_str = ", ".join(
            f"A" if c == 11 else str(c) for c in sorted(self.cards, reverse=True)
        )
        
        return f"Hand({cards_str}) = {value} [{hand_type}]"


class DealerHand(Hand):
    """
    Specialized hand for dealer's hand.
    Dealer shows one card initially.
    """
    
    def get_upcard(self) -> int:
        """
        Get dealer's upcard (first visible card).
        
        Returns:
            Upcard value
        """
        return self.cards[0] if self.cards else 0
    
    def get_hole_card(self) -> int:
        """
        Get dealer's hole card (face-down card).
        
        Returns:
            Hole card value, or 0 if not yet dealt
        """
        return self.cards[1] if len(self.cards) > 1 else 0
    
    def get_visible_cards(self) -> List[int]:
        """
        Get dealer's visible cards (only upcard initially).
        
        Returns:
            List containing only the upcard
        """
        return [self.cards[0]] if self.cards else []
