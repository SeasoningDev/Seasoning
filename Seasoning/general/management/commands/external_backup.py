from django.core.management.base import NoArgsCommand
from oauth2client.client import OAuth2WebServerFlow
from Seasoning.settings import GOOGLE_APP_ID as CLIENT_ID, GOOGLE_SECRET as CLIENT_SECRET, GOOGLE_CREDS_FILE as CRED_FILENAME,\
    DATABASE_DAILY_BACKUP_FILE
import httplib2
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
import pprint
from oauth2client.file import Storage
import datetime

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        """
        This command backs up all the media files and the database to the Seasoning Google Drive
        
        """
        # Check https://developers.google.com/drive/scopes for all available scopes
        OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'
        
        # Redirect URI for installed apps
        REDIRECT_URI = 'https://www.seasoning.be'
        
        # Path to the file to upload
        FILENAME = DATABASE_DAILY_BACKUP_FILE
        
        ### For storing token
        storage = Storage(CRED_FILENAME)
        
        if not storage.get():
            # Run through the OAuth flow and retrieve authorization code
            flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
            authorize_url = flow.step1_get_authorize_url()
            print 'Go to the following link in your browser: ' + authorize_url
            code = raw_input('Enter verification code: ').strip()
            credentials = flow.step2_exchange(code)
        
            ### Storing access token and a refresh token in CRED_FILENAME
            storage.put(credentials)
        else:
            ### Getting access_token,expires_in,token_type,Refresh_toke info from CRED_FILENAME to 'credentials'
            credentials = storage.get()
        
        # Create an httplib2.Http object and authorize it with our credentials
        http = httplib2.Http()
        http = credentials.authorize(http)
        
        drive_service = build('drive', 'v2', http=http)
        
        today = datetime.date.today()
        
        # Insert a file
        media_body = MediaFileUpload(FILENAME, mimetype='text/plain', resumable=True)
        body = {
            'title': 'seasoning-%s.sql.bzip2' % today.strftime('%Y-%m-%d'),
            'description': 'Seasoning database backup for %s' % today.strftime('%d-%m-%Y'),
        }
        
        f = drive_service.files().insert(body=body, media_body=media_body).execute()
