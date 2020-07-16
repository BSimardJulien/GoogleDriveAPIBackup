from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient.http import MediaFileUpload

import os
import logging

class MyDrive():
    def __init__(self):
        # If modifying these scopes, delete the file token.pickle.
        SCOPES = ['https://www.googleapis.com/auth/drive']
        """Shows basic usage of the Drive v3 API.
        Prints the names and ids of the first 10 files the user has access to.
        """
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('drive', 'v3', credentials=creds)

    def list_files(self, page_size = 10):
        # Call the Drive v3 API
        results = self.service.files().list(
            pageSize=page_size, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            print('No files found.')
        else:
            print('Files:')
            for item in items:
                print(u'{0} ({1})'.format(item['name'], item['id']))

    def upload_file(self,filename,path,logger):
        folder_id = "1MidtHonrkX1Ti1nxJbE3i0XMTtftTX7D"
        media = MediaFileUpload("{}{}".format(path, filename))
        response = self.service.files().list(
                                        q="name='{}' and parents='{}'".format(filename, folder_id),
                                        spaces='drive',
                                        fields='nextPageToken, files(id, name)',
                                        pageToken=None).execute()

        if len(response['files']) == 0:
            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }
            file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            logger.logger.info("Un nouveau dossier a ete cree {}".format(file.get('id')))

        else:
            for file in response.get('files',[]):
                #Changement dans un dossier

                update_file = self.service.files().update(
                    fileId=file.get('id'),
                    media_body=media,
                ).execute()
                logger.logger.info("dossier mise a jour")

class MyLogger():
    def __init__(self):
        LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
        filepath = "D:/Source/Python Project/Backup DB Script/logging.log"

        #create and configure logger
        logging.basicConfig(filename=filepath,
                            level=logging.DEBUG,
                            format=LOG_FORMAT)

        self.logger = logging.getLogger()

    def printOnLog(self,String):
        self.logger.info(String)


def main():
    path = "D:/clb/dat/"
    files = os.listdir(path)

    my_logger = MyLogger()

    my_drive = MyDrive()
    try:
        for item in files:
            if os.path.isdir(path+item):
                path2 = path+ item + "/"
                for item2 in os.listdir(path2):
                    my_drive.upload_file(item2,path2,my_logger)
            else:
                my_drive.upload_file(item,path,my_logger)
        my_logger.logger.info("LE SCRIPT A TERMINE SANS ERREUR")
    except ValueError:
        my_logger.logger.critical("UNE ERREUR CRITIQUE EST SURVENUE")


if __name__ == '__main__':
    main()