import random
from handevaluator import hand_rank
from deck import RANKS

def bot_decision(bot_player, community_cards, call_amount, pot_size, round_name):
    full_hand = bot_player.hole_cards + community_cards
    stack = bot_player.stack
    num_cards = len(full_hand)

    if num_cards < 5:
        return preflop_decision(bot_player, community_cards, call_amount, pot_size, round_name)
    else:
        strength_tuple = hand_rank(full_hand)
        equity = estimate_equity_from_rank(strength_tuple)
        return postflop_decision(bot_player, equity, call_amount, pot_size, round_name)

def estimate_equity_from_rank(rank_tuple):
    category = rank_tuple[0]
    if category == 9:
        return 0.99
    elif category == 8:
        return 0.95
    elif category == 7:
        return 0.92
    elif category == 6:
        return 0.85
    elif category == 5:
        return 0.75
    elif category == 4:
        return 0.65
    elif category == 3:
        return 0.55
    elif category == 2:
        return 0.45
    elif category == 1:
        return 0.35
    else:
        return 0.25

def preflop_decision(bot_player, community_cards, call_amount, pot_size, round_name):
    hole_cards = bot_player.hole_cards
    ranks = sorted([c[0] for c in hole_cards], key=lambda x: RANKS.index(x))
    hole_str = "".join(ranks)
    premium = hole_str in ["AA", "KK", "QQ", "JJ"]
    good = hole_str in ["TT","99","88","AK","AQ","AJ","KQ"]
    mid_pairs = ["77","66","55","44","33","22"]
    medium = hole_str in mid_pairs
    weak = not(premium or good or medium)

    stack = bot_player.stack

    if call_amount == 0:
        if premium:
            raise_amt = min(stack, max(20, pot_size))
            return ('bet', raise_amt)
        elif good:
            if random.random() < 0.9:
                raise_amt = min(stack, max(15, pot_size//2))
                return ('bet', raise_amt)
            else:
                return ('check', 0)
        elif medium:
            if random.random() < 0.6:
                raise_amt = min(stack, max(10, pot_size//3))
                return ('bet', raise_amt)
            else:
                return ('check', 0)
        else:
            if random.random() < 0.3:
                raise_amt = min(stack, max(10, pot_size//4))
                return ('bet', raise_amt)
            return ('check', 0)
    else:
        pot_odds = call_amount / float(pot_size + call_amount)
        if premium:
            if random.random() < 0.7:
                raise_amt = min(stack, call_amount * 4)
                return ('raise', raise_amt)
            else:
                return ('call', call_amount)
        elif good:
            if pot_odds < 0.5:
                if random.random() < 0.5:
                    raise_amt = min(stack, call_amount * 3)
                    return ('raise', raise_amt)
                else:
                    return ('call', call_amount)
            else:
                if random.random() < 0.5:
                    return ('call', call_amount)
                else:
                    return ('fold', 0)
        elif medium:
            if pot_odds < 0.6:
                if random.random() < 0.3:
                    raise_amt = min(stack, call_amount * 2)
                    return ('raise', raise_amt)
                else:
                    return ('call', call_amount)
            else:
                if random.random() < 0.4:
                    return ('call', call_amount)
                else:
                    return ('fold', 0)
        else:
            if pot_odds < 0.5 and random.random() < 0.2:
                return ('call', call_amount)
            elif random.random() < 0.15:
                raise_amt = min(stack, call_amount * 2)
                return ('raise', raise_amt)
            else:
                return ('fold', 0)

def postflop_decision(bot_player, equity, call_amount, pot_size, round_name):
    stack = bot_player.stack
    if pot_size + call_amount > 0:
        pot_odds = call_amount / float(pot_size + call_amount)
    else:
        pot_odds = 0

    if call_amount == 0:
        if equity > 0.7:
            bet_amt = min(stack, max(20, int(pot_size*0.8)))
            return ('bet', bet_amt)
        elif equity > 0.5:
            if random.random() < 0.7:
                bet_amt = min(stack, max(15, pot_size//2))
                return ('bet', bet_amt)
            else:
                return ('check', 0)
        else:
            if random.random() < 0.4:
                bet_amt = min(stack, max(10, pot_size//3))
                return ('bet', bet_amt)
            return ('check', 0)
    else:
        if equity > pot_odds:
            if equity > 0.8:
                if random.random() < 0.6:
                    raise_amt = min(stack, max(20, call_amount * 3))
                    return ('raise', raise_amt)
                else:
                    return ('call', call_amount)
            elif equity > 0.5:
                if random.random() < 0.4:
                    raise_amt = min(stack, max(15, call_amount * 2))
                    return ('raise', raise_amt)
                return ('call', call_amount)
            else:
                if random.random() < 0.2:
                    raise_amt = min(stack, max(15, call_amount * 2))
                    return ('raise', raise_amt)
                return ('call', call_amount)
        else:
            if random.random() < 0.3:
                return ('call', call_amount)
            elif random.random() < 0.15:
                raise_amt = min(stack, max(15, call_amount * 2))
                return ('raise', raise_amt)
            else:
                return ('fold', 0)
