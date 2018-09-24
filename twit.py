from twython import Twython, TwythonError, TwythonRateLimitError
import pymysql

import time, datetime
import random

# --- PRIVATE ---
_DEBUG = False

def _output(out, force=False):
	if force or _DEBUG: print(out)

# --- PUBLIC ---
def enableDebug():
	_DEBUG = True
def disableDebug():
	_DEBUG = False


class Twit:
	def __init__(self, TWAUTH, DBINF):
		# -- InitiaLize Connections --
		# Twitter API
		self.TWYTHON = {"API": Twython(*TWAUTH)}

		# Amazon RDS SQL server
		self.DB = {"CONN": pymysql.connect(*DBINF)}
		self.DB["CURS"] = self.DB["CONN"].cursor()


		# -- Load Data --
		self.hasFollowed = set()
		self.hasFollowedE = []

		self.DB["CURS"].execute("SELECT ct, twitterID FROM HasFollowed")
		for x in self.DB["CURS"].fetchall():
			ct, ID = x[0].timestamp(), x[1]
			self.hasFollowed.add(int(ID))
			self.hasFollowedE.append((int(ID), int(ct)))

		self.hasFollowedE.sort(key=lambda x: x[1])

		_output("Length of followed before: {}".format(len(self.hasFollowed)))

		self.DB["CURS"].execute("SELECT twitterID from Whitelist")
		self.whitelist = [int(x[0]) for x in self.DB["CURS"].fetchall()]

		self.isFollowed = set([int(x) for x in self.TWYTHON["API"].get_friends_ids()["ids"]])	# The isFollowed set ONLY includes people currently being followed
		self.followers = set([int(x) for x in self.TWYTHON["API"].get_followers_ids()["ids"]])	# People following this account

		self.exceptions = 0


	def follow(self, ID, user_obj=None):
		t = int(time.time())
		try:
			user = user_obj if user_obj else self.TWYTHON["API"].show_user(user_id=ID)
			self.TWYTHON["API"].create_friendship(user_id=ID)

			self.hasFollowed.add(int(ID))
			self.hasFollowedE.append((int(ID), t))
			self.DB["CURS"].execute(
				"INSERT INTO HasFollowed (ct, twitterID) VALUES ('{}', {})".format(
					datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S'), ID))
			self.DB["CONN"].commit()

			_output("\033[92m[FOLLOWED]\033[0m {} - https://twitter.com/{}".format(user['name'], user['screen_name']))

			return True
		except Exception as e:
			_output("\033[93m[ERROR]\033[0m Account {}".format(ID), force=True)
			_output("\t{}".format(e), force=True)
			if isinstance(e, TwythonRateLimitError):
				raise TwythonRateLimitError
			elif "already requested" in str(e) or "blocked" in str(e):
				self.hasFollowed.add(int(ID))
				self.hasFollowedE.append((int(ID), t))
				self.DB["CURS"].execute(
					"INSERT INTO HasFollowed (ct, twitterID) VALUES ('{}', {})".format(
						datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S'), ID))
				self.DB["CONN"].commit()
			else:
				self.exceptions += 1

			if self.exceptions > 3:
				raise e

			return False

	def unfollow(self, ID, user_obj=None):
		try:
			user = user_obj if user_obj else self.TWYTHON["API"].show_user(user_id=ID)
			if ID in self.whitelist:
				_output("\033[96m[WHITELIST SKIP]\033[0m {} - https://twitter.com/{}".format(user['name'], user['screen_name']))
				return False

			self.TWYTHON["API"].destroy_friendship(user_id=ID)

			_output("\033[91m[UNFOLLOWED]\033[0m {} - https://twitter.com/{}".format(user['name'], user['screen_name']))

			return True
		except Exception:
			_output("\033[93m[ERROR]\033[0m Account {}".format(ID), force=True)

			self.exceptions += 1
			if self.exceptions > 3:
				raise Exception("More than 3 exceptions have been caught - exiting.")

			return False
