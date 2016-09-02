import github
import csv
import sys
import signal
from time import gmtime, strftime


##Global variable (semi constant) declarations
NUM_FOLLOWERS = 20
NUM_REPOS = 10
LOCATION = 'San Francisco, CA'
LIMIT_FOLLOWERS = 10
q_size_limit = 40
qual_users = set()
qual_emails = set()
used_emails = set()
LIMIT = 10

##pyGithub Library
from github import Github


def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        sys.exit(1)

signal.signal(signal.SIGINT, signal_handler)

##calls needed functions in the correct order, passes around an array of inputs dictated by a file or user input.
def main():
	inputs = ['', '', '', LIMIT, NUM_FOLLOWERS, NUM_REPOS]
	setup(inputs)
	run_script(inputs)
	print_list()
	write_file(inputs)
	return

##Sets up and reads the file of previously found profiles. Takes inputs as a parameter and fills it with user input with a call to get_inputs
def setup(inputs):
	try:
		with open('prev_found.txt', 'r') as prev_file:
			curr_email = prev_file.readline().strip()
			while not curr_email == '':
				used_emails.add(curr_email)
				curr_email = prev_file.readline().strip()
	except:
		with open('prev_found.txt', 'w') as prev_file:
			print("created previously found file")
	get_input(inputs)
	return


##Takes user inputs and assigns global variables, commented section with ability to read inputs from file. 
def get_input(inputs):
	inputs[0] = raw_input("Do you want a keyword or user search? : ").strip()
	inputs[1] = raw_input("What is the username or keyword you want to search? : ").strip()
	inputs[2] = raw_input("Where should they be located? Enter as many locations as you like. : ")
	inputs[3] = int(raw_input("How many results do you want? : ").strip())
	inputs[4] = int(raw_input("At least how many repos should they have? : ").strip())
	inputs[5] = int(raw_input("At least how many followers should they have? : ").strip())

	global LIMIT_FOLLOWERS
	global LOCATION
	global NUM_REPOS
	global NUM_FOLLOWERS
	global LIMIT

	LIMIT = inputs[2]
	NUM_REPOS = inputs[3]
	NUM_FOLLOWERS = inputs[4]

	'''
	with open("input_file.txt", 'r') as input_file:
		read_first_line = input_file.readline()
		whats_wanted = read_first_line[read_first_line.index(':')+1:] ##Sudo code, figure out how to actually code this.
		read_second = input_file.readline()
		input_word = read_second[read_second.index(':')+1:]
		inputs[0] = whats_wanted
		inputs[1] = input_word
		limit_line = input_file.readline()
		global LIMIT
		LIMIT = limit_line[limit_line.index(':')+1].strip()
		print(LIMIT)
		print("Got here")
		'''

##Establishes an auth0 connection to Github (Good for 5000 reqs/hr) calls search function.
def run_script(inputs):

	try:
		gh = Github('39c1ad610c6c01fb0f2c30a68d2c24e54aa6ed3e')
	except:
		print("Github could not be reached. Contact Tevon, his account may be down or there may be a issue with the Github API")

	##whats_wanted = raw_input("type user (To set a base user), Search (To enter an advanced search string) or keyword (for a keyword based search): ")
	inputs[0] = inputs[0].lower().strip()
	inputs[1] = inputs[1].lower().strip()
	if inputs[0] in 'user' or 'user' in inputs[0]: collect_user(gh, inputs, inputs[1])
	elif inputs[0] == 'search': collect_searched(gh)
	elif inputs[0] == 'keyword': collect_keyword(gh, inputs, inputs[1])

	return

##Keyword based search (Github may depricate this functionality soon)
'''
def collect_keyword(gh, inputs, search_term):


	users = gh.search_users(search_term)

	count = 0
	print("Warning: Github may deprecate this feature in the next iteration of their API")
	try:
		for user in users:
			sys.stdout.write('. ')
			sts.stdout.flush()
			if protect_user(user):
			## Checking Needed profile criteria
				if check_user(user):
					qual_users.add(user)
					qual_emails.add(user.email)
				count+=1
			if(count > LIMIT): break
	except: 
		print('You may have reached your query limit for the Github API or another error occured while accessing user data. Please try again later')
		print('In the mean time I have saved good profiles I have already found to the usual CSV')
		write_file(inputs)
		return
	return
'''

##User based search, takes a seed user and checks who he follows for more qualified users
def collect_user(gh, inputs, user_name):
	try:
		base_user = gh.get_user(user_name)
	except:
		print('Github could not find a user with that username.')
		## Add code to handle entering another name and reinputing into Algo
	user_queue = []
	user_queue.append(base_user)
	qual_emails.add(base_user.email)
	count = 0;
	while user_queue:
		curr_user = user_queue.pop(0)
		count += 1
		if not len(user_queue)>LIMIT:
			count_2 = 0;
			sys.stdout.write('\nEvaluating user who '+ curr_user.name+ ' follows\n')
			
			##Tries to iterate through followers, adding to qualified list and queue or discarding
			try:
				print('Got into try...')
				for user in curr_user.get_followers():
					sys.stdout.write('. ')
					sys.stdout.flush()
					if count_2 > LIMIT_FOLLOWERS: break
					if protect_user(user) and check_user(user):
						user_queue.append(user)
						qual_users.add(user)
						if len(qual_users) >= LIMIT: return
						qual_emails.add(user.email)
						print("+ ")
						count_2 += 1
			except:
				if qual_users: 
					print('You may have reached your query limit for the Github API or another error occured while accessing user data. Please try again later')
					print('In the mean time I have saved good profiles I have already found to the usual CSV')
					write_file(inputs)
	return

##Protects from possible None fields. If any of these required fields are None, returns false and algo passes over.
def protect_user(user):
	if user==None or user.location == None or user.email == None or user.name == None or user.followers == None or user.public_repos == None: return False
	if user.email in qual_emails: return False 
	if user.email in used_emails: 
		sys.stdout.write("- ")
		return False
	return True

##Checks the criteria set to be considered a qualified profile (Checks number of followers, location and number of Repos)
def check_user(user):
	if(user.followers >= NUM_FOLLOWERS and user.public_repos >= NUM_REPOS and ((user.location in LOCATION) or (LOCATION in user.location))): return True
	return False

##Testing Helper function
def print_list():
	result = ""
	for user in qual_users:
		result += user.name + ' ' + str(user.followers).encode('utf-8') + user.location + '\n'

	print(result)
	return

##Writes the CSV file and appends the previously found file with the new returned profiles. 
def write_file(inputs):
	if qual_users:
		print('Writing to CSV format.')
		file_name = inputs[0]+'_'+inputs[1]+strftime('%m-%d %H_%M_%S')+'.csv'
		with open(file_name, 'w+') as cand_file:
			writer = csv.writer(cand_file)
			header_row = ['Name', 'Email', 'Location', 'Number of Repos', 'Number of Followers', 'Profile URL']
			writer.writerow(header_row)
			for user in qual_users:
				user_list = [user.name.encode('utf-8'), user.email, user.location, user.public_repos, user.followers, 'github.com/'+user.login]
				writer.writerow(user_list)
		with open('prev_found.txt', 'a') as email_file:
			for email in qual_emails:
				email_file.write(email+'\n')
	else:
		print("No users found with those criteria, try a different base or broaden repo and follower requirements.")
	return

main()
