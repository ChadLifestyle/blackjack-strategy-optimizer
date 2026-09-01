"""
Interactive CLI interface for the blackjack strategy optimizer.
Provides user-friendly terminal-based interaction for strategy analysis.
"""

from shoe import Shoe
from hand import Hand, DealerHand
from strategy import BasicStrategy, CompositionDependentStrategy, HybridStrategy
from ev_calculator import EVCalculator
from typing import List, Optional
import sys


class BlackjackUI:
    """Terminal-based user interface for strategy analysis."""
    
    def __init__(self):
        """Initialize the UI."""
        self.shoe = Shoe(num_decks=6)
        self.strategy_mode = "composition"  # composition, basic, or hybrid
        self.player_hand = None
        self.dealer_hand = None
        self.history = []
    
    def print_header(self):
        """Print application header."""
        print("\n" + "="*70)
        print("   BLACKJACK STRATEGY OPTIMIZER - Exact Shoe Tracking & EV Analysis")
        print("="*70 + "\n")
    
    def print_menu(self):
        """Print main menu."""
        print("\nMAIN MENU:")
        print("-" * 50)
        print("1. New Hand Analysis")
        print("2. Input Player Hand")
        print("3. Input Dealer Upcard")
        print("4. Update Shoe State")
        print("5. Get Strategy Recommendation")
        print("6. View Shoe Status")
        print("7. Change Strategy Mode")
        print("8. Reset Shoe")
        print("9. Help & Instructions")
        print("0. Exit")
        print("-" * 50)
    
    def card_string_to_value(self, card_str: str) -> Optional[int]:
        """
        Convert card string to value.
        
        Args:
            card_str: Card representation (2-9, T, J, Q, K, A)
            
        Returns:
            Card value (2-11), or None if invalid
        """
        card_str = card_str.strip().upper()
        
        if card_str.isdigit():
            val = int(card_str)
            if 2 <= val <= 9:
                return val
        elif card_str == 'T':
            return 10
        elif card_str in ['J', 'Q', 'K']:
            return 10
        elif card_str == 'A':
            return 11
        
        return None
    
    def value_to_card_string(self, value: int) -> str:
        """Convert card value to string representation."""
        if value == 11:
            return "A"
        elif 2 <= value <= 9:
            return str(value)
        elif value == 10:
            return "10"
        else:
            return "?"
    
    def input_cards(self, prompt: str) -> Optional[List[int]]:
        """
        Input multiple cards from user.
        
        Args:
            prompt: Prompt message
            
        Returns:
            List of card values, or None if invalid
        """
        print(f"\n{prompt}")
        print("Enter cards separated by spaces (2-9, T, J, Q, K, A)")
        print("Example: 5 10 A or K Q")
        
        card_input = input("> ").strip()
        
        if not card_input:
            print("No cards entered.")
            return None
        
        cards = []
        for card_str in card_input.split():
            value = self.card_string_to_value(card_str)
            if value is None:
                print(f"Invalid card: {card_str}")
                return None
            cards.append(value)
        
        return cards
    
    def input_single_card(self, prompt: str) -> Optional[int]:
        """Input a single card from user."""
        cards = self.input_cards(prompt)
        if cards and len(cards) == 1:
            return cards[0]
        print("Please enter exactly one card.")
        return None
    
    def display_hand(self, hand: Hand, label: str = "Hand"):
        """Display a hand nicely."""
        cards_str = " ".join(self.value_to_card_string(c) for c in hand.cards)
        print(f"\n{label}:")
        print(f"  Cards: {cards_str}")
        print(f"  Value: {hand.get_value()}")
        print(f"  Type: {hand.get_hand_type().value}")
        print(f"  Composition: {hand.get_hand_composition()}")
    
    def new_hand(self):
        """Start a new hand analysis."""
        print("\n" + "="*50)
        print("NEW HAND ANALYSIS")
        print("="*50)
        
        self.player_hand = None
        self.dealer_hand = None
        
        # Input player hand
        player_cards = self.input_cards("Input your hand:")
        if not player_cards:
            return
        
        self.player_hand = Hand(player_cards)
        self.display_hand(self.player_hand, "Your Hand")
        
        # Input dealer upcard
        dealer_upcard = self.input_single_card("Input dealer's upcard:")
        if dealer_upcard is None:
            return
        
        self.dealer_hand = DealerHand([dealer_upcard])
        print(f"\nDealer's Upcard: {self.value_to_card_string(dealer_upcard)}")
        
        # Get recommendation
        self.get_recommendation()
    
    def input_player_hand(self):
        """Manually input player hand."""
        cards = self.input_cards("Input your hand:")
        if cards:
            self.player_hand = Hand(cards)
            self.display_hand(self.player_hand, "Your Hand")
    
    def input_dealer_upcard(self):
        """Manually input dealer upcard."""
        upcard = self.input_single_card("Input dealer's upcard:")
        if upcard is not None:
            self.dealer_hand = DealerHand([upcard])
            print(f"Dealer's Upcard: {self.value_to_card_string(upcard)}")
    
    def update_shoe(self):
        """Update shoe based on cards dealt."""
        print("\n" + "="*50)
        print("UPDATE SHOE STATE")
        print("="*50)
        print("\nCards to mark as used/removed from shoe:")
        
        cards = self.input_cards("Enter cards dealt:")
        if not cards:
            return
        
        removed_count = 0
        for card in cards:
            if self.shoe.remove_card(card):
                removed_count += 1
            else:
                card_str = self.value_to_card_string(card)
                print(f"Warning: Could not remove {card_str} (not available in shoe)")
        
        print(f"\nRemoved {removed_count} cards from shoe")
        self.display_shoe_status()
    
    def display_shoe_status(self):
        """Display current shoe status."""
        print("\n" + "-"*50)
        print("SHOE STATUS:")
        print("-"*50)
        
        state = self.shoe.get_state_vector()
        remaining = self.shoe.get_remaining_cards()
        penetration = self.shoe.get_penetration()
        
        print(f"Total Cards Remaining: {remaining} / {self.shoe.total_cards}")
        print(f"Penetration: {penetration*100:.1f}%")
        print(f"Decks Remaining: {remaining/52:.2f}")
        
        print("\nCard Distribution:")
        for value in range(2, 12):
            count = state[value]
            card_str = self.value_to_card_string(value)
            bar = "█" * count + "░" * (self.shoe.num_decks * 4 - count)
            print(f"  {card_str:2s}: {count:2d} cards  {bar}")
    
    def get_recommendation(self):
        """Get strategy recommendation."""
        if self.player_hand is None or self.dealer_hand is None:
            print("\nError: Please input player hand and dealer upcard first.")
            return
        
        print("\n" + "="*50)
        print("STRATEGY RECOMMENDATION")
        print("="*50)
        
        # Select strategy
        if self.strategy_mode == "basic":
            strategy = BasicStrategy()
        elif self.strategy_mode == "composition":
            strategy = CompositionDependentStrategy()
        else:  # hybrid
            strategy = HybridStrategy()
        
        action, reasoning = strategy.get_recommendation(
            self.player_hand,
            self.dealer_hand.get_upcard(),
            self.shoe
        )
        
        print(f"\nStrategy Mode: {self.strategy_mode.upper()}")
        print(f"\n>>> RECOMMENDED ACTION: {action.upper()} <<<")
        print(f"\nReasoning:\n{reasoning}")
        
        # If composition-dependent, show EV details
        if self.strategy_mode in ["composition", "hybrid"]:
            self.show_ev_details()
    
    def show_ev_details(self):
        """Show detailed EV calculations."""
        print("\n" + "-"*50)
        print("EXPECTED VALUE ANALYSIS:")
        print("-"*50)
        
        calculator = EVCalculator(self.shoe, self.dealer_hand.get_upcard())
        ev_dict = calculator.calculate_player_ev(self.player_hand, self.dealer_hand)
        
        print("\nEV by Action:")
        for action in sorted(ev_dict.keys(), 
                            key=lambda a: ev_dict[a], reverse=True):
            ev = ev_dict[action]
            print(f"  {action:10s}: {ev:8.4f}")
    
    def change_strategy(self):
        """Change strategy mode."""
        print("\n" + "="*50)
        print("SELECT STRATEGY MODE")
        print("="*50)
        print("1. Composition-Dependent (EV-based, most accurate)")
        print("2. Basic Strategy (traditional, composition-independent)")
        print("3. Hybrid (basic strategy with EV adjustments)")
        
        choice = input("\nChoice (1-3): ").strip()
        
        if choice == "1":
            self.strategy_mode = "composition"
            print("✓ Strategy mode: Composition-Dependent")
        elif choice == "2":
            self.strategy_mode = "basic"
            print("✓ Strategy mode: Basic Strategy")
        elif choice == "3":
            self.strategy_mode = "hybrid"
            print("✓ Strategy mode: Hybrid")
        else:
            print("Invalid choice.")
    
    def show_help(self):
        """Show help and instructions."""
        help_text = """
╔════════════════════════════════════════════════════════════════════╗
║           BLACKJACK STRATEGY OPTIMIZER - USER GUIDE               ║
╚════════════════════════════════════════════════════════════════════╝

OVERVIEW:
This tool analyzes blackjack hands using exact shoe tracking and 
composition-dependent strategy optimization. It calculates the 
mathematically optimal move based on your specific cards and the 
remaining shoe composition.

KEY FEATURES:

1. EXACT SHOE TRACKING
   - Maintains precise count of remaining cards
   - Tracks penetration (% of deck dealt)
   - Updates dynamically as cards are played

2. COMPOSITION-DEPENDENT ANALYSIS
   - Doesn't just look at hand totals (e.g., 16)
   - Considers the SPECIFIC cards (e.g., 10+6 vs 5+5+6)
   - Different compositions = different optimal plays

3. EXPECTED VALUE (EV) CALCULATION
   - Computes EV for each possible action
   - Hit, Stand, Double, Split, Surrender
   - Shows which action maximizes long-term profit

STRATEGY MODES:

• COMPOSITION-DEPENDENT (Recommended)
  Most accurate, uses EV calculations based on exact shoe state
  
• BASIC STRATEGY (Classic)
  Traditional approach, works well but ignores shoe composition
  
• HYBRID
  Uses basic strategy with EV-based adjustments when they differ

USAGE WORKFLOW:

1. Start "New Hand Analysis"
2. Input your cards (e.g., "5 10" for five and ten)
3. Input dealer's upcard (e.g., "K" for king)
4. Get recommendation (shows best move and EV analysis)
5. As cards are played, "Update Shoe State" to track them
6. Analysis updates automatically with new shoe composition

CARD NOTATION:
  2-9  : Number cards
  T    : Ten
  J,Q,K: Face cards (all count as 10)
  A    : Ace

EXAMPLE SESSION:

  > New Hand Analysis
  > Input cards: 5 10        (Your hand: 5 and 10 = 15)
  > Dealer upcard: 6        (Dealer showing 6)
  > Get Recommendation      (System: STAND - best move)
  > Update Shoe State
  > Cards dealt: 5 10 6 K 7 (Mark these as played)
  > View Shoe Status        (See updated remaining cards)

TIPS:
• The more cards dealt, the more accurate the analysis
• Update shoe regularly for best recommendations
• EV values range from -1.0 (certain loss) to +1.0 (certain win)
• Composition matters! Same total can have different EV
"""
        print(help_text)
    
    def run(self):
        """Main UI loop."""
        self.print_header()
        
        while True:
            self.print_menu()
            choice = input("Enter choice: ").strip()
            
            if choice == "1":
                self.new_hand()
            elif choice == "2":
                self.input_player_hand()
            elif choice == "3":
                self.input_dealer_upcard()
            elif choice == "4":
                self.update_shoe()
            elif choice == "5":
                self.get_recommendation()
            elif choice == "6":
                self.display_shoe_status()
            elif choice == "7":
                self.change_strategy()
            elif choice == "8":
                self.shoe.reset_shoe()
                print("\n✓ Shoe reset to initial state")
            elif choice == "9":
                self.show_help()
            elif choice == "0":
                print("\nThank you for using Blackjack Strategy Optimizer!")
                sys.exit(0)
            else:
                print("Invalid choice. Please try again.")


def main():
    """Entry point."""
    try:
        ui = BlackjackUI()
        ui.run()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
