# hand_evaluator.py

from itertools import combinations

RANK_STR = "23456789TJQKA"
RANK_MAP = {r: i + 2 for i, r in enumerate(RANK_STR)}  # '2'->2, ..., 'T'->10, 'J'->11, 'Q'->12, 'K'->13, 'A'->14


def hand_rank(cards):
    """
    Evaluate the best 5-card poker hand from the given 7 cards.

    cards: list of strings like ['AH', 'KD', 'TC', '2S', ...] total 7 cards.

    returns: a tuple that can be compared. Higher is better.
    The tuple format: (category_rank, tie-break detail...)
    where category_rank:
        9 = Royal Flush
        8 = Straight Flush
        7 = Four of a Kind
        6 = Full House
        5 = Flush
        4 = Straight
        3 = Three of a Kind
        2 = Two Pair
        1 = One Pair
        0 = High Card
    """
    best = None
    # Generate all 5-card combinations from the 7 cards
    for five in combinations(cards, 5):
        score = hand_rank_5cards(five)
        if best is None or score > best:
            best = score
    return best


def hand_rank_5cards(cards):
    # cards: 5-card combination
    # Convert to ranks and suits
    ranks = sorted([RANK_MAP[c[0]] for c in cards], reverse=True)
    suits = [c[-1] for c in cards]

    # Count occurrences
    rank_counts = {}
    for r in ranks:
        rank_counts[r] = rank_counts.get(r, 0) + 1

    # Sort by frequency, then by rank
    # Example: for tie-breaking in 4-of-kind: (4 count rank), kicker
    freq_sorted = sorted(rank_counts.items(), key=lambda x: (x[1], x[0]), reverse=True)
    # freq_sorted is like [(rank, count), (rank, count), ...] sorted by count desc, then rank desc

    is_flush = len(set(suits)) == 1
    is_straight, top_card = check_straight(ranks)

    # Determine category
    # freq pattern:
    #   Four of a Kind: one rank with count=4
    #   Full House: pattern [3,2]
    #   Three of a Kind: pattern [3,1,1]
    #   Two Pair: pattern [2,2,1]
    #   One Pair: pattern [2,1,1,1]
    #   High Card: [1,1,1,1,1]

    counts = sorted((c for r, c in freq_sorted), reverse=True)  # just the counts in descending order

    # Check for Royal Flush (Straight Flush with highest card = Ace)
    if is_flush and is_straight and top_card == 14:
        # Royal flush
        return (9,)  # no need for more tie-break, royal is highest

    # Straight Flush
    if is_flush and is_straight:
        return (8, top_card)

    # Four of a kind
    if counts == [4, 1]:
        # freq_sorted[0] = (rank of 4,4), freq_sorted[1] = (kicker,1)
        four_rank = freq_sorted[0][0]
        kicker = freq_sorted[1][0]
        return (7, four_rank, kicker)

    # Full House [3,2]
    if counts == [3, 2]:
        three_rank = freq_sorted[0][0]
        pair_rank = freq_sorted[1][0]
        return (6, three_rank, pair_rank)

    # Flush
    if is_flush:
        # Tie-break by ranks sorted desc
        return (5,) + tuple(sorted(ranks, reverse=True))

    # Straight
    if is_straight:
        return (4, top_card)

    # Three of a Kind [3,1,1]
    if counts == [3, 1, 1]:
        three_rank = freq_sorted[0][0]
        kickers = sorted([r for r, c in freq_sorted[1:] if c == 1], reverse=True)
        return (3, three_rank) + tuple(kickers)

    # Two Pair [2,2,1]
    if counts == [2, 2, 1]:
        pair1 = freq_sorted[0][0]
        pair2 = freq_sorted[1][0]
        kicker = freq_sorted[2][0]
        # order pairs by rank (they already are, pair1 >= pair2)
        return (2, pair1, pair2, kicker)

    # One Pair [2,1,1,1]
    if counts == [2, 1, 1, 1]:
        pair = freq_sorted[0][0]
        kickers = sorted([freq_sorted[i][0] for i in range(1, 4)], reverse=True)
        return (1, pair) + tuple(kickers)

    # High Card [1,1,1,1,1]
    # Just sort by ranks
    return (0,) + tuple(sorted(ranks, reverse=True))


def check_straight(ranks):
    """
    Check if the given 5 ranks (already sorted descending) form a straight.
    Ranks might have duplicates (since we picked from 7 originally),
    so handle that as well. For 5-card sets, duplicates won't matter since it's a chosen combination.

    For 5 distinct ranks to form a straight, difference between max and min rank is 4.
    Special case: A-2-3-4-5 (A can be low).
    """
    # Because we might have combinations from 7-card sets, and we choose 5 distinct cards,
    # no duplicates appear in the chosen 5-card combination. If duplicates do occur, it means
    # that combination doesn't have 5 distinct ranks and isn't a standard 5-card hand.
    # But in hold'em 5-card chosen sets, duplicates in rank won't matter for straight checking.

    unique_ranks = sorted(set(ranks), reverse=True)
    if len(unique_ranks) < 5:
        return False, None
    # Since we have exactly 5 cards chosen, unique_ranks should be length 5.
    # Check if they form a sequence:
    high = unique_ranks[0]
    low = unique_ranks[-1]

    # Normal straight check:
    if high - low == 4 and len(unique_ranks) == 5:
        return True, high

    # Check A-2-3-4-5 straight:
    # ranks would be something like [14,5,4,3,2] for A-5 straight
    # If we have A and 2,3,4,5
    if set(unique_ranks) == {14, 5, 4, 3, 2}:
        # Here the top card is actually 5 in a 5-high straight
        return True, 5

    return False, None
