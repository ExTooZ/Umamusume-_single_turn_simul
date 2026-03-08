# %% imports
from dataclasses import dataclass
from itertools import combinations

import math
# %% main 

@dataclass(frozen=True) # cleaner way to initialize the object (it doesn't use innit function)
class SupportCard:
    name: str
    card_type: str      # "speed", "wit", "pal", "power", "stamina"
    fb: float           # friendship bonus as decimal (0.25 for 25%)
    me: float           # mood effect as decimal (0.30 for 30%)
    te: float           # training effectiveness as decimal (0.15 for 15%)
    bonus: float        # main-stat bonus for THIS training (speed bonus if speed training)
    sp: float           # special priority (your SP)

    def appear_prob(self) -> float:
        # Your simplified model:
        # prob = (SP + 100) / (550 + SP)
        return (self.sp + 100.0) / (550.0 + self.sp)


# ---------- Helpers ----------
FL_MAP = {1: 8, 2: 9, 3: 10, 4: 11, 5: 12}

def round_down(x: float, decimals: int = 2) -> float:
    factor = 10 ** decimals
    return math.floor(x * factor) / factor

# gets all the possible subsets
def all_subsets(items):
    # yields all subsets (as tuples)
    results = []
    items = list(items)
    print(len(items))
    for r in range(len(items) + 1):                 # + 1 for all subsets of that size 
        for comb in combinations(items, r):         # combination finds all the combination of r items with on and off states (6 items mean 2^6 configurations)
            results.append(comb)                    # you can use yield instead of return because it immediately appends to a list without initializing the list
    return results


# ---------- Speed gain model ----------
def speed_gain(cards_in_facility, FL_level: int, friendship,mood) -> float:
    if FL_level not in FL_MAP:
        raise ValueError("FL must be an integer in {1,2,3,4,5}")

    FL = FL_MAP[FL_level]
    n = len(cards_in_facility)

    total_bonus = sum(c.bonus for c in cards_in_facility)     # speed bonus sum
    total_me    = sum(c.me for c in cards_in_facility)
    total_te    = sum(c.te for c in cards_in_facility)
    if friendship == True:
        total_fb = sum(c.fb for c in cards_in_facility if c.card_type == "speed")
    elif friendship == False:
        total_fb = 0
        # FB applies ONLY for speed cards during speed training (your rule)
    if mood == "great":
        gain = (
            (FL + total_bonus)
            * (1 + 0.2 * (1 + total_me))
            * (1 + total_te)
            * (1 + total_fb)
            * (1 + 0.05 * n)
        )
    elif mood == "good":
        gain = (
            (FL + total_bonus)
            * (1 + 0.1 * (1 + total_me))
            * (1 + total_te)
            * (1 + total_fb)
            * (1 + 0.05 * n)
        )
    elif mood == "normal":
        gain = (
            (FL + total_bonus)
            * (1 + 0.0 * (1 + total_me))
            * (1 + total_te)
            * (1 + total_fb)
            * (1 + 0.05 * n)
        )
    
    return gain

# training without friendship bonus

def expected_speed_gain(deck, FL_level: int,friendship, mood) -> float:
    """
    Expected gain over all appearance subsets.
    Assumes each card appears independently with appear_prob().
    """
    ev = 0.0
    for subset in all_subsets(deck):
        # probability of exactly this subset appearing
        p = 1.0
        # calculates probability of every outcome
        for c in deck:
            p *= c.appear_prob() if c in subset else (1.0 - c.appear_prob())
        ev += p * speed_gain(subset, FL_level,friendship, mood)
    return ev

# ---------- Data model ----------
# ---------- Your cards (Speed training: bonus=Speed Bonus) ----------
matikanefukukitaru = SupportCard("Matikanefukukitaru", "speed", fb=0.2, me=0.45, te=0.10, bonus=0.0, sp=0)
mihono_bourbon= SupportCard("Mihono Bourbon", "wit",  fb=0.20, me=0.40, te=0.05, bonus=1.0, sp=20)
kitasan_black = SupportCard("Kitasan Black", "speed", fb=0.25, me=0.30, te=0.15, bonus=0.0, sp=100)
sweep_tosho   = SupportCard("Sweep Tosho",   "speed", fb=0.30, me=0.40, te=0.10, bonus=0.0, sp=50)
riko          = SupportCard("Riko",          "pal",   fb=0.00, me=0.00, te=0.10, bonus=0.0, sp=0)
fine_motion   = SupportCard("Fine Motion",   "wit",   fb=0.35, me=0.30, te=0.15, bonus=0.0, sp=35)
marvelous     = SupportCard("Marvelous",     "wit",   fb=0.35, me=0.30, te=0.00, bonus=0.0, sp=50)
daiwa         = SupportCard("Daiwa Scarlet", "wit",   fb=0.30, me=0.55, te=0.00, bonus=0.0, sp=50)
eishin_flash  = SupportCard("Eishin Flash",  "speed", fb=0.20, me=0.65, te=0.00, bonus=1.0, sp=35)
biko_pegasus  = SupportCard("Biko Pegasus",  "speed", fb=0.25, me=0.00, te=0.20, bonus=1.0, sp=55)
nice_nature   = SupportCard("Nice Nature",   "wit",   fb=0.25, me=0.00, te=0.15, bonus=0.0, sp=35)
king_halo     = SupportCard("King Halo",     "speed", fb=0.20, me=0.30, te=0.05, bonus=1.0, sp=60)


