import os  
import base64 
import xml.etree.ElementTree as ET  


def main():
    input_folder = "./NoteBooks"
    output_folder = "./Evernote"

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



if __name__ == "__main__":
    main()
