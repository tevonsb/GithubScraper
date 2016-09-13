##Trying to create a GUI with asynchonous I/O stream.
import csv
import sys
import signal
from time import gmtime, strftime
import os.path
import Queue
import threading
import errno

import Tkinter as Tk
from github import Github

##signal.signal(signal.SIGINT, signal_handler)
def signal_handler(signal, frame):
        sys.exit(1)


class GUI:

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
			textvariable=self.buttontext, command=self.scraper_clicked).pack()

		self.autobuttontext = Tk.StringVar()
		self.autobuttontext.set("Auto-scrape")
		Tk.Button(self.root, textvariable = self.autobuttontext, command = self.auto_clicked).pack()

		self.only_select_comps = Tk.IntVar()
		self.select_comp = Tk.Checkbutton(self.root, text = "Only select companies", variable = self.only_select_comps)
		self.select_comp.pack()

		self.label = Tk.Label(self.root, text="Users")
		self.label.pack()

		self.system_label = Tk.Label(self.root, text = "System Messages")
		self.system_label.pack()

		self.running = False
		self.auto_used = False

		self.auto_users = Queue.Queue()

		self.message_queue = Queue.Queue()
		self.system_queue = Queue.Queue()
		self.root.after(250, self.handle_queue)
		self.root.after(1000, self.handle_sys_queue)

		##Starts mainloop execution and sets window size
		self.root.minsize(400, 400)
		self.root.mainloop()

	##Checks the message and system asynchronous message queues for any messages posted by the Scraper object
	def handle_queue(self):
		try:
			msg = self.message_queue.get(0)
			self.label.configure(text = msg)
			if(msg == 'Done!'):
				self.running = False
		except Queue.Empty:
			pass
		self.root.after(250, self.handle_queue)

	def handle_sys_queue(self):
		try:
			msg = self.system_queue.get(0)
			self.system_label.configure(text = msg)
		except Queue.Empty:
			pass
		self.root.after(1000, self.handle_sys_queue)

	##Handles the click of the Scrape! button, creates a new thread for the scraping script.
	def scraper_clicked(self):
		if self.T_github_username.get() == '':
			self.label.configure(text = 'please enter a username')
			return
		print(self.T_github_username.get())
		if not self.running:
			inputs = [self.T_github_username.get().strip().lower(), self.T_location.get().strip().lower(), int(self.T_num_results.get().strip()), int(self.T_num_repos.get().strip()), int(self.T_num_followers.get().strip()), self.only_select_comps.get(), self.auto_users, self.auto_users]
			Scraper(self.message_queue, self.system_queue, inputs).start()
			self.running = True
		else:
			self.system_queue.put('A search is already running')

	def auto_clicked(self):
		self.auto_used = True
		self.gather_auto_users()
		self.auto_users.put('mojombo')
		try:
			temp = Tk.StringVar()
			temp.set(self.auto_users.get())
			print(temp.get())
			self.T_github_username = temp
		except:
			self.system_queue.put("The auto queue is empty... Try a regular scrape.")
		self.scraper_clicked()
		pass

	def gather_auto_users(self):
		try:
			with open('auto_users.txt', 'r') as auto_file:
				curr_user = auto_file.readline().strip 
				while not curr_user == '':
					self.auto_users.add(curr_user)
					curr_user = auto_file.readline().strip()
		except:
			with open('auto_users.txt', 'w') as auto_file:
				self.system_queue.put("created Auto-scrape file")

	def button_click(self, e):
		pass



