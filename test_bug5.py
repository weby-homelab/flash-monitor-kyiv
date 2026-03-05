def debug_search():
    current_slot_idx = 38 # 19:00 - 19:30
    slots = [True]*33 + [False]*7 + [True]*8
    # idx 33-39 are False (16:30 - 20:00)
    look_for_light = False
    target_idx = -1
    
    # 1. First loop: look for transition
    for i in range(current_slot_idx + 1, len(slots)):
        if slots[i] == look_for_light:
            if i > 0 and slots[i-1] != look_for_light:
                target_idx = i
                print("Found transition at", i)
                break
                
    # Since slot 39 is False and slot 38 is False, no transition is found here.
    
    # 2. Fallback loop: just find first occurrence
    if target_idx == -1:
        for i in range(current_slot_idx + 1, len(slots)):
            if slots[i] == look_for_light:
                target_idx = i
                print("Found fallback at", i)
                break
                
    print("target_idx:", target_idx)
    
debug_search()
