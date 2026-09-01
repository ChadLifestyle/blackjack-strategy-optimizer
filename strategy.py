"""
Strategy module with basic and composition-dependent strategies.
Provides both traditional basic strategy and adaptive EV-based strategy.
"""

from typing import Dict, Tuple
from hand import Hand, DealerHand
from shoe import Shoe
from ev_calculator import EVCalculator


class Strategy:
    """Base strategy class."""
    
    def get_recommendation(self, player_hand: Hand,
                          dealer_upcard: int,
                          shoe: Shoe) -> Tuple[str, str]:
        """
        Get strategy recommendation.
        
        Args:
            player_hand: Player's hand
            dealer_upcard: Dealer's upcard
            shoe: Current shoe
            
        Returns:
            Tuple of (action, reasoning)
        """
        raise NotImplementedError


class BasicStrategy(Strategy):
    """Traditional basic strategy (composition-independent)."""
    
    def get_recommendation(self, player_hand: Hand,
                          dealer_upcard: int,
                          shoe: Shoe) -> Tuple[str, str]:
        """Get basic strategy recommendation."""
        
        player_value = player_hand.get_value()
        is_soft = player_hand._is_soft()
        is_pair = player_hand.is_pair()
        
        # Pair strategy
        if is_pair:
            pair_value = player_hand.get_pair_value()
            return self._pair_strategy(pair_value, dealer_upcard)
        
        # Soft hand strategy
        if is_soft:
            return self._soft_strategy(player_value, dealer_upcard)
        
        # Hard hand strategy
        return self._hard_strategy(player_value, dealer_upcard)
    
    def _pair_strategy(self, pair_value: int, dealer_upcard: int) -> Tuple[str, str]:
        """Strategy for paired hands."""
        
        # Always split 8s and Aces
        if pair_value == 8 or pair_value == 11:
            return ('split', 'Always split 8s and Aces')
        
        # Never split 5s and 10s
        if pair_value == 5 or pair_value == 10:
            return ('hit' if pair_value == 5 else 'stand', 
                   f'Never split {pair_value}s')
        
        # Split 2s and 3s on 3-7
        if pair_value in [2, 3]:
            if 3 <= dealer_upcard <= 7:
                return ('split', f'Split {pair_value}s against dealer {dealer_upcard}')
            else:
                return ('hit', f'Hit with {pair_value}s against dealer {dealer_upcard}')
        
        # Split 4s on 5-6
        if pair_value == 4:
            if dealer_upcard in [5, 6]:
                return ('split', 'Split 4s on dealer 5-6')
            else:
                return ('hit', 'Hit with 4s')
        
        # Split 6s on 2-7
        if pair_value == 6:
            if 2 <= dealer_upcard <= 7:
                return ('split', f'Split 6s against dealer {dealer_upcard}')
            else:
                return ('hit', f'Hit with 6s against dealer {dealer_upcard}')
        
        # Split 7s on 2-7
        if pair_value == 7:
            if 2 <= dealer_upcard <= 7:
                return ('split', f'Split 7s against dealer {dealer_upcard}')
            else:
                return ('hit', f'Hit with 7s against dealer {dealer_upcard}')
        
        # Split 9s on 2-9 (except 7)
        if pair_value == 9:
            if dealer_upcard in [2, 3, 4, 5, 6, 8, 9]:
                return ('split', f'Split 9s against dealer {dealer_upcard}')
            else:
                return ('stand', f'Stand with 9s against dealer {dealer_upcard}')
        
        return ('hit', 'Default: hit')
    
    def _soft_strategy(self, player_value: int, dealer_upcard: int) -> Tuple[str, str]:
        """Strategy for soft hands (with usable ace)."""
        
        # Soft 13-14: Hit except double on 5-6
        if player_value in [13, 14]:
            if dealer_upcard in [5, 6]:
                return ('double', f'Double soft {player_value} against dealer {dealer_upcard}')
            return ('hit', f'Hit soft {player_value}')
        
        # Soft 15-16: Hit except double on 4-6
        if player_value in [15, 16]:
            if dealer_upcard in [4, 5, 6]:
                return ('double', f'Double soft {player_value} against dealer {dealer_upcard}')
            return ('hit', f'Hit soft {player_value}')
        
        # Soft 17: Hit except double on 3-6
        if player_value == 17:
            if dealer_upcard in [3, 4, 5, 6]:
                return ('double', f'Double soft 17 against dealer {dealer_upcard}')
            return ('hit', 'Hit soft 17')
        
        # Soft 18: Stand except hit on 9-10-A, double on 2-6
        if player_value == 18:
            if dealer_upcard in [2, 3, 4, 5, 6]:
                return ('double', f'Double soft 18 against dealer {dealer_upcard}')
            elif dealer_upcard in [9, 10, 11]:
                return ('hit', 'Hit soft 18 against 9-10-A')
            return ('stand', 'Stand with soft 18')
        
        # Soft 19+: Always stand
        if player_value >= 19:
            return ('stand', f'Stand with soft {player_value}')
        
        return ('hit', f'Hit soft {player_value}')
    
    def _hard_strategy(self, player_value: int, dealer_upcard: int) -> Tuple[str, str]:
        """Strategy for hard hands."""
        
        # 8 or less: always hit
        if player_value <= 8:
            return ('hit', f'Always hit {player_value}')
        
        # 9: double on 3-6, else hit
        if player_value == 9:
            if dealer_upcard in [3, 4, 5, 6]:
                return ('double', 'Double 9 against dealer 3-6')
            return ('hit', 'Hit 9')
        
        # 10: double on 2-9, else hit
        if player_value == 10:
            if 2 <= dealer_upcard <= 9:
                return ('double', f'Double 10 against dealer {dealer_upcard}')
            return ('hit', 'Hit 10')
        
        # 11: always double
        if player_value == 11:
            return ('double', 'Always double 11')
        
        # 12: stand on 4-6, else hit
        if player_value == 12:
            if dealer_upcard in [4, 5, 6]:
                return ('stand', 'Stand 12 against dealer 4-6')
            return ('hit', f'Hit 12 against dealer {dealer_upcard}')
        
        # 13-16: stand on 2-6, else hit
        if 13 <= player_value <= 16:
            if 2 <= dealer_upcard <= 6:
                return ('stand', f'Stand {player_value} on dealer 2-6')
            return ('hit', f'Hit {player_value}')
        
        # 17+: always stand
        if player_value >= 17:
            return ('stand', f'Stand {player_value}')
        
        return ('hit', f'Hit {player_value}')


