from generate_text_report import format_slot_time, get_all_intervals, generate_day_block
import json

slots = [True] * 45 + [False] * 51
intervals = get_all_intervals(slots)
cfg = {'ui': {'icons': {'on': '🔆', 'off': '✖️'}}}
print("--- TODAY ---")
print(generate_day_block(True, intervals, cfg))
print("--- TOMORROW ---")
print(generate_day_block(False, intervals, cfg))
