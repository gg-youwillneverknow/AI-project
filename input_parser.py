import re, sys
import random

#assumptions, problem representation, and initial definitions
pattern = r'((?:(?:High|Low);){3}[ENW]);((?:(?:High|Low);){2}(?:High|Low))'
lowloop_direction = "N"
states = []
def populate_states():
	global states
	for i,a in enumerate(["High", "Low"]):
		for j,b in enumerate(["High", "Low"]):
			for k,c in enumerate(["High", "Low"]):
				state= a+";"+b+";"+c
				states+=[state]
def actions(state):
	if state == "Low;Low;Low":
		return next_loop()
	else:
		return ["N","E","W"]
def next_loop():
	global lowloop_direction
	if lowloop_direction=="N":
		lowloop_direction="E"
	elif lowloop_direction=="E":
		lowloop_direction="W"
	else:
		lowloop_direction="N"
	return [lowloop_direction]
def cost_function(state,action):
	return 1

#if do_calc, take 0th of argv as filename of input data and compute and save off serialization/json files
#else, take argv as filenames of [transition_table, expected_costs, policies]
def main(argv, do_calc):
	populate_states()
	transition_table = None
	expected_costs = {}
	policies = {}
	#process input files, either by calculating off of data or reading pre-computations
	#result: populated transition_table, expected_costs, and policies
	if do_calc:
		traffic_data_file = open(argv[0], "r")
		transition_table = make_transition_table(traffic_data_file)
		#HERE: save off transition_table as json object
				
		#run PIA to compute expected costs and optimal policy
		has_changed = True
		global states
		while(has_changed):
			has_changed = False
			for state in states:
				policy,min = value_iteration(state,transition_table,expected_costs)
				if expected_costs.get(state,0)!=min:
					expected_costs[state]=min
					policies[state]=policy
					has_changed = True
		print(policies)
		print("")
		print(expected_costs)
		#HERE: save off results (expected_costs, policies) as JSON for next time
		
	else:
		#HERE: json load in the transition_table, expected_costs, and policies
	
	#next, run one simulation/trace from each initial state
	tracerun_MDP(transition_table, policies, cost_function)

def make_transition_table(f):
	dict={}
	#do some re and print the output, let's say 5 times

	for i,s in enumerate(list(f.readlines())):
		non_initial = []
		#print(s, end='')
		m = re.search(pattern, s)
		#print(m.group(1) + " " + m.group(2))
		if m.group(1) not in dict:
			dict[m.group(1)] = {m.group(2):1}
			#print(dict)
			#return 0
		else:
			if m.group(2) in dict[m.group(1)]:
				dict[m.group(1)][m.group(2)]+=1
				#print(dict)
				#return 0
			elif m.group(2) not in dict[m.group(1)]:
				dict[m.group(1)][m.group(2)]=1
			
	#print("the number of initial states: ",len(dict))
	l = [len(key) for key in dict]
	#print(l)
	reachable = []
	for key in dict:
		for second_key in dict[key]:
			for i,d in enumerate([";W",';E',";N"]):
				if second_key+d not in dict:
					non_initial += [second_key+d]
			reachable+=[second_key]
	#print(set(reachable))
	#print(set(non_initial))
	#print(dict)
	
	for state in dict: 

		total=sum([dict[state][final_state] for final_state in dict[state]])
		for final_state in dict[state]:
			dict[state][final_state] = dict[state][final_state] / total
	print(dict)
	return dict

#perform value- and policy-iteration
def value_iteration(state,transition_table,expected_costs):
	min = False
	policy = False
	for i,action in enumerate(actions(state)):
		if state == "Low;Low;Low":
			return action,0
		value = cost_function(state,action)
		for final_state in transition_table[state+';'+action]:
			value += transition_table[state+';'+action][final_state]*expected_costs.get(final_state,0)
		
		if bool(min)==False or value<min:
			min = value 
			policy = action 
	return policy,min

def tracerun_MDP(transition_table,policy,cost_function):
	MDP_run={}
	for initial_state in transition_table: 
		states = []
		cost = 0 
		while next_state!='Low;Low;Low':
			action = policy[initial_state]
			cost+=cost_function(initial_state,action)
			n = len(transition_table[initial_state+";"+action])
			next_state = 0
			random_number = random.uniform(0,1)
			for state in transition_table[initial_state]:
				prob = transition_table[initial_state][state]
				if prob >= random_number: 
					next_state = state
				else:
					random_number-= prob
			states.append(next_state)
		MDP_run[initial_state] = (states,cost)
	return MDP_run

if __name__ == "__main__":
	main(sys.argv[1:], (sys.argc < 2)) #should pass as a boolean
	