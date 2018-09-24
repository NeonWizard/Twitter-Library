import twit
import os

twit.enableDebug()

TWAUTH = [
	os.environ["TWITTER_API_KEY"],
	os.environ["TWITTER_API_SECRET"],
	os.environ["TWITTER_TOKEN"],
	os.environ["TWITTER_TOKEN_SECRET"]
]
DBINF = [
	"twitter-management.ccbwxidfcchn.us-east-1.rds.amazonaws.com",
	"wespooky",
	os.environ["DB_PASS"],
	"twittermanagement"	
]

t = twit.Twit(TWAUTH, DBINF)
