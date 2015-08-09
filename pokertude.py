import collections
import functools
import itertools
import random

VALUES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
SUITS = ['H', 'D', 'C', 'S']
FACE_TO_VALUE = {
    'J': 11,
    'Q': 12,
    'K': 13,
    'A': 14
}
VALUE_TO_FACE = dict(map(reversed, FACE_TO_VALUE.items()))
RANK_TO_STRING = {
    8: 'Straight flush',
    7: 'Four of a kind',
    6: 'Full house',
    5: 'Flush',
    4: 'Straight',
    3: 'Three of a kind',
    2: 'Two pair',
    1: 'Pair',
    0: 'High card'
}

# Functions to convert between face and value.
# A card's value is the numerical representation of its value. Ace is 14.
# A card's face is a human-readable string representing the card's value.
# It's often just the number, but can also be 'A', 'K', 'Q', or 'J'.
def face_to_value(face):
    if face in FACE_TO_VALUE:
        return FACE_TO_VALUE[face]
    else:
        return int(face)
def value_to_face(value):
    if value in VALUE_TO_FACE:
        return VALUE_TO_FACE[value]
    else:
        return str(value)

# Converts a tuple representing the rank of a hand (flush, pair, etc.)
# and all applicable kickers to a human readable string.
def rank_to_string(rank):
    hand_type = rank[0]
    kickers = tuple(map(value_to_face, rank[1:]))
    if hand_type == 8:
        return 'Straight flush (%s high)' % kickers
    elif hand_type == 7:
        return 'Four %ss (%s kicker)' % kickers
    elif hand_type == 6:
        return 'Full house (%ss over %ss)' % kickers
    elif hand_type == 5:
        return 'Flush (%s %s %s %s %s)' % kickers
    elif hand_type == 4:
        return 'Straight (%s high)' % kickers
    elif hand_type == 3:
        return 'Three %ss (%s, %s kickers)' % kickers
    elif hand_type == 2:
        return 'Two pair (%s and %s, %s kicker)' % kickers
    elif hand_type == 1:
        return 'Pair of %ss (%s, %s, %s kickers)' % kickers
    else:  # hand_type == 0
        return 'High card (%s %s %s %s %s)' % kickers

@functools.total_ordering
class Card:
    def __init__(self, value, suit):
        # e.g. Card(10, 'A')
        self.value = value
        self.suit = suit

    def __str__(self):
        return value_to_face(self.value) + self.suit

    def __repr__(self):
        return "%s%s" % (self.value, self.suit)

    def __eq__(self, other):
        return (self.value == other.value and self.suit == other.suit)

    def __lt__(self, other):
        return (self.value < other.value or
                (self.value == other.value and self.suit < other.suit))

# Precomputed 52-card deck.
ALL_CARDS = [Card(value, suit) for value in VALUES for suit in SUITS]

# A deck that can be shuffled and drawed from.
class Deck:
    def __init__(self):
        self.cards = ALL_CARDS[:]
        self.next_card_idx = 0
        self.shuffle()

    def draw(self):
        result = self.cards[self.next_card_idx]
        self.next_card_idx += 1
        return result

    def shuffle(self):
        random.shuffle(self.cards)
        self.next_card_idx = 0

# Analyzes games of Texas Hold'em.
class Analyzer:
    def __init__(self):
        self.reset()
        self.num_opponents = 1
        self.monte_carlo_rounds = 3000

    def reset(self):
        self.cards_left = ALL_CARDS[:]
        self.hole_cards = []
        self.community_cards = []

    def set_num_opponents(self, n):
        self.num_opponents = n

    def set_monte_carlo_rounds(self, n):
        self.monte_carlo_rounds = n

    # Sets the user's hole cards for analysis.
    def set_hole_cards(self, card1, card2):
        self.cards_left.remove(card1)
        self.cards_left.remove(card2)
        self.hole_cards.append(card1)
        self.hole_cards.append(card2)

    # Adds a community card to the analysis. Call three times for the flop,
    # once for the turn and river.
    def community_card(self, card):
        self.cards_left.remove(card)
        self.community_cards.append(card)

    # Determines the user's chance of winning given current hole cards and
    # community cards, assuming that all unseen cards (undealt community cards
    # and opponents' hole cards) are distributed randomly.
    def analyze(self):
        wins = 0
        ties = 0
        to_flop = 5 - len(self.community_cards)
        to_draw = to_flop + 2 * self.num_opponents

        total_rounds = self.monte_carlo_rounds
        total_opponent_hands = total_rounds * self.num_opponents

        # Counter of which hand types we're often beaten by.
        lossers = collections.Counter()

        # Monte Carlo simulation
        for _ in range(self.monte_carlo_rounds):
            # Draw a random combination of unseen cards (remaining community
            # cards + 2 hole cards per opponent)
            drawn_cards = random.sample(self.cards_left, to_draw)
            all_comms = self.community_cards + drawn_cards[:to_flop]
            my_ranking = best_rank(self.hole_cards + all_comms)

            # 2: win, 1: tie, 0: loss
            winner = 2
            for i in range(self.num_opponents):
                their_cards = drawn_cards[to_flop+2*i:to_flop+2*i+2]
                their_ranking = best_rank(their_cards + all_comms)
                if my_ranking < their_ranking:
                    winner = 0
                    lossers[their_ranking[0]] += 1
                elif my_ranking == their_ranking:
                    winner = min(winner, 1)
            if winner == 2:
                wins += 1
            elif winner == 1:
                ties += 1

        win_ratio = wins/total_rounds
        exp_winnings = win_ratio * (self.num_opponents+1) - 1
        print(
            "Wins: {0:.2f}% (Expected winnings: {1:.2f}%)"
            .format(100*win_ratio, 100*exp_winnings)
        )
        print("Ties: {0:.2f}%".format(ties/total_rounds*100))
        print("Sources of loss:")
        for rank, count in lossers.most_common():
            print(
                "{0}: {1:.2f}%"
                .format(RANK_TO_STRING[rank], count/total_opponent_hands*100)
            )
        print()