class Scraper(threading.Thread):

	def __init__(self, queue, system_queue, inputs):
		threading.Thread.__init__(self)
		self.message_queue = queue
		self.system_queue = system_queue
		self.qual_users = Queue.PriorityQueue()
		self.qual_emails = set()
		self.used_emails = set()
		self.wanted_companies = set()

		self.username = inputs[0]
		self.location = inputs[1]
		self.num_results = inputs[2]
		self.num_repos = inputs[3]
		self.num_followers = inputs[4]
		self.only_select = inputs[5]

	##Starts the thread going
	def run(self):
		self.setup()
		self.run_script()
		self.write_file()
		return

	##Reads in previously found candidates and also creates Desktop folder if it does not already exist.
	def setup(self):
		##Open or create prev_found file
		try:
			with open('prev_found.txt', 'r') as prev_file:
				curr_email = prev_file.readline().strip()
				while not curr_email == '':
					self.used_emails.add(curr_email)
					curr_email = prev_file.readline().strip()
		except:
			with open('prev_found.txt', 'w') as prev_file:
				self.post_system("created previously found file")

		##Open or create wanted_company file
		try:
			with open('wanted_company.txt', 'r') as wanted_file:
				curr_company = wanted_file.readline().strip()
				while not curr_company == '':
					self.wanted_companies.add(curr_company.lower())
					curr_company = wanted_file.readline().strip()
		except:
			with open('wanted_company.txt', 'w') as wanted_file:
				self.post_system("created previously found file")

		##Create Desktop directory if needed
		try:
			complete_name = os.path.join(os.path.expanduser('~'),'Desktop/Github Scraped')
			os.makedirs(complete_name)
			self.post_system('Created directory Github Scraped on your Desktop')
		except OSError as exception:
			if exception.errno != errno.EEXIST:
				raise

		return

	##Establishes OAuth connection to Github using tevonsb
	def run_script(self):
		try:
			gh = Github('9d4d22032b635a02b06e5ef7b4dc82af5366b9fa')
		except:
			self.post_system("Github could not be reached. Contact Tevon, his account may be down or there may be a issue with the Github API")

		self.collect_user(gh)
		return

	##Starts with the base user and performs a breadth first search on those followers, adding to a queue, finishes
	##when there are no more candidates in the queue or the desired number of candidates is found.
	def collect_user(self, gh):
		try:
			base_user = gh.get_user(self.username)
		except:
			self.post_system('Github could not find a user with that username.')
		user_queue = []
		user_queue.append(base_user)
		self.qual_emails.add(base_user.email)
		count = 0;
		while user_queue:
			curr_user = user_queue.pop(0)
			count += 1
			self.post_message('Evaluating user who '+ curr_user.name+ ' follows')	
			##Tries to iterate through followers, adding to qualified list and queue or discarding
			try:
				for user in curr_user.get_followers():
					if self.protect_user(user):
						self.post_message('Checked '+user.name)
						if self.check_user(user):
							if not user.email in self.qual_emails:
								self.qual_users.put((self.get_priority(user),user))
								self.qual_emails.add(user.email)
							user_queue.append(user)
							if self.qual_users.qsize() >= self.num_results: return
							self.post_message('Added '+user.name)
			except:
				if not self.qual_users.empty(): 
					self.post_system('You may have reached your query limit for the Github API or another error occured while accessing user data. Please try again later')
					self.write_file()
				return 
		return

	##Writes files (Previously found and found candidates)
	def write_file(self):
		if not self.qual_users.empty():
			self.post_system('Writing to CSV format.')
			self.post_message('Done!')

			##where to save, creates a folder on the desktop if one does not exist and labels file
			save_path = 'Desktop/Github Scraped'
			file_name = self.username+'_'+self.location+strftime('%m-%d %H_%M_%S')+'.csv'
			complete_name = os.path.join(os.path.expanduser('~'),save_path)
			complete_name = os.path.join(complete_name, file_name)

			with open(complete_name, 'w+') as cand_file:
				writer = csv.writer(cand_file)
				header_row = ['Name', 'Email', 'Location', 'Number of Repos', 'Number of Followers', 'Profile URL', 'Company', 'Bio']
				writer.writerow(header_row)
				while not self.qual_users.empty():
					user = self.qual_users.get()[1]
					user_list = self.create_csv_user(user)
					writer.writerow(user_list)

			##Writes to the list of previously found candidates, creates file if it does not exist
			with open('prev_found.txt', 'a') as email_file:
				for email in self.qual_emails:
					if email:
						email_file.write(email+'\n')
		else:
			self.post_system("No users found with those criteria, try a different base or broaden repo and follower requirements.")
		return

	def get_priority(self, user):
		priority = 20000
		if user.company != None:
			priority-=300
			if user.company.lower() in self.wanted_companies:
				priority -= 10000
			priority -= user.followers
		if priority < 0:
			priority = 0
		return priority

	def create_csv_user(self, user):
		user_list = [user.name.encode('utf-8'), user.email.encode('utf-8'), user.location.encode('utf-8'), user.public_repos, user.followers, 'www.github.com/'+user.login.encode('utf-8'), ' ', ' ']
		if not user.company == None:
			user_list[6] = user.company.encode('utf-8')
		if not user.bio == None:
			user_list[7] = user.bio.encode('utf-8')
		return user_list

	##Checks that none of the used fields are None, and that the candidate has not already been found. 
	def protect_user(self, user):
		if user==None or user.location == None or user.email == None or user.name == None or user.followers == None or user.public_repos == None: return False
		if user.email in self.used_emails: 
			return False
		return True

	##Checks the criteria set to be considered a qualified profile (Checks number of followers, location and number of Repos)
	def check_user(self, user):
		if self.only_select:
			if user.company == None or user.company.lower() not in self.wanted_companies or user.company == '' or user.company == ' ': return False
		if(user.followers >= self.num_followers and user.public_repos >= self.num_repos and ((user.location.lower() in self.location) or (self.location in user.location.lower()))): return True
		return False

	##Posts msg to the message_queue asynchronous queue to be printed to the GUI
	def post_message(self, msg):
		self.message_queue.put(msg)

	##posts msg to the system_queue asynchronous queue to print to the GUI
	def post_system(self, msg):
		self.system_queue.put(msg)

def main():
	GithubScraper = GUI()

main()