'''
    A very basic stub to show how to implement use the event and send it
    to REDIS.
'''

from mixevent import build_event
import redis
import json

REDIS_HOST = '127.0.0.1' # If this really was Django, you'd put this in settings

def register(request):
    ''' Let's pretend this is a registration event that's part of Django
        and therefore has a request header with access to the HTTP meta tags.
        In this (not so) hypothetical example, a user fills out a registration
        form and signsup, we want to log this event AFTER validation
    '''
    
    # Your form validation code goes here.
    
    # Everything is OK and you now want to log the signup event.
    
    # We are behind NGINX and forwarding the IP, but it's really important to
    # record this - so we match with the IP used by the MixPanel javascript
    # library.  Otherwise funnels won't work properly.
    event = build_event('signup', ip_address=request.META['HTTP_X_REAL_IP'])
    logger.debug('Pushing signup event to REDIS')
    dbr = redis.Redis(host=REDIS_HOST)
    dbr.rpush('mixpanel:mixevent', json.dumps(event))
    
    # Happy processing - the task is now on the queue.

