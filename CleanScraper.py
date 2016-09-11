import github
import csv
import sys
import signal
from time import gmtime, strftime
import os.path	

import Tkinter as Tk
from github import Github

def signal_handler(signal, frame):
        sys.exit(1)

##signal.signal(signal.SIGINT, signal_handler)


class Scraper(object):

	def __init__(self):
		self.root = Tk.Tk()
		self.root.wm_title("Github Scraper")

		##Label and field declarations
		self.name_label = Tk.Label(self.root, text="Enter Github Username")
		self.name_label.pack()
		self.T_github_username = Tk.StringVar()

		Tk.Entry(self.root, textvariable=self.T_github_username).pack()
		self.results_label = Tk.Label(self.root, text="Enter number of results you want")
		self.results_label.pack()
		self.T_num_results = Tk.StringVar()
		self.T_num_results.set('10')
		Tk.Entry(self.root, textvariable=self.T_num_results).pack()

		self.location_label = Tk.Label(self.root, text="Enter the location")
		self.location_label.pack()
		self.T_location = Tk.StringVar()
		self.T_location.set('San Francisco')
		Tk.Entry(self.root, textvariable=self.T_location).pack()

		self.repos_label = Tk.Label(self.root, text="Enter the number of repos you want")
		self.repos_label.pack()
		self.T_num_repos = Tk.StringVar()
		self.T_num_repos.set('5')
		Tk.Entry(self.root, textvariable=self.T_num_repos).pack()

		self.followers_label = Tk.Label(self.root, text="Enter number of followers you want")
		self.followers_label.pack()
		self.T_num_followers = Tk.StringVar()
		self.T_num_followers.set('10')
		Tk.Entry(self.root, textvariable=self.T_num_followers).pack()

		self.buttontext = Tk.StringVar()
		self.buttontext.set("Scrape!")

		Tk.Button(self.root,
                  textvariable=self.buttontext,
                  command=self.clicked1).pack()

		self.label = Tk.Label(self.root, text="Filler Texted")
		self.label.pack()

		self.qual_users = set()
		self.qual_emails = set()
		self.used_emails = set()

		self.username = ''
		self.location = ''
		self.num_results = 0
		self.num_repos = 0
		self.num_followers = 0

		self.root.mainloop()




	def validate_inputs(self):
		self.username = self.T_github_username.get().strip().lower()
		self.location = self.T_location.get().strip().lower()
		self.num_results = int(self.T_num_results.get().strip())
		self.num_repos = int(self.T_num_repos.get().strip())
		self.num_followers = int(self.T_num_followers.get().strip())

	def clicked1(self):
		self.validate_inputs()
		self.label.configure(text=self.username)
		self.scrape()

	def button_click(self, e):
		pass

	def scrape(self):
		self.setup()
		self.run_script()
		self.write_file()
		return

	def setup(self):
		try:
			with open('prev_found.txt', 'r') as prev_file:
				curr_email = prev_file.readline().strip()
				while not curr_email == '':
					self.used_emails.add(curr_email)
					curr_email = prev_file.readline().strip()
		except:
			with open('prev_found.txt', 'w') as prev_file:
				self.label.configure(text = "created previously found file")
		return

	def run_script(self):
		try:
			gh = Github('39c1ad610c6c01fb0f2c30a68d2c24e54aa6ed3e')
		except:
			self.label.configure(text = "Github could not be reached. Contact Tevon, his account may be down or there may be a issue with the Github API")

		self.collect_user(gh)
		return

	def collect_user(self, gh):
		try:
			base_user = gh.get_user(self.username)
		except:
			self.label.configure(text = 'Github could not find a user with that username.')
		user_queue = []
		user_queue.append(base_user)
		self.qual_emails.add(base_user.email)
		count = 0;
		while user_queue:
			curr_user = user_queue.pop(0)
			count += 1
			self.label.configure(text = 'Evaluating user who '+ curr_user.name+ ' follows')	
			##Tries to iterate through followers, adding to qualified list and queue or discarding
			try:
				for user in curr_user.get_followers():
					if self.protect_user(user) and self.check_user(user):
						if not user.email in self.qual_emails:
							self.qual_users.add(user)
							self.qual_emails.add(user.email)
						user_queue.append(user)
						if len(self.qual_users) >= self.num_results: return
						self.label.configure(text = 'Added'+user.name)
			except:
				if self.qual_users: 
					self.label.configure(text = 'You may have reached your query limit for the Github API or another error occured while accessing user data. Please try again later')
					self.label.configure(text = 'In the mean time I have saved good profiles I have already found to the usual CSV')
					self.write_file()
				return 
		return

	def write_file(self):
		if self.qual_users:
			self.label.configure(text = 'Writing to CSV format.')

			##where to save
			save_path = 'GoogleDrive/Scraper'
			file_name = self.username+'_'+self.location+strftime('%m-%d %H_%M_%S')+'.csv'
			complete_name = os.path.join(os.path.expanduser('~'),save_path)
			complete_name = os.path.join(complete_name, file_name)

			with open(complete_name, 'w+') as cand_file:
				writer = csv.writer(cand_file)
				header_row = ['Name', 'Email', 'Location', 'Number of Repos', 'Number of Followers', 'Profile URL']
				writer.writerow(header_row)
				for user in self.qual_users:
					user_list = [user.name.encode('utf-8'), user.email.encode('utf-8'), user.location.encode('utf-8'), user.public_repos, user.followers, 'www.github.com/'+user.login.encode('utf-8')]
					writer.writerow(user_list)
			with open('prev_found.txt', 'a') as email_file:
				for email in self.qual_emails:
					if email:
						email_file.write(email+'\n')
		else:
			self.label.configure(text = "No users found with those criteria, try a different base or broaden repo and follower requirements.")
		return

	def protect_user(self, user):
		if user==None or user.location == None or user.email == None or user.name == None or user.followers == None or user.public_repos == None: return False
		if user.email in self.used_emails: 
			return False
		return True

	##Checks the criteria set to be considered a qualified profile (Checks number of followers, location and number of Repos)
	def check_user(self, user):
		if(user.followers >= self.num_followers and user.public_repos >= self.num_repos and ((user.location.lower() in self.location) or (self.location in user.location.lower()))): return True
		return False

def main():
	GithubScraper = Scraper()

main()
