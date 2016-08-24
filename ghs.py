import stdio
import urllib3
import requests
import github
import Queue

NUM_FOLLOWERS = 20
NUM_REPOS = 10
LOCATION = 'San Francisco, CA'
LIMIT = 3
q_size_limit = 3
qual_users = set()


from github import Github
def main():
	run_script()
	write_file()
	return

def run_script():



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
		if protect_user(user): continue
		## Checking Needed profile criteria

		print("Trying with:"+ user.name)
		if check_user(user):
			qual_users.add(user)
		count+=1
		if(count > 30): break


	result = ""
	for user in qual_users:
		result += user.name + ' ' + str(user.followers) + user.location + '\n'

	print(result)
	return

def collect_user(gh):
	user_name = 'mojombo'
	base_user = gh.get_user(user_name)
	user_queue = Queue.Queue(q_size_limit)
	user_queue.put(base_user)
	count = 0;
	while(not user_queue.empty() and count < LIMIT):
		curr_user = user_queue.get()
		count += 1
		if not user_queue.full():
			count_2 = 0;
			for user in curr_user.get_followers():
				if count_2 > 20: break
				if protect_user(user) and check_user(user):
					user_queue.put(user)
					qual_users.add(user)
					print("adding "+ curr_user.name)
					count_2 += 1

	return

def collect_searched(gh):
	return

def protect_user(user):
	if user==None or user.location == None or user.location not in LOCATION or user.name == None or user.followers == None or user.public_repos == None: return False
	if user in qual_users: return False
	print("Trying " + user.name)
	return True


def check_user(user):
	if(user.followers >= NUM_FOLLOWERS and user.public_repos >= NUM_REPOS and (user.location in LOCATION)): return True
	return False




def write_file():
	return

main()
