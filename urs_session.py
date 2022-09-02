
"""
Build  session object that can be used with URS. This works only with
the public Earthdata Login. Generalize for use with UAT at some point.

To use this, set up the file 'user.config' with the username and password
and then build a session object using:

    session = SessionEarthData(username=username, password=password)

The session object can be passed into various 
"""
import requests
import configparser

config = configparser.ConfigParser()
config.read('user.config')
username = config['user']['user']
password = config['user']['pwd']


class SessionEarthData(requests.Session):
    AUTH_HOST = 'urs.earthdata.nasa.gov'

    def __init__(self, username, password):
        super().__init__()
        self.auth = (username, password)

    def rebuild_auth(self, prepared_request, response):
        headers = prepared_request.headers
        url = prepared_request.url
        if 'Authorization' in headers:
            original_parsed = requests.utils.urlparse(response.request.url)
            redirect_parsed = requests.utils.urlparse(url)
            if (original_parsed.hostname != redirect_parsed.hostname) and \
                    redirect_parsed.hostname != self.AUTH_HOST and \
                    original_parsed.hostname != self.AUTH_HOST:
                del headers['Authorization']
        return