def hand_rank(cards):
    # Args:
    #   cards: a list of five Card objects
    # Returns:
    #   a tuple (ranking, kicker1, kicker2, ...)
    #   representing the ranking of the hand.
    # The kickers are not just the actual kickers, but include all values used
    # in comparing two hands in order of importance. e.g. for a full house,
    # kicker1 is the value of the triple, kicker2 is the value of the double.
    # Thus, the returned tuple can be compared lexicographically.

    # Sort cards from high to low
    cards.sort(reverse=True)

    # Useful information to rank the hand
    values = [c.value for c in cards]
    suits = [c.suit for c in cards]
    values_counter = collections.Counter(values)

    # High card
    ranking = (0,) + tuple(values)

    value_counts = sorted(values_counter.most_common(),
                          key=lambda x:tuple(reversed(x)),
                          reverse=True)
    values_by_freq = tuple(v for v,f in value_counts)

    if value_counts[0][1] == 4:
        # Four of a kind
        ranking = max(ranking, (7,) + values_by_freq)
    elif value_counts[0][1] == 3:
        if value_counts[1][1] == 2:
            # Full house
            ranking = max(ranking, (6,) + values_by_freq)
        else:
            # Three of a kind
            ranking = max(ranking, (3,) + values_by_freq)
    elif value_counts[0][1] == 2:
        if value_counts[1][1] == 2:
            # Two pair
            ranking = max(ranking, (2,) + values_by_freq)
        else:
            # One pair
            ranking = max(ranking, (1,) + values_by_freq)

    flush = len(set(suits)) == 1
    straight = all(v == nv+1 for v,nv in zip(values, values[1:]))
    if values == [14, 5, 4, 3, 2]:
        # Special case for 5-high straight
        straight = True
        values = [5, 4, 3, 2, 1]

    if flush and straight:
        ranking = max(ranking, (8, max(values)))
    elif flush:
        ranking = max(ranking, (5,) + tuple(values))
    elif straight:
        ranking = max(ranking, (4, max(values)))

    return ranking

def best_rank(cards):
    # Goes through all 5-card combinations of the list of cards, returning the
    # rank of the best combination.
    best = (-1,)
    for hand in itertools.combinations(cards, 5):
        best = max(best, hand_rank(list(hand)))
    return best

def parse_card(card_text):
    card_text = card_text.upper()
    value = face_to_value(card_text[:-1])
    face = card_text[-1]
    return Card(value, face)

def parse_cards(cards_text):
    cards = []
    for card_text in cards_text.split():
        cards.append(parse_card(card_text))
    return cards

def prompt(text):
    print(text)
    print('> ', end='')

if __name__ == '__main__':
    analyzer = Analyzer()
    while True:
        print('Starting new hand.')
        try:
            prompt('Hole cards?')
            h1, h2 = parse_cards(input())
            analyzer.set_hole_cards(h1, h2)
            prompt('# opponents?')
            analyzer.set_num_opponents(int(input()))
            analyzer.analyze()

            prompt('Flop?')
            h1, h2, h3 = parse_cards(input())
            for c in [h1, h2, h3]:
                analyzer.community_card(c)
            prompt('# opponents remaining?')
            analyzer.set_num_opponents(int(input()))
            analyzer.analyze()

            prompt('Turn?')
            c = parse_card(input())
            analyzer.community_card(c)
            prompt('# opponents remaining?')
            analyzer.set_num_opponents(int(input()))
            analyzer.analyze()

            prompt('River?')
            c = parse_card(input())
            analyzer.community_card(c)
            prompt('# opponents remaining?')
            analyzer.set_num_opponents(int(input()))
            analyzer.analyze()

        except ValueError:
            pass

        analyzer.reset()
