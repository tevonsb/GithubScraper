import stdio
import urllib3
import requests
import github

NUM_FOLLOWERS = 20
NUM_REPOS = 10
LOCATION = 'San Francisco, CA'


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

	qual_users = set()
	count = 0
	for user in users:
		if user==None: continue
		## Checking Needed profile criteria
		if user.location == None or user.location not in LOCATION or user.name == None: continue
		print("Trying with:"+ user.name)
		check_user(user, qual_users)
		count+=1
		if(count > 30): break


	result = ""
	for user in qual_users:
		result += user.name + ' ' + str(user.followers) + user.location + '\n'

	print(result)
	return

def collect_user(gh, user):
	user_name = 'tevonsb'
	base_user = gh.get_user(user_name)
	for
	return

def collect_searched(gh):
	return





def check_user(user, qual_users):
	if(user.followers >= NUM_FOLLOWERS and user.public_repos >= NUM_REPOS and (user.location in LOCATION)):
		qual_users.add(user)
	return




def write_file():
	return

main()
