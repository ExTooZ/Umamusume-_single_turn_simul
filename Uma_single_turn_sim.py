# %% imports
from dataclasses import dataclass
from itertools import combinations
import matplotlib.pyplot as plt
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
        # prob = (SP + 100) / (550 + SP)
        return (self.sp + 100.0) / (550.0 + self.sp)


# Facility level base stats
FL_MAP = {1: 8, 2: 9, 3: 10, 4: 11, 5: 12}
Mood_MAP = {"great": 0.2, "good": 0.1, "normal": 0.0}
def round_down(x: float, decimals: int = 2) -> float:
    factor = 10 ** decimals
    return math.floor(x * factor) / factor

# gets all the possible subsets
def all_subsets(items: list):
    # yields all subsets (as tuples)
    results = []                           
    for r in range(len(items) + 1):                 # + 1 for all subsets of that size 
        for comb in combinations(items, r):         # combination finds all the combination of r items with on and off states (6 items mean 2^6 configurations)
            results.append(comb)                    # you can use yield instead of return because it immediately appends to a list without initializing the list
    return results


# ---------- Speed gain model with FB and without FB ----------
def speed_gain(cards_in_facility: list, FL_level: int, friendship: bool, mood) -> float:
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
    gain = (
        (FL + total_bonus)
        * (1 + Mood_MAP[mood] * (1 + total_me))
        * (1 + total_te)
        * (1 + total_fb)
        * (1 + 0.05 * n)
    )
    
    return gain


# Calculates the expected value of said stat
def expected_speed_gain(deck, FL_level: int,friendship, mood) -> float:
    """
    Expected gain over all appearance subsets.
    Assumes each card appears independently with appear_prob().
    """
    ev = 0.0
    for subset in all_subsets(deck):
        current = subset
        # probability of exactly this subset appearing
        p = 1.0
        # calculates probability of every outcome
        for c in deck:
            p *= c.appear_prob() if c in subset else (1.0 - c.appear_prob())
        ev += p * speed_gain(subset, FL_level,friendship, mood)
    return ev

# Gets the probability of each possible combination and returns them as a dictionary
def probability_outcome(deck):
    outcomes = {}
    for subset in all_subsets(deck):
        # probability of exactly this subset appearing
        p = 1.0
        # calculates probability of every outcome
        for c in deck:
            p *= c.appear_prob() if c in subset else (1.0 - c.appear_prob())
        tupple_names = tuple(card.name for card in subset)                  # Set the tupple name as a tuple
        outcomes[tupple_names] = p                                          # Set the outcome to the probability 
    return outcomes
# ---------- Data model (More cards to be added) ----------
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


deck = [riko, kitasan_black, sweep_tosho, fine_motion, marvelous, nice_nature]
# Get all the values for best to worsrt to expected gain
def best_worst_speed(deck, FL_level: int, growth: float,friendship,mood):
    best_gain  = speed_gain(deck, FL_level,friendship, mood) * (1 + growth/100)           # all appear
    worst_gain = speed_gain((), FL_level,friendship, mood)   * (1 + growth/100)           # none appear (empty subset)
    ev_gain    = expected_speed_gain(deck, FL_level,friendship, mood) * (1 + growth/100)  # expected over all subsets
    return best_gain, worst_gain, ev_gain

# Calculate the expected value from failure rate
def get_ev_from_fail(expected_value,failure_rate):
    success_rate = 1 - failure_rate/100
    failure_penalty = 5
    ev = expected_value * success_rate + (failure_rate/100) * failure_penalty
    return ev
# Quantifying skill points into speed
# We approximate using some math in tablet and based on uma simulator
def skill_to_speed(skill_points):
    weight = 1/1.72                                  # base on an approximation on uma simulator (notes in tablet)
    speed = skill_points * weight
    return speed

# Determines whether or not you should train or rather rest or race
# Used to choose the best option for the current turn
# Rule of thumb is 2 x failure rate < stats gain to be worth it
# Now the rule of thumb is applied for compraing race stats to actual stats
# On average it is about 14% failure rate for the threshold on G1 races and 27% for races that gives 50 SP
def should_train(expected_value, skill_points,failure_rate) -> bool:
    if 13 + skill_to_speed(skill_points) > 2 * get_ev_from_fail(expected_value,failure_rate): # Here we use 2.5 to simulate power getting added
        return "You shouldn't train. Instead just race or rest"
    else:
        return "You should train or just rest"
        

# Calculates the loss if you had mood good or great. It also calculates how many turns you need for great mood to be worth it
def recreation(FL_level,mood):
    if mood == "good":
        expected_diff = expected_speed_gain(deck,FL_level,friendship,mood="great") - expected_speed_gain(deck,FL_level,friendship,mood)
        print("current mood is good")
        return f"you are losing {expected_diff} stats per turn which can be equalized after {ev/expected_diff} turns"
    if mood == "normal":
        expected_diff = expected_speed_gain(deck,FL_level,friendship,mood="great") - expected_speed_gain(deck,FL_level,friendship,mood)
        expected_diff2 = expected_speed_gain(deck,FL_level,friendship,mood="good") - expected_speed_gain(deck,FL_level,friendship,mood)
        return f"you are losing {expected_diff} stats per turn if you had great mood which can be equalized after {ev/expected_diff} turns and {expected_diff2} stats per turn if you had good mood which can be equalized after {ev/expected_diff2} turns"
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
print(should_train(ev, 50, 26))

print(recreation(5,mood))
#%% Side preojects
# ============== Multiple Support Cards Probability ============= 
probs = probability_outcome(deck)
print(probs)
count_dist = {}
for subset,p in probs.items():
    n = len(subset)
    count_dist[n] = count_dist.get(n,0) + p     # .get returns 0 if it doesn't exists else it returns the value of n
print(count_dist)

# Plotting
plt.bar(count_dist.keys(), count_dist.values())
plt.xlabel("number of cards")
plt.ylabel("chance of success")
plt.show()

# %%
