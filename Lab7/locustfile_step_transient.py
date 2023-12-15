#!/usr/bin/python
#
# Copyright 2018 Google LLC
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

import random
import math
from locust import HttpUser, TaskSet, between, LoadTestShape

products = [
    '0PUK6V6EV0',
    '1YMWWN1N4O',
    '2ZYFJ3GM2N',
    '66VCHSJNUP',
    '6E92ZMYYFZ',
    '9SIQT8TOJO',
    'L9ECAV7KIM',
    'LS4PSXUNUM',
    'OLJCESPC7Z']

def index(l):
    l.client.get("/")

def setCurrency(l):
    currencies = ['EUR', 'USD', 'JPY', 'CAD']
    l.client.post("/setCurrency",
        {'currency_code': random.choice(currencies)})

def browseProduct(l):
    l.client.get("/product/" + random.choice(products))

def viewCart(l):
    l.client.get("/cart")

def addToCart(l):
    product = random.choice(products)
    l.client.get("/product/" + product)
    l.client.post("/cart", {
        'product_id': product,
        'quantity': random.choice([1,2,3,4,5,10])})

def checkout(l):
    addToCart(l)
    l.client.post("/cart/checkout", {
        'email': 'someone@example.com',
        'street_address': '1600 Amphitheatre Parkway',
        'zip_code': '94043',
        'city': 'Mountain View',
        'state': 'CA',
        'country': 'United States',
        'credit_card_number': '4432-8015-6152-0454',
        'credit_card_expiration_month': '1',
        'credit_card_expiration_year': '2039',
        'credit_card_cvv': '672',
    })

class UserBehavior(TaskSet):

    def on_start(self):
        index(self)

    tasks = {index: 1,
        setCurrency: 2,
        browseProduct: 10,
        addToCart: 2,
        viewCart: 3,
        checkout: 1}

import sys, os

def transient_in_effect(run_secs):
    '''
    transient_min_run_secs = [150, 250, 350, 450, 650]
    transient_max_run_secs = [170, 270, 370, 470, 670]
    transient_surge = [200, 200, 100, 100, 100]
    '''

    transient_min_run_secs = [100, 200, 300, 400, 600]
    transient_max_run_secs = [120, 220, 320, 420, 620]
    transient_surge = [150, 150, 80, 80, 80]

    '''
    transient_min_run_secs = [150, 300, 450, 600, 900]
    transient_max_run_secs = [180, 330, 480, 630, 930]
    transient_surge = [100, 150, 200, 250, 300]
    '''


    for i in range(len(transient_min_run_secs)):
        if run_secs >= transient_min_run_secs[i] and run_secs <= transient_max_run_secs[i]:
            print("applying transient of " + str(transient_surge[i]) + " users" )
            return transient_surge[i]
    return 0

class MyCustomShape(LoadTestShape):
    time_limit = int(os.environ.get("TIMELIMIT", 3600))
    spawn_rate = int(os.environ.get("SPAWNRATE", 20))
    max_users = int(os.environ.get("MAXUSERS", 250))
    cycle_time = int(os.environ.get("CYCLETIME", 1200))
    num_steps = int(os.environ.get("NUMSTEPS", 10))

    last_target_users = 0
    current_steps = 0

    print ('Test run time is ', str(time_limit))
    print ('Spawn rate is ', str(spawn_rate))
    print ('Cycle time is ', str(cycle_time))
    print ('Users is ', str(max_users))
    print ('Number of steps is ', str(num_steps))

    seconds_per_step = int(cycle_time / num_steps)
    print ('Seconds per step is ', str(seconds_per_step))
    users_per_step = int(max_users / num_steps) * 2  # have to go up and back down each in half the time
    print ('Users per step is ', str(users_per_step))

    next_update_time = seconds_per_step

    def tick(self):   

        run_time = self.get_run_time()
        print( 'run time = ' + str(run_time) )

        current_users = self.get_current_user_count() 
        print( 'current users = ' + str(current_users) )
        print( 'last_target_users = ' + str(self.last_target_users) )

        if run_time < self.time_limit:
            transient_spike = transient_in_effect(run_time)

            if run_time >= self.next_update_time:
               self.next_update_time = self.next_update_time + self.seconds_per_step
               self.current_steps = self.current_steps + 1
               print ('current step in cycle is ', str(self.current_steps))

               # should we be going up or down?
               if self.current_steps < self.num_steps / 2 + 1:  # still going up
                   target_users = self.last_target_users + self.users_per_step
               else:
                   target_users = self.last_target_users - self.users_per_step
                   if target_users < 0: target_users = 0
                   if self.current_steps == self.num_steps: # time to start next cycle and go back up
                       self.current_steps = 0

               print( 'target users = ' + str(target_users) )
               self.last_target_users = target_users

               return (target_users + transient_spike, self.spawn_rate)
            else:
              return (self.last_target_users + transient_spike, self.spawn_rate)

        return None

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 10)