deck = [riko, kitasan_black, king_halo, fine_motion, marvelous, nice_nature]
def best_worst_speed(deck, FL_level: int, growth: float,friendship,mood):
    best_gain  = speed_gain(deck, FL_level,friendship, mood) * (1 + growth/100)           # all appear
    worst_gain = speed_gain((), FL_level,friendship, mood)   * (1 + growth/100)           # none appear (empty subset)
    ev_gain    = expected_speed_gain(deck, FL_level,friendship, mood) * (1 + growth/100)  # expected over all subsets
    return best_gain, worst_gain, ev_gain

def get_ev_from_fail(expected_value,failure_rate):
    success_rate = 1 - failure_rate/100
    ev = expected_value * success_rate
    return ev

# quantifying skill points into speed
# we approximate using some bullshit math in tablet and based on uma simulator
def skill_to_speed(skill_points):
    weight = 2/15                                  # base on an approximation on uma simulator (notes in tablet)
    speed = skill_points * weight
    return speed
# Example run
# %% run prints
# ============== Parameters ==============  
FL_level = 5
growth = 20         # in percentage
mood = "great"
friendship = True
best, worst, ev = best_worst_speed(deck, FL_level, growth,friendship,mood)

print("Best-case (all appear):", round_down(best, 2))
print("Worst-case (none appear):", round_down(worst, 2))
print("Expected gain (EV):", round_down(ev, 2))

# We can compare this with the expected outcome of the speed 
print("Expected gains = ", get_ev_from_fail(ev,20))

# False means you shouldn't train and True means you should train
def should_train(expected_value, skill_points,failure_rate) -> bool:
    if 13 + skill_to_speed(skill_points) > get_ev_from_fail(expected_value,failure_rate):
        return "You shouldn't train. Instead just race or rest"
    else:
        return "You should train or just rest"
        
# FL_MAP2 = {1: 20, 2: 21, 3: 22, 4: 23, 5: 24}

# def energy_to_stat(FL_level:int):
#     speed_energy = FL_MAP2[FL_level]
#     energy_stat =  ev/speed_energy
#     ev_energy = 70 * 0.25 + 50 * 0.625 + 30 * 12.5
#     ev_energy_rest = ev/ev_energy
#     total_race_speed = 2/15 * 60 + 13
#     ev_energy_race = total_race_speed/15
#     return ev_energy_rest,energy_stat, ev_energy_race

# calculates the loss if u had mood good or great. It also calculates how many turns you need for great mood to be worth it
def recreation(FL_level,mood):
    if mood == "good":
        expected_diff = expected_speed_gain(deck,FL_level,friendship,mood="great") - expected_speed_gain(deck,FL_level,friendship,mood)
        print("current mood is good")
        return f"you are losing {expected_diff} stats per turn which can be equalized after {ev/expected_diff} turns"
    if mood == "normal":
        expected_diff = expected_speed_gain(deck,FL_level,friendship,mood="great") - expected_speed_gain(deck,FL_level,friendship,mood)
        expected_diff2 = expected_speed_gain(deck,FL_level,friendship,mood="good") - expected_speed_gain(deck,FL_level,friendship,mood)
        return f"you are losing {expected_diff} stats per turn if you had great mood which can be equalized after {ev/expected_diff} turns and {expected_diff2} stats per turn if you had good mood which can be equalized after {ev/expected_diff2} turns"
print(recreation(5,"good"))
print(should_train(ev, 50, 20))
# print(energy_to_stat(FL_level=5))


# use a random generator to make different probability of a 10 run with failure rate and see its outcome and how it changes
# %%
