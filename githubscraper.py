import stdio
import urllib3
import requests



def main():
	run_script()
	parse_data()
	write_file()
	return

def run_script():
	'''
	location = raw_input('Enter a location: ')
	num_repos = '>5'
	num_repos = raw_input('Number of repos, range say >20')
	num_followers = '>5'
	num_followers = raw_input('Number of followers: same range as above! ')
	'''
	##search_string = 'https://api.github.com/search/users?q='+'location:"'+location+'"'+'+repos:'+num_repos
	search_string = 'https://api.github.com/tevonsb/emails'
	r = requests.get(search_string, auth = ('tevonsb', 'T3v0ni23'))
	stdio.writeln(r.status_code)
	stdio.writeln(r.headers)

	##stdio.writeln(r.json())
	##stdio.writeln('Your search returned '+r.total_count+' results.')
	return


def parse_data():
	return

def write_file():
	return

main()