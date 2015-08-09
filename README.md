# Pokertude

Analyzes poker odds, assuming (and this is a very bad assumption) that unseen cards are uniformly picked from the remaining cards in the deck.

## Example session

```
Starting new hand.
Hole cards?
> ad ac
# opponents?
> 1
Wins: 84.77% (Expected winnings: 69.53%)
Ties: 0.50%
Sources of loss:
Straight: 4.73%
Two pair: 3.00%
Three of a kind: 2.67%
Full house: 2.57%
Flush: 1.57%
Four of a kind: 0.10%
Straight flush: 0.10%

Flop?
> 2d kh 5h
# opponents remaining?
> 1
Wins: 86.30% (Expected winnings: 72.60%)
Ties: 0.13%
Sources of loss:
Two pair: 4.10%
Flush: 3.43%
Three of a kind: 2.83%
Straight: 1.90%
Full house: 1.27%
Four of a kind: 0.03%

Turn?
> 4h
# opponents remaining?
> 1
Wins: 74.60% (Expected winnings: 49.20%)
Ties: 0.67%
Sources of loss:
Flush: 11.20%
Two pair: 5.57%
Straight: 5.37%
Three of a kind: 2.10%
Full house: 0.43%
Straight flush: 0.07%

River?
> 2h
# opponents remaining?
> 1
Wins: 54.03% (Expected winnings: 8.07%)
Ties: 0.00%
Sources of loss:
Flush: 36.77%
Three of a kind: 4.57%
Full house: 3.13%
Straight: 1.13%
Straight flush: 0.27%
Four of a kind: 0.10%
```
