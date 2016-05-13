import time
import cherrypy
import cherrypy_cors
import base64
import os.path
import requests
from urllib import urlencode
import json
from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow
import httplib2
from threading import Thread
from pymongo import MongoClient
import re
from sets import Set
import categorize

INTERNAL_IP = '10.140.0.3'
EXTERNAL_IP = '130.211.251.145'

clientID = '961180585767-43l499eej0riiqljcla75psc39cavghj.apps.googleusercontent.com'
clientSecret = "TMLV_8rYxLV0vV77U-dD8vxs"
redirectURI = 'http://www.catemail.tk/oauth2callback'
gmailScope = 'https://www.googleapis.com/auth/gmail.readonly'

class CATEmail(object):

  @cherrypy.expose
  def index(self):
    return file('html/index.html')

  # this method runs in a thread created when oauth2callback
  # method is invoked
  def analyze(self, gmail, email):
    # connect to database
    db = MongoClient().catemail
    collection = db.messages
    # create a new thread, pass the code to new thread
    userId = 'me'
    while True:
      # query the max timestamp stamp all the emails belonging to "email" 
      print 'email is ', email
      maxTime = collection.find_one({'email': email}, sort=[("timestamp", -1)])
      if maxTime:
        maxTime = int(maxTime["timestamp"])
        maxTime =int( max(maxTime, 1000 * (time.time() - 24*3600)))
      else:
        maxTime = 1000 * (int(time.time()) - 24*3600)
      print 'before query: ', maxTime
      q = "category:promotions after:%d"%(maxTime/1000)
      response = gmail.users().messages().list(userId = userId, 
                                               q = q).execute()
      
      print ('first query executed:', q)
      cnt = 0
      messages = []
      if 'messages' in response:
        messages.extend(response['messages'])

      while 'nextPageToken' in response:
        pageToken = response['nextPageToken']
        response = gmail.users().messages().list(userId=userId, 
                                q=q,
                                pageToken=pageToken).execute()
        messages.extend(response['messages'])


      for meta in messages:
        # print (meta)
        # check if meta['id'] is already in db before asking google
        message = gmail.users().messages().get(userId = userId, 
                                               id = meta['id']).execute()

        headers = message['payload']['headers']
        subject = ""
        sender = ""
        for header in headers:
          if header['name'] == 'Subject':
            subject = header['value']
          if header['name'] == 'From':
            sender = header['value'] 
    
        timestamp = message['internalDate']
    
        body = ""
        inParts = False
        # find plain text version if it exists
        if 'parts' in message['payload'].keys():
          for part in message['payload']['parts']:
            if 'data' not in part['body']:
              continue;
            inParts = True;
            body = part['body']['data']
            if part['mimeType'] == 'text/plain':
              body = part['body']['data']
              break;
        
        if not inParts:
          if 'data' in message['payload']['body']:      
            # no plain text, use the first available
            body = message['payload']['body']['data']
          else:
            # no data associated with this email
            continue

        # decode message
        body = base64.urlsafe_b64decode(body.encode('ASCII'))

        # remove html tags and css styles here
        body = self.remove_html(body)

        # extract bag of words for classifier
        word_bag = categorize.vocabulary(subject, body)

        #categorize discount or trend
        category = ""
        discount = categorize.categorize_dis_trend(word_bag)
        if discount == '200':
          category = "discount"
        elif discount == "201":
          category = "trend"
        else:
          print "wront classifer"

        #categorize product
        products = categorize.categorize_product(word_bag)
        
        print timestamp, sender, category
        print products
        # after you setup the classifier, use it to calculate the category here
        self.save(collection, email, sender, timestamp, subject, body, category, products);
      #break
      time.sleep(30)

      # check if the thread should continue
      user = db.threads.find_one({'email':email})
      if user['status'] != 'running':
        db.threads.replace_one({'email':email}, {'email':email, 'status':'stopped'})
        break;

    print "done analyzing"

  def save(self, collection, email, sender, timestamp, subject, body, category, products):
    doc = {'email': email,
           'sender': sender,
           'timestamp': timestamp,
           'subject': subject,
           'body': body,
           'category': category,
           'products': products}
    collection.save(doc)

  def remove_html(self, content):
    clean_content = ""
    tag = False
    style = False
    table = False
    for i in range(len(content)):
      if content[i] == "<" and tag == False:
        tag = True
      if content[i] == "{" and style == False:
        style = True
      if content[i] == "[" and table == False:
        table = True
      if ((not tag) and (not style) and not(table)):
        clean_content += content[i]
      if content[i] == ">" and tag == True:
        tag = False
      if content[i] == "}" and style == True:
        style = False
      if content[i] == "]" and table == True:
        table = False
    re.sub("\s+", " ", clean_content)
    return clean_content


  @cherrypy.expose
  def crawler_status(self, email = None):
    db = MongoClient().catemail
    if db.threads.find_one({'email':email, 'status': 'running'}):
      return json.dumps({'status': 'running'});
    else:
      return json.dumps({'status': 'stopped'});

  @cherrypy.expose
  def stop_crawler(self, email = None):
    db = MongoClient().catemail
    user = db.threads.find_one({'email':email, 'status': 'running'})
    print 'stopping crawler for ', email, user
    if user:
      db.threads.replace_one({'email':email}, {'email':email, 'status':'stopping'})
    return 'OK'

  @cherrypy.expose
  def oauth2callback(self, code = None):
    flow = OAuth2WebServerFlow(client_id=clientID,
                               client_secret=clientSecret,
                               scope=gmailScope,
                               redirect_uri=redirectURI)

    credentials = flow.step2_exchange(code)
    http = httplib2.Http()
    http = credentials.authorize(http)
    gmail = build('gmail', 'v1', http=http)
    profile = gmail.users().getProfile(userId='me').execute()
    email = profile['emailAddress']

    print (email)
    # check if user exists
    db = MongoClient().catemail
    user = db.threads.find_one({'email':email})
    data = {'email':email, 'status': 'running'}
    if not user or user['status'] == 'stopped':
      # start a thread to crawl user emails
      thread = Thread(target = self.analyze, args = (gmail, email, ))
      thread.daemon = True
      thread.start()
      if not user:
        db.threads.insert_one(data)
      else:
        db.threads.replace_one({'email':email}, data)
    elif user['status'] == 'stopping':
      db.threads.replace_one({'email':email}, data)
    raise cherrypy.HTTPRedirect("http://www.promotiondigest.tk:3000")
    #raise cherrypy.HTTPRedirect("http://www.catemail.tk")


  @cherrypy.expose
  def get_promotions(self, category = None, products = None):
    print category, products
    db = MongoClient().catemail
    collections = db.messages
    products = products.split('_')
    query = {'category': category, 'products': {'$in': products}}
    res = collections.find(query).sort('timestamp', -1).limit(100)
    ret = []
    for doc in res:
      doc.pop('_id', None)
      ret.append(doc)
    return json.dumps({'status': 'OK', 'data': ret})



if __name__ == '__main__':
  cherrypy_cors.install()
  import sys  
  reload(sys)  
  sys.setdefaultencoding('utf8')

  current_dir = os.path.dirname(os.path.abspath(__file__))
  cherrypy.server.socket_host = INTERNAL_IP
  #cherrypy.config.update({'server.socket_port': 80})
  cherrypy.server.socket_port = 80
  #cherrypy.config.update('config')
  cherrypy.config.update({'environment': 'production',
                          'log.error_file': 'site.log',
                          'cors.expose.on': True,
                          'log.screen': True,
                          'tools.proxy.on': True,
                          'tools.proxy.local': 'X-Forwarded-Host'})

  conf = {'/js': {'tools.staticdir.on':  True,
                  'tools.staticdir.dir': os.path.join(current_dir, 'js')}}
  cherrypy.quickstart(CATEmail(), '/', config=conf)
