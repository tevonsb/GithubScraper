import github
import csv
import sys
from time import gmtime, strftime

NUM_FOLLOWERS = 20
NUM_REPOS = 10
LOCATION = 'San Francisco, CA'
LIMIT_FOLLOWERS = 10
q_size_limit = 3
qual_users = set()
qual_emails = set()
used_emails = set()

from github import Github
def main():
	inputs = ['', '']
	setup(inputs)
	run_script(inputs)
	print_list()
	write_file(inputs)
	return

def setup(inputs):
	with open('prev_found.txt', 'r') as prev_file:
		curr_email = prev_file.readline().strip()
		while not curr_email == '':
			used_emails.add(curr_email)
			print(curr_email)
			curr_email = prev_file.readline().strip()
	global LIMIT
	get_input(inputs)
	return

def get_input(inputs):
	with open("input_file.txt", 'r') as input_file:
		read_first_line = input_file.readline()
		whats_wanted = read_first_line[read_first_line.index(':')+1:] ##Sudo code, figure out how to actually code this.
		read_second = input_file.readline()
		input_word = read_second[read_second.index(':')+1:]
		inputs[0] = whats_wanted
		inputs[1] = input_word
		limit_line = input_file.readline()
		LIMIT = limit_line[limit_line.index(':')+1].strip()
		print(LIMIT)


def run_script(inputs):


	gh = Github('39c1ad610c6c01fb0f2c30a68d2c24e54aa6ed3e')

	##whats_wanted = raw_input("type user (To set a base user), Search (To enter an advanced search string) or keyword (for a keyword based search): ")
	inputs[0] = inputs[0].lower().strip()
	inputs[1] = inputs[1].lower().strip()
	if inputs[0] in 'user' or 'user' in inputs[0]: collect_user(gh, inputs[1])
	elif inputs[0] == 'search': collect_searched(gh)
	elif inputs[0] == 'keyword': collect_keyword(gh, inputs[1])

	return


def collect_keyword(gh, search_term):


	users = gh.search_users(search_term)

	count = 0
	for user in users:
		if protect_user(user):
		## Checking Needed profile criteria
			if check_user(user):
				qual_users.add(user)
				qual_emails.add(user.email)
			count+=1
		if(count > LIMIT): break
	return

def collect_user(gh, user_name):
	base_user = gh.get_user('mojombo')
	user_queue = []
	user_queue.append(base_user)
	count = 0;
	while user_queue:
		curr_user = user_queue.pop(0)
		count += 1
		if not len(user_queue)>LIMIT:
			count_2 = 0;
			sys.stdout.write('\nEvaluating user who '+ curr_user.name+ ' follows')
			for user in curr_user.get_followers():
				sys.stdout.write('. ')
				sys.stdout.flush()
				if count_2 > LIMIT_FOLLOWERS: break
				if protect_user(user) and check_user(user):
					user_queue.append(user)
					qual_users.add(user)
					if len(qual_users) >= LIMIT: return
					qual_emails.add(user.email)
					print("\nadding "+ user.name)
					count_2 += 1

	return

def collect_searched(gh):
	return

def protect_user(user):
	if user==None or user.location == None or user.email == None or user.name == None or user.followers == None or user.public_repos == None: return False
	if user.email in qual_emails: return False 
	if user.email in used_emails: 
		print("found repeat email")
		return False
	return True


def check_user(user):
	if(user.followers >= NUM_FOLLOWERS and user.public_repos >= NUM_REPOS and (user.location in LOCATION)): return True
	return False

def print_list():
	result = ""
	for user in qual_users:
		result += user.name + ' ' + str(user.followers).encode('utf-8') + user.location + '\n'

	print(result)
	return


def write_file(inputs):
	print('Writing to CSV format.')
	file_name = inputs[0]+'_'+inputs[1]+strftime('%m-%d %H_%M_%S')+'.csv'
	with open(file_name, 'w+') as cand_file:
		writer = csv.writer(cand_file)
		for user in qual_users:
			user_list = [user.name.encode('utf-8'), user.email, user.location, user.followers, 'github.com/'+user.login]
			writer.writerow(user_list)
	with open('prev_found.txt', 'a') as email_file:
		for email in qual_emails:
			email_file.write(email+'\n')
	return

main()