class CompositionDependentStrategy(Strategy):
    """Strategy that adapts to exact card composition using EV."""
    
    def get_recommendation(self, player_hand: Hand,
                          dealer_upcard: int,
                          shoe: Shoe) -> Tuple[str, str]:
        """Get composition-dependent recommendation using EV."""
        
        # Create dealer hand with known upcard
        dealer_hand = DealerHand([dealer_upcard])
        
        # Calculate EV for all actions
        calculator = EVCalculator(shoe, dealer_upcard)
        ev_dict = calculator.calculate_player_ev(player_hand, dealer_hand)
        
        if not ev_dict:
            return ('stand', 'No actions available')
        
        # Get best action
        best_action = max(ev_dict, key=ev_dict.get)
        best_ev = ev_dict[best_action]
        
        # Format reasoning with EV values
        reasoning = f"Composition-dependent EV: {best_action.upper()} (EV={best_ev:.3f})\n"
        reasoning += "  All options:\n"
        
        for action in sorted(ev_dict.keys()):
            ev = ev_dict[action]
            marker = " ← BEST" if action == best_action else ""
            reasoning += f"    {action:10s}: EV = {ev:7.3f}{marker}\n"
        
        return (best_action, reasoning.strip())


class HybridStrategy(Strategy):
    """Hybrid strategy: uses basic strategy with EV-based adjustments."""
    
    def get_recommendation(self, player_hand: Hand,
                          dealer_upcard: int,
                          shoe: Shoe) -> Tuple[str, str]:
        """Get hybrid recommendation."""
        
        basic_strategy = BasicStrategy()
        comp_strategy = CompositionDependentStrategy()
        
        basic_action, basic_reason = basic_strategy.get_recommendation(
            player_hand, dealer_upcard, shoe
        )
        
        comp_action, comp_reason = comp_strategy.get_recommendation(
            player_hand, dealer_upcard, shoe
        )
        
        # If they agree, use basic strategy (faster)
        if basic_action == comp_action:
            return (basic_action, f"Basic strategy: {basic_reason}")
        
        # If they disagree, note the difference
        reasoning = (
            f"Basic strategy: {basic_action}\n"
            f"Composition-dependent: {comp_action}\n\n"
            f"{comp_reason}"
        )
        
        return (comp_action, reasoning)
