import datetime
from google.appengine.ext import db
from google.appengine.api import users

class Reminder(db.Model):
	id = (db.IntegerProperty(required=True))
	title = (db.StringProperty(required=True))
	longitude = (db.FloatProperty(required=True))
	latitude = (db.FloatProperty(required=True))
	