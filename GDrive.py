# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 12:10:45 2018

@author: mike.lanza
"""

from __future__ import print_function
from oauth2client import file, client, tools
import sys, os

#creates the authorization class that will run to check the Google Drive Authentication with the information provided
class auth:
    
    def __init__(self,SCOPES,CLIENT_SECRET_FILE,APPLICATION_NAME):
        self.SCOPES = SCOPES
        self.CLIENT_SECRET_FILE = CLIENT_SECRET_FILE
        self.APPLICATION_NAME = APPLICATION_NAME
    
    def getCredentials(self):
        
        ###Gets valid user credentials from storage.
        

        #gets the current working directory where this is being ran from
        cwd_dir = os.path.dirname(os.path.abspath(__file__))
        
        #sets the credentials folder
        credential_dir = os.path.join(cwd_dir, '.credentials')
        #checks if directory exists and if not creates it
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        #creates the filepath for the credentials
        credential_path = os.path.join(credential_dir,'google-drive-credentials.json')
        
        #creates a store for accessing creditials
        store = file.Storage(credential_path)
        credentials = store.get()
        
        #sets the client_secret folder
        client_secret_dir = os.path.join(cwd_dir, 'client_secret')
        #checks if directory exists and if not creates it
        if not os.path.exists(client_secret_dir):
            os.makedirs(client_secret_dir)
        #creates the filepath for the client_secret
        client_secret_path = os.path.join(client_secret_dir,self.CLIENT_SECRET_FILE)
        
        #checks if file exists otherwise exits script
        if not os.path.exists(client_secret_path):
            input('The client_secret.json file is missing from \\client_secret directory. Visit https:/developers.google.com/drive/v2/web/quickstart/python \
for instructions to generate this file and store in the clients_secret directory. \nPress enter to exit')
            sys.exit() 
                
        #if the credentials are non-existant, a flow is created to generate the credentials
        if not credentials or credentials.invalid:
            
            #attempts to grab the client_secrets.json file but if it's not found, instructs user to place it in correct location
            flow = client.flow_from_clientsecrets(client_secret_path, self.SCOPES)
            credentials = tools.run_flow(flow, store)
            print('Storing credentials to ' + credential_path)
        
        #results in the credentials
        return credentials

from httplib2 import Http
import io
from apiclient.discovery import build
from apiclient import errors
from apiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive API Python Quickstart'

#performs authorization
authInst = auth(SCOPES,CLIENT_SECRET_FILE,APPLICATION_NAME)

#gets the credentials for use
credentials = authInst.getCredentials()

#sets up the drive service from which functions can be created
drive_service = build('drive', 'v3', http=credentials.authorize(Http()))

#import pandas to use DataFrames
import pandas as pd

#download file function
def downloadFile(file_id,filepath,mimeType):
    
    #mimeType is the type of document you wish to save it as
    
    #creates the request to download a file using google API
    request= drive_service.files().export_media(fileId=file_id, mimeType = mimeType)
    #sets filehandler
    fh = io.BytesIO()
    #initiates the downloader utilizing the request above
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))
    #once download is complete, write to file
    with io.open(filepath,'wb') as f:
        fh.seek(0)
        f.write(fh.read())

#download file function
def DataFrameDownload(file_id):

    #for using read_csv() to save DataFrame
    mimeType = 'text/csv'
        
    #creates the request to download a file using google API
    request= drive_service.files().export_media(fileId=file_id, mimeType = mimeType)
    #sets filehandler?
    fh = io.BytesIO()
    #initiates the downloader utilizing the request above
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))

    fh.seek(0)
    ###For downloading files with special characters, utf-8 and ISO-8859-1 will work
    return pd.read_csv(fh, index_col=None, encoding = 'utf-8')

#upload file function
def uploadFile(filename,filepath,mimetype):
    file_metadata = {'name': filename}
    media = MediaFileUpload(filepath,
                            mimetype=mimetype)
    file = drive_service.files().create(body=file_metadata,
                                        media_body=media,
                                        fields='id').execute()
    fileID = file.get('id')
    print('File ID: %s Upload Complete!' % fileID)
    return fileID

#update file function
def updateFile(filename,filepath,fileId, mimetype):
    file_metadata = {'name': filename, 'mimeType': mimetype}
    media = MediaFileUpload(filepath,
                            mimetype=mimetype)
    file = drive_service.files().update(fileId = fileId,\
                                          body=file_metadata,\
                                          media_body=media,\
                                          fields='id').execute()
    fileID = file.get('id')
    print('File ID: %s Update Complete!' % fileID)


#upload csv to google sheet function
def df_to_GoogleSheetUpload(dataframe, filename):
    file_metadata = {'name': filename, 'mimeType': 'application/vnd.google-apps.spreadsheet'}
    #must encode to get it to be a bytes object for uploading
    fh = io.BytesIO(dataframe.to_csv(index = False, encoding = 'utf-8').encode('utf-8'))
    media = MediaIoBaseUpload(fh,\
                            mimetype='text/csv',\
                            resumable = False)
    file = drive_service.files().create(body=file_metadata,\
                                          media_body=media,\
                                          fields='id').execute()
    fileID = file.get('id')
    print('File Upload Complete!\nID#: %s' % fileID)

#update google sheet from csv file function
def df_to_GoogleSheetUpdate(dataframe, filename, fileId):
    file_metadata = {'name': filename, 'mimeType': 'application/vnd.google-apps.spreadsheet'}
    #must encode to get it to be a bytes object for uploading
    fh = io.BytesIO(dataframe.to_csv(index = False, encoding = 'utf-8').encode('utf-8'))
    media = MediaIoBaseUpload(fh,\
                            mimetype='text/csv',\
                            resumable = False)
    file = drive_service.files().update(fileId = fileId,\
                                          body=file_metadata,\
                                          media_body=media,\
                                          fields='id').execute()
    fileID = file.get('id')
    print('File Update Complete!\nID#: %s' % fileID)

#function for searching for a file in google drive, returns # of results equal to size
def searchFile(size,query):
    #request for list of fields requested
    results = drive_service.files().list(pageSize=size,\
                                         fields="nextPageToken, files(id, name, parents, kind, mimeType)",\
                                         q=query).execute()
    #resulting list from query
    items = results.get('files', [])
    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print(item)
        return items

#function for searching for a file in google drive, returns # of results equal to size
def getFilename(fileID):
    
    #request for file name from fileIDrequested
    results = drive_service.files().get(fileId=fileID).execute()
    
            
    #resulting list from query
    filename = results.get('name', [])
    if not filename:
        print('No file found.')
    else:
        return filename

#delete file from google drive
def delete_file(file_id):

  try:
    return drive_service.files().delete(fileId=file_id).execute()
    print('File successfully deleted')
  except errors.HttpError as error:
    print('An error occurred: %s' % error)

#function to get MainDriveID 
def getMainDriveID():
    
    #Creates the filename for the file being created
    MainDriveFilename = os.getcwd() + r'\MainDrive.txt'
    
    #creates file to be uploaded to find Main Drive ID
    open(MainDriveFilename,'a').close()
    
    #Gets the File ID for the file which will be deleted
    DeleteFileID = uploadFile(r'MainDrive.txt',MainDriveFilename,'text/plain')
    
    #ID of the Main Drive DO NOT DELETE THIS!!!
    MainDriveID = searchFile(1,'name contains "MainDrive"')[0]['parents'][0]
    
    #Deletes the file
    delete_file(DeleteFileID)
    
    #removes the file from the cwd
    os.remove(MainDriveFilename)
    
    return MainDriveID

def getFolderStructure():
    
    #Get MainDriveID
    MainDriveID = getMainDriveID()
    
    #sets folderquery to get all the Main Directory Folders
    folderquery = 'trashed=False and mimeType = "application/vnd.google-apps.folder" and parents =\'' + MainDriveID + '\''
    
    #initiates the folder structure and the removelist for items to be deleted
    FolderStructure = {'main_dir':{}}
    
    #initializes nextPageToken
    nextPageToken = None
    
    #loop to gather all files and folders on the Main Drive
    #if nextPageToken not empty, gather additional information and apply to items
    while (nextPageToken != None) or (FolderStructure['main_dir'] =={}):
    
        #request for list of fields requested
        results = drive_service.files().list(fields="nextPageToken, files(id, name, parents, kind, mimeType)",\
                                             q=folderquery,\
                                             pageToken=nextPageToken).execute()
        
        #resulting list from query
        nextPageToken = results.get('nextPageToken')
        
        #iterate through list and create file dictionary    
        for i,values in enumerate(results['files']):
    
            FolderStructure['main_dir'][values['name']] = values
    
    #sets subfolderquery for everything else
    subfilequery = 'trashed=False and parents !=\'' + MainDriveID + '\''
    
    #initializes items list
    items = []
    
    #initializes nextPageToken
    nextPageToken = None
    
    #if nextPageToken not empty, gather additional information and apply to items
    while (nextPageToken != None) or (items == []):
    
        #request for list of fields requested
        results = drive_service.files().list(fields="nextPageToken, files(id, name, parents, kind, mimeType)",\
                                             q=subfilequery,\
                                             pageToken=nextPageToken).execute()
        #resulting list from query
        nextPageToken = results.get('nextPageToken')
        
        #appends new results to items
        items = items + results.get('files', [])
    
    #while loop to work through folders and delete them as they are addressed
    while len(items) != 0:
        
        #initializes the currfolder and pathstring as the main_dir
        currfolder = FolderStructure['main_dir']
        pathstring = r'FolderStructure["main_dir"]'
        parentsid = ''
        
        try:
            #sets parentsid to search for
            parentsid = items[0]['parents'][0]
        #if there is no parentid, this is a shared file and should be added to folder
        except KeyError:
            #attempts to add to folder and creates one in the dictionary if it doesn't exist
            try:
                currfolder['SharedWithMe']['children'][items[0]['name']] = items[0]
            except KeyError:
                currfolder['SharedWithMe'] = {}
                currfolder['SharedWithMe']['children'] = {}
                currfolder['SharedWithMe']['id'] = 'SharedWithMe'
                currfolder['SharedWithMe']['name'] = 'SharedWithMe'
                currfolder['SharedWithMe']['parents'] = [MainDriveID]
                currfolder['SharedWithMe']['children'][items[0]['name']] = items[0]
            
            #deletes the item and moves on
            del items[0]
            continue
            
        #checks that the item does not already exist in the MainDrive
        if parentsid==MainDriveID:
            
            #deletes the item from the list and continues to next iteration
            del items[0]
            continue
        
        #initializes the folderlist and level
        folderlist = []
        level = 0
        
        #appends values to the folderlist for the main directory folders
        for key,value in currfolder.items():
             f = [(key,value['id'],level)]
             folderlist= folderlist + f
        
        #while loop to go through folderlist and find the files parent folder
        while len(folderlist) != 0:
            
            #checks if parentsid is equal to the parentid in the folderlist
            if parentsid == currfolder[folderlist[0][0]]['id']:
                
                #tries to set the currfolder children equal to the items but if it doesn't exists it initiates it
                try:
                    currfolder[folderlist[0][0]]['children'][items[0]['name']] = items[0]
                except KeyError:
                    currfolder[folderlist[0][0]]['children'] ={}
                    currfolder[folderlist[0][0]]['children'][items[0]['name']] = items[0]
                
                #since the item was found, the currfolder is set back to the main_dir
                currfolder = FolderStructure['main_dir']
                
                #deletes the item to move onto the next
                del items[0]
                
                #breaks out of searching loop
                break
            
            else:
                
                #checks if the currfolder has any children sets this as the new searching directory
                try:
                    #set the currfolder to the children now
                    currfolder = currfolder[folderlist[0][0]]['children']
                    
                    #updates the pathstring for the children before the folderlist is updated
                    pathstring = pathstring + '["' + folderlist[0][0] + '"]' + '["children"]'
                    
                    #increases the level to the next sub
                    level = level + 1
                    
                    #removes the current folder from the list before getting the children otherwise loop will run endlessly
                    del folderlist[0]
                    
                    #finds all the children and appends them to the top of the folderlist which is being searched through
                    for key,value in currfolder.items():
                        f = [(key,value['id'],level)]
                        folderlist = f + folderlist
                
                #if there aren't any children and the parentid isn't found, move onto the next item in the folderlist
                except KeyError:
                    
                    #checks what the currlevel is to see if we have to go up a level
                    currlevel = folderlist[0][2]
                    
                    #deletes the top value in the folder list
                    del folderlist[0]
                    
                    try:
                        #checks what the next level is
                        nextlevel = folderlist[0][2]
                        
                    #if all folders were searched need to reset
                    except IndexError:
                                            
                        #moves item back to end of list
                        items = items + [items[0]]
                        del items[0]
                        
                        #break out of folderlist search and move onto next item
                        break
                        
                        
                    #if the levels don't match, we have to back out a folder level otherwise no addt action necessary
                    if currlevel != nextlevel:
                        
                        #reduces the level to back out
                        level = level - 1
                        
                        if nextlevel == 0:
                            
                            currfolder = FolderStructure['main_dir']
                            pathstring = r'FolderStructure["main_dir"]'
                        
                        else:
                            
                            #strips out the folder and children from the title of the pathstring
                            pathstring = pathstring[0:pathstring[0:pathstring.rfind(r'["children"]')].rfind('[')]
                            
                            #creates the execution string from the pathfile to set the curr folder
                            executionstring = 'currfolder = ' + pathstring
                            
                            #executes the string
                            exec(executionstring)
    
    #initializes nextPageToken
    nextPageToken = None
    
    #query for getting all files on the MainDrive
    filequery = 'trashed=False and mimeType != "application/vnd.google-apps.folder" and parents =\'' + MainDriveID + '\''
    
    #resets results dictionary
    results = {}
    
    #loop to gather all remaining files on the Main Drive
    #if nextPageToken not empty, gather additional information and apply to items
    while (nextPageToken != None) or (results == {}):
    
        #request for list of fields requested
        results = drive_service.files().list(fields="nextPageToken, files(id, name, parents, kind, mimeType)",\
                                             q=filequery,\
                                             pageToken=nextPageToken).execute()
        
        #resulting list from query
        nextPageToken = results.get('nextPageToken')
        
        #iterate through list and create file dictionary    
        for i,values in enumerate(results['files']):
    
            FolderStructure['main_dir'][values['name']] = values
    
    return FolderStructure
