# Copyright (C) 2013 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Request Handler for /notify endpoint."""

__author__ = 'alainv@google.com (Alain Vongsouvanh)'


import io
import json
import logging
import webapp2
import math

from random import choice
from apiclient.http import MediaIoBaseUpload
from oauth2client.appengine import StorageByKeyName
from google.appengine.ext import db
from google.appengine.api import users


from model import Credentials
import util


CAT_UTTERANCES = [
		"<em class='green'>Purr...</em>",
		"<em class='red'>Hisss... scratch...</em>",
		"<em class='yellow'>Meow...</em>"
]


class NotifyHandler(webapp2.RequestHandler):
	"""Request Handler for notification pings."""

	MAX_DISTANCE = 200  # Notify users when they are less than 100 feet from the location.

	def post(self):
		"""Handles notification pings."""
		logging.info('Got a notification with payload %s', self.request.body)
		data = json.loads(self.request.body)
		userid = data['userToken']
		# TODO: Check that the userToken is a valid userToken.
		self.mirror_service = util.create_service(
				'mirror', 'v1',
				StorageByKeyName(Credentials, userid, 'credentials').get())
		if data.get('collection') == 'locations':
			self._handle_locations_notification(data)
		elif data.get('collection') == 'timeline':
			self._handle_timeline_notification(data)

	def _get_distance(lat1, long1, lat2, long2):
		# Convert latitude and longitude to 
		# spherical coordinates in radians.
		degrees_to_radians = math.pi/180.0
				
		# phi = 90 - latitude
		phi1 = (90.0 - lat1)*degrees_to_radians
		phi2 = (90.0 - lat2)*degrees_to_radians
				
		# theta = longitude
		theta1 = long1*degrees_to_radians
		theta2 = long2*degrees_to_radians
				
		# Compute spherical distance from spherical coordinates.
				
		# For two locations in spherical coordinates 
		# (1, theta, phi) and (1, theta, phi)
		# cosine( arc length ) = 
		#    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
		# distance = rho * arc length
		
		cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
					 math.cos(phi1)*math.cos(phi2))
		arc = math.acos( cos )

		# Returns distance in feet
		return arc * 3960 * 5280

	def _handle_locations_notification(self, data):
		"""Handle locations notification."""
		location = self.mirror_service.locations().get(id=data['itemId']).execute()
		lat = location.get('latitude')
		lng = location.get('longitude')

		reminders = Reminder.gql("WHERE user = :user_id", user_id = users.get_current_user().user_id())
		for reminder in reminders: # for each reminder in the database:
			distance = _get_distance(lat, lng, reminder.latitude, reminder.longitude)

			distance_msg = '%s feet away' % int(round(distance))

			if distance < MAX_DISTANCE:
				map_html = '''
				<article>
					<figure>
						<img src="glass://map?w=240&h=360&marker=0;{0},
							{1}&polyline=;"
							height="360" width="240">
					</figure>
					<section>
						<div class="text-auto-size">
							<p class="yellow">Reminder</p>
							<p>{2}</p>
							<p style="font-size:.7em;">{3}</p>
						</div>
					</section>
				</article>'''.format(lat, lng, reminder.title, distance_msg)

				body = {
						'html': map_html,
						'text': reminder.title,
						'location': location,
						'menuItems': [{'action': 'NAVIGATE'}],
						'notification': {'level': 'DEFAULT'}
				}
				self.mirror_service.timeline().insert(body=body).execute()

	def _handle_timeline_notification(self, data):
		"""Handle timeline notification."""
		for user_action in data.get('userActions', []):
			# Fetch the timeline item.
			item = self.mirror_service.timeline().get(id=data['itemId']).execute()

			if user_action.get('type') == 'SHARE':
				# Create a dictionary with just the attributes that we want to patch.
				body = {
						'text': 'Python Quick Start got your photo! %s' % item.get('text', '')
				}

				# Patch the item. Notice that since we retrieved the entire item above
				# in order to access the caption, we could have just changed the text
				# in place and used the update method, but we wanted to illustrate the
				# patch method here.
				self.mirror_service.timeline().patch(
						id=data['itemId'], body=body).execute()

				# Only handle the first successful action.
				break
			elif user_action.get('type') == 'LAUNCH':
				# Grab the spoken text from the timeline card and update the card with
				# an HTML response (deleting the text as well).
				note_text = item.get('text', '');
				utterance = choice(CAT_UTTERANCES)

				item['text'] = None
				item['html'] = ("<article class='auto-paginate'>" +
						"<p class='text-auto-size'>" +
						"Oh, did you say " + note_text + "? " + utterance + "</p>" +
						"<footer><p>Python Quick Start</p></footer></article>")
				item['menuItems'] = [{ 'action': 'DELETE' }];

				self.mirror_service.timeline().update(
						id=item['id'], body=item).execute()
			else:
				logging.info(
						"I don't know what to do with this notification: %s", user_action)


NOTIFY_ROUTES = [
		('/notify', NotifyHandler)
]
