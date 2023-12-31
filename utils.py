from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
from datetime import datetime, timedelta
import socket
import requests
import re


# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/drive",
]


def parse_date_string(s) -> datetime:
    # Read the "s" argument to figure out how many days, hours, and minutes until we remind the user.
    days, hours, minutes = None, None, None
    if "d" in s:
        pattern = "\d+d"
        match = re.search(pattern, s)
        days = str(match.group()).replace("d", "")
    
    if "h" in s:
        print(s)
        pattern = "\d+h"
        match = re.search(pattern, s, flags=re.IGNORECASE)
        hours = str(match.group()).replace("h", "")
    
    if "m" in s:
        pattern = "\d+m"
        match = re.search(pattern, s)
        minutes = str(match.group()).replace("m", "")
    
    # There is a possibility that the user does not enter a day or an hour or a minute. We check for that possiblity here using ternary operators.
    date = datetime.today() + timedelta(
        days=int(days if days else 0),
        hours=int(hours if hours else 0),
        minutes=int(minutes if minutes else 0),
    )
    return date

def convert_date_to_readable_form(date: datetime) -> str:
    return datetime.strftime(date, "%d %B, %I:%M %p")

def set_up_gdrive_api():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=8080)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    socket.setdefaulttimeout(
        3600
    )  # Set the default timeout to 5 minutes. Because uploading large files to GDrive causes error.
    drive = build("drive", "v3", credentials=creds)
    return drive


def upload_to_gdrive(fileObj):
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    drive = set_up_gdrive_api()

    with open(fileObj.filename, "rb") as file:
        metadata = {"name": file.name}
        media = MediaFileUpload(file.name, mimetype="image/jpeg")

        f = drive.files().create(body=metadata, media_body=media, fields="id").execute()

        file_id = f.get("id")
        download_link = f"https://drive.google.com/u/0/uc?id={file_id}&export=download"

        return {"download_link": download_link, "file_id": file_id}


def delete_file_from_google_drive(file_id):
    drive = set_up_gdrive_api()

    deleted_file = drive.files().delete(field=file_id).execute()
    return deleted_file


def delete_downloaded_files():
    for file in os.listdir():
        if file.endswith(".jpg") or file.endswith(".zip"):
            os.remove(file)


def download_attachment(i, attachment):
    url = attachment.url
    response = requests.get(url)
    with open(f"file00{i}-{attachment.filename}", "wb+") as file:
        file.write(response.content)
        return file.name


def change_file_permissions_to_anyone(fileId):
    drive = set_up_gdrive_api()

    file_perms = (
        drive.permissions()
        .create(
            fileId=fileId,
            body={"role": "reader", "type": "anyone"},
        )
        .execute()
    )

    return file_perms
