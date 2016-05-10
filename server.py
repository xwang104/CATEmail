import cherrypy
import os.path
import requests
from urllib import urlencode
import json
from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow
import httplib2

INTERNAL_IP = '10.140.0.2'
EXTERNAL_IP = '104.155.193.244'

clientID = '961180585767-43l499eej0riiqljcla75psc39cavghj.apps.googleusercontent.com'
clientSecret = "TMLV_8rYxLV0vV77U-dD8vxs"
redirectURI = 'http://www.catemail.tk/oauth2callback'
gmailScope = 'https://www.googleapis.com/auth/gmail.readonly'

class CATEmail(object):
  @cherrypy.expose
  def index(self):
    return file('html/index.html')

  @cherrypy.expose
  def oauth2callback(self, code = None):
    flow = OAuth2WebServerFlow(client_id=clientID,
                               client_secret=clientSecret,
                               scope=gmailScope,
                               redirect_uri=redirectURI)

    #auth_uri = flow.step1_get_authorize_url()
    credentials = flow.step2_exchange(code)
    http = httplib2.Http()
    http = credentials.authorize(http)
    gmail = build('gmail', 'v1', http=http)
    userId = 'me'
    maxResults = 10
    q = "category:promotions after:2016/05/07"
    response = gmail.users().messages().list(userId = userId, 
                                             q = q).execute()
    
    print ('first query executed')
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
      print (meta)
      message = gmail.users().messages().get(userId = userId, 
                                             id = meta['id']).execute()

      headers = message['payload']['headers']
      for header in headers:
        if header['name'] == 'Subject':
          print header['value']
    return 'OK'

    """
    data = {'code': code,
            'client_id': clientID,
            'client_secret': clientSecret,
            'redirect_uri': redirectURI,
            'grant_type': 'authorization_code'}
    url = 'https://accounts.google.com/o/oauth2/token'
    print urlencode(data).encode()
    res = requests.post(url, data)
    print res.content
    return 'OK: ' + urlencode(data).encode() 
    """

  @cherrypy.expose
  @cherrypy.tools.json_out()
  @cherrypy.tools.json_in()
  def token(self):
    print cherrypy.request.json
    return {'status': 'OK'}

if __name__ == '__main__':
  current_dir = os.path.dirname(os.path.abspath(__file__))
  cherrypy.server.socket_host = INTERNAL_IP
  #cherrypy.config.update({'server.socket_port': 80})
  cherrypy.server.socket_port = 80
  #cherrypy.config.update('config')
  cherrypy.config.update({'environment': 'production',
                          'log.error_file': 'site.log',
                          'log.screen': True})

  conf = {'/js': {'tools.staticdir.on':  True,
                  'tools.staticdir.dir': os.path.join(current_dir, 'js')}}
  cherrypy.quickstart(CATEmail(), '/', config=conf)
