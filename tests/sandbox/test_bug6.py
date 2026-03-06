def debug_search():
    current_slot_idx = 38 # 19:00 - 19:30
    slots = [True]*33 + [False]*7 + [True]*8
    # idx 33-39 are False (16:30 - 20:00)
    look_for_light = False
    target_idx = -1
    
    for i in range(current_slot_idx + 1, len(slots)):
        if slots[i] == look_for_light:
            if i > 0 and slots[i-1] != look_for_light:
                target_idx = i
                print("Found transition at", i)
                break
                
    if target_idx == -1:
        if slots[current_slot_idx] != look_for_light:
            for i in range(current_slot_idx + 1, len(slots)):
                if slots[i] == look_for_light:
                    target_idx = i
                    print("Found fallback at", i)
                    break
    
    print("Final target_idx:", target_idx)
    
debug_search()
