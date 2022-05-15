import re, sys
import random
import json 

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
	return 20

#if do_calc, take 0th of argv as filename of input data and compute and save off serialization/json files
#else, take argv as filenames of [transition_table, expected_costs, policies]
def main(argv, do_calc):
	if argv[0] == "splitdays":
		if do_calc:
			days = split_data_day(argv[1])
			for i,path in enumerate(list(days)):	
				t = "transition_table" + str(i+1) + '.json'
				e = "expected_costs" + str(i+1) + '.json'
				p = "policies" + str(i+1) + '.json'
				argv = [path] + [t,e,p]		
				main2(argv,do_calc)
		else:
			for i in range(3):	
				t = "transition_table" + str(i+1) + '.json'
				e = "expected_costs" + str(i+1) + '.json'
				p = "policies" + str(i+1) + '.json'
				argv = [t,e,p]
				main2(argv,do_calc)
			
	else:	
		t = "transition_table.json"
		e = "expected_costs.json" 
		p = "policies.json" 
		if do_calc:
			argv = [argv[1]] + [t,e,p]
		else:
			argv = [t,e,p]
		main2(argv, do_calc)
	return
		
def main2(argv, do_calc):
	print(argv)
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
		with open(argv[1],'w') as file_object:
			json.dump(transition_table,file_object)
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
		#HERE: save off results (expected_costs, policies) as JSON for next time
		with open(argv[2],'w') as file_object:
			json.dump(expected_costs,file_object)
		with open(argv[3],'w') as file_object:
			json.dump(policies,file_object)
	else:
		#HERE: json load in the transition_table, expected_costs, and policies
		with open(argv[0]) as file_object:
			transition_table = json.load(file_object)
		with open(argv[1]) as file_object:
			expected_costs = json.load(file_object)
		with open(argv[2]) as file_object:
			policies = json.load(file_object)
	#next, run one simulation/trace from each initial state
	tracerun_MDP(transition_table, policies, cost_function)

def make_transition_table(f):
	dict={}
	
	#do some re and print the output, let's say 5 times
	for i,s in enumerate(list(f.readlines())):
		non_initial = []
		#print(s, end='')
		m = re.search(pattern, s)
		if m == None:
			continue
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
	filename = 'transition_table.json'          #use the file extension .json
	with open(filename, 'w') as file_object:  #open the file in write mode
		json.dump(dict, file_object)
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
	global states
	MDP_run={}
	for i in range(30000):
		for initial_state in states: 
			visited_states = []
			cost = 0 
			next_state = initial_state
			while next_state!='Low;Low;Low':
				action = policy[next_state]
				state_action = next_state+';'+action
				#print(state_action)
				cost+=cost_function(next_state,action)
				random_number = random.uniform(0,1)
				for state in transition_table[state_action]:
					#print(state)
					prob = transition_table[state_action][state]
					#print(prob)
					#print(random_number)
					if prob >= random_number: 
						next_state = state
						break	
					else:
						random_number-= prob
					
				#print(next_state)
				visited_states.append(next_state)
			#print(visited_states)
			MDP_run[initial_state] = MDP_run.get(initial_state,0)+cost
		#print(i, end=' ')
		#for state in MDP_run: 
		#	print(MDP_run[state], end=' ')
		#print(" ")
	print('final', end=' ')
	for state in MDP_run: 
		MDP_run[state]=MDP_run[state]/30000
		print(str(state) + ' ' + str(MDP_run[state]), end=' ')
	return MDP_run

def split_data_day(argv):
    file = open(argv, "r")
    list_file = file.read().splitlines()
    m = re.search(pattern, list_file[0])
    if m == None:
        list_file=list_file[1:]
    print(list_file)
    print(len(list_file))
    day_1 = list_file[:4230]
    day_1 = "\n".join(day_1)
    day_2 = list_file[4230:8460]
    day_2 = "\n".join(day_2)
    day_3 = list_file[8460:]
    day_3 = "\n".join(day_3)
    file = open('day_1.csv','w')
    file.write(day_1)
    file = open('day_2.csv','w')
    file.write(day_2)
    file = open('day_3.csv','w')
    file.write(day_3)
    return 'day_1.csv','day_2.csv','day_3.csv'
	
if __name__ == "__main__":
	#print(len(sys.argv), sys.argv)
	#DEPRECATED: main(sys.argv[1:], (len(sys.argv) < 3)) #should pass as a boolean
	if sys.argv[1] == "Create":
		main(sys.argv[2:], True)
	elif sys.argv[1] == "Load":	
		main(sys.argv[2:], False)
	else:
		print("Run in either Create or Load mode!")
		exit
