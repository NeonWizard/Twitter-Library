# TWIT
`Twit` is a custom-built Twython wrapper meant for quick and easy creation of scripts for manipulating Twitter follows.

## Documentation
Initialization requires authorization on the part of Twython and MySQL.

```python
TWAUTH = [
	'YOUR_API_KEY', 'YOUR_API_SECRET',
	'YOUR_TOKEN', 'YOUR_TOKEN_SECRET'
]
DBINF = [
	'HOSTNAME',
	'DBUSER', 'DBPASS', 'DBNAME'
]

twitter = twit.Twit(TWAUTH, DBINF)
```
