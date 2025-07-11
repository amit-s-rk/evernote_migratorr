import os  
import base64 
import xml.etree.ElementTree as ET  

import google.auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle

def main(input_folder, output_folder):


# if input folder not defined than returnn
    if not os.path.exists(input_folder):
        return

    files = [f for f in os.listdir(input_folder) if f.endswith(".enex")]

    if not files:
        return

    for file in files:
        notebook_name = os.path.splitext(file)[0]
        file_path = os.path.join(input_folder, file)

        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            notes = root.findall("note")
        except:
            continue

        for note in notes:
            title = note.find("title")
            note_title = title.text
            note_folder = os.path.join(output_folder, notebook_name, note_title)
            os.makedirs(note_folder, exist_ok=True)
            resources = note.findall("resource")

            if not resources:
                continue

            for idx, res in enumerate(resources, start=1):
                # resource
                data_element = res.find("data")
                # Resource Type
                mime_element = res.find("mime")

             
                if data_element is None or mime_element is None:
                    continue
                

                mime_type = mime_element.text
                print('mime_type', mime_type)
                # File extentsion
                extension = mime_type.split("/")[-1]
                print('extention', extension)

                file_name = f"{note_title}_{idx}.{extension}" if len(resources) > 1 else f"{note_title}.{extension}"
                print('file name',file_name)
                
                file_path = os.path.join(note_folder, file_name)
                
                try:
                    with open(file_path, "wb") as f:
                        f.write(base64.b64decode(data_element.text))
                except:
                    pass


                
def authenticate_drive():
            SCOPES = ["https://www.googleapis.com/auth/drive"]
            creds = None
            if os.path.exists("token.pickle"):
                with open("token.pickle", "rb") as token:
                    creds = pickle.load(token)
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
                    creds = flow.run_local_server(port=0)
                with open("token.pickle", "wb") as token:
                    pickle.dump(creds, token)
            return build("drive", "v3", credentials=creds)


def create_drive_folder(service, name, parent_id=None):
            file_metadata = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
            if parent_id:
                file_metadata["parents"] = [parent_id]
            folder = service.files().create(body=file_metadata, fields="id").execute()
            return folder["id"]


def upload_file(service, file_path, parent_id):
            file_name = os.path.basename(file_path)
            file_metadata = {"name": file_name, "parents": [parent_id]}
            media = MediaFileUpload(file_path, resumable=True)
            service.files().create(body=file_metadata, media_body=media, fields="id").execute()


def upload_folder_recursive(service, local_path, parent_id=None):
            folder_name = os.path.basename(local_path)
            folder_id = create_drive_folder(service, folder_name, parent_id)
            for item in os.listdir(local_path):
                item_path = os.path.join(local_path, item)
                if os.path.isdir(item_path):
                    upload_folder_recursive(service, item_path, folder_id)
                else:
                    upload_file(service, item_path, folder_id)


if __name__ == "__main__":
    input_folder = "./NoteBooks"
    output_folder = "./Evernote"
    main(input_folder,output_folder)
    drive_service = authenticate_drive()
    upload_folder_recursive(drive_service, output_folder )













