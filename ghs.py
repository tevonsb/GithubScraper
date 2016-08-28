##import stdio
import urllib3
import requests
import github
import Queue
import csv
import sys

NUM_FOLLOWERS = 20
NUM_REPOS = 10
LOCATION = 'San Francisco, CA'
LIMIT = 10
LIMIT_FOLLOWERS = 10
q_size_limit = 3
qual_users = set()
qual_emails = set()
used_emails = set()

from github import Github
def main():
	setup()
	run_script()
	print_list()
	write_file()
	return

def setup():
	with open('prev_found.txt', 'r') as prev_file:
		curr_email = prev_file.readline()
		while not curr_email == '':
			used_emails.add(curr_email)
			curr_email = prev_file.readline()
	return




def run_script():


	sys.stdout.write("Hello, World!")
	gh = Github('39c1ad610c6c01fb0f2c30a68d2c24e54aa6ed3e')

	whats_wanted = raw_input("type user (To set a base user), Search (To enter an advanced search string) or keyword (for a keyword based search): ")
	if whats_wanted == 'user': collect_user(gh)
	elif whats_wanted == 'search': collect_searched(gh)
	elif whats_wanted == 'keyword': collect_keyword(gh, 'hello')

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

def collect_user(gh):
	user_name = 'mojombo'
	base_user = gh.get_user(user_name)
	user_queue = []
	user_queue.append(base_user)
	count = 0;
	while user_queue and count < LIMIT:
		curr_user = user_queue.pop(0)
		count += 1
		if not len(user_queue)>LIMIT:
			count_2 = 0;
			sys.stdout.write('\nEvaluating user who '+ curr_user.name+ ' follows')
			for user in curr_user.get_followers():
				sys.stdout.write('. ')
				if count_2 > LIMIT_FOLLOWERS: break
				if protect_user(user) and check_user(user):
					user_queue.append(user)
					qual_users.add(user)
					qual_emails.add(user.email)
					print("\nadding "+ user.name)
					count_2 += 1

	return

def collect_searched(gh):
	return

def protect_user(user):
	if user==None or user.location == None or user.email == None or user.name == None or user.followers == None or user.public_repos == None: return False
	if user.email in qual_emails or user.email in used_emails: 
		return False
	return True


def check_user(user):
	if(user.followers >= NUM_FOLLOWERS and user.public_repos >= NUM_REPOS and (user.location in LOCATION)): return True
	return False

def print_list():
	result = ""
	for user in qual_users:
		result += user.name + ' ' + str(user.followers) + user.location + '\n'

	print(result)
	return


def write_file():
	print('Writing to CSV format.')
	with open('results.csv', 'w+') as cand_file:
		writer = csv.writer(cand_file)
		for user in qual_users:
			user_list = [user.name, user.email, user.location, user.followers, user.url]
			writer.writerow(user_list)
	with open('prev_found.txt', 'a') as email_file:
		for email in qual_emails:
			email_file.write(email+'\n')
	return

main()
