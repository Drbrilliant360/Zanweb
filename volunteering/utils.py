RANKS = [
    ('newcomer', 0),
    ('active', 40),
    ('elite', 100),
    ('platinum', 140),
]


def get_rank_info(total_hours):
    for i, (name, threshold) in enumerate(RANKS):
        if total_hours < threshold:
            if i == 0:
                return {'rank': name, 'percent_to_next_rank': 0}
            rank = RANKS[i - 1][0]
            lower = RANKS[i - 1][1]
            range_size = threshold - lower
            progress = total_hours - lower
            percent = int((progress / range_size) * 100) if range_size > 0 else 0
            return {'rank': rank, 'percent_to_next_rank': min(percent, 99)}

    return {'rank': RANKS[-1][0], 'percent_to_next_rank': 100}
