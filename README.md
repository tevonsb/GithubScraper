# GithubScraper

This scraper takes a seed username and uses hir or her network to find other profiles that fit the specifications that you choose. These specs
are: Location, Number of Repos and Number of Followers. It takes each group of followers and performs a breadth first search 
using a OAuth connection. 

This is a tool I created for my team and as an exercise to learn Python as I'd never used it before!

It uses a theaded, asynchronous queue to keep the GUI up to date. 

Future changes:
  Updated GUI
  Advanced error handling
  Threaded concurrent searches

