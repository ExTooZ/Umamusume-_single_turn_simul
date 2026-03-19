# Umamusume-_single_turn_simul
An attempt to find the best option to do during training in umamusume. Knowing how many variables are available, this simulation tries to only take the most relevant variables into account
The simulation is not meant to replace human decisions. The rule of thumb for decision making is sufficient to enjoy the game to its fullest.

Note: The simulation is only applicable to unity cup scenario since MANT has a different racing system than the others

## How to use
Print functions are already given in the python file. The main function is, however, the should_train function. It gives a estimation on whether or not the trainer has to train or rest/race. The function takes an average of 13 stat points and added to the converted skill points to then be compared to the rule of thumb. 


## Recreation Function
The recreation function is however useful to see whether or not a normal recreation is worth it knowing how many turns is left. The function assumes the turns doesn't have any rests. A good assumption of a rest every 3 turns is sufficient to reenact the game.
