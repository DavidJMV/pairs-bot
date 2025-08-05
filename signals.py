def generate_signal(z, position, entry_threshold=2.0, exit_threshold=0.5, max_threshold=4.0):
    """
    z: latest z-score (float)
    position: current position (-1: short spread, 0: flat, +1: long spread)
    entry_threshold: z-score threshold for entering positions
    exit_threshold: z-score threshold for exiting positions  
    max_threshold: emergency exit threshold
    returns: new_position, action
    action: 'enter_long', 'enter_short', 'exit', or None
    """
    # Exit conditions when in a position
    if position != 0:
        # Emergency exit if z-score moves too far against us
        if abs(z) > max_threshold:
            return 0, 'exit'
        
        # Normal exit when z-score returns toward mean
        if abs(z) < exit_threshold:
            return 0, 'exit'

    # Entry conditions when flat
    if position == 0:
        if z > entry_threshold:
            return -1, 'enter_short'  # short SHEL, long BP
        if z < -entry_threshold:
            return +1, 'enter_long'   # long SHEL, short BP

    # Otherwise, hold current position
    return position, None
