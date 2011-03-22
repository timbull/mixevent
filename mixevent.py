#!/usr/bin/env python

''' A basic gevent worker that will continually process MixPanel events from
    a REDIS queue and send them to mixpanel '''

import redis
import signal
import json
import time

from mixpanel import track

import gevent
from gevent.pool import Pool
from gevent import monkey
monkey.patch_all()

REDIS_HOST = '127.0.0.1' # Whereever your REDIS server is hosted


def run(payload):
    """ Executes the thread with the settings """

    try:
        task = json.loads(payload)
    except:
        # logger.error(traceback.format_exc()) <-   You want to implement some
        #                                           logging here to catch this
        return

    # I don't normally care enough to track if it failed or not... but the
    # following returns True or False according to its success.
    # Consider resubmitting the task to the REDIS queue on a fail.
    track(task)

def request_shutdown(signum, frame):
    """ Let the thread know to shutdown """
    global _shutdown
    _shutdown = True

if __name__ == "__main__":
    """ Execute and enter a permanent loop """
    signal.signal(signal.SIGTERM, request_shutdown)
    signal.signal(signal.SIGINT, request_shutdown)
    signal.signal(signal.SIGQUIT, request_shutdown)

    dbr = redis.Redis(host=REDIS_HOST)
    queue = 'mixpanel:mixevent'
    pool = Pool(2)

    total = 0
    global _shutdown
    _shutdown = False
    # Restart the process every 1,000 messages.
    while not _shutdown and total < 1000:
        payload = dbr.lpop(queue)
        if not payload:
            # Have to set this carefully since we don't want to storm the
            # redis server with "do you have a message for me" requests.
            gevent.sleep(5)
            continue
        else:
            total += 1
            # Optional, but you can log these so you know what links you
            dbr.hincrby('mixpanel:stat', 'mixevent', 1)
            dbr.hset('mixpanel:last', 'mixevent', time.time())

            pool.spawn(run, payload)

    pool.join(timeout=30)