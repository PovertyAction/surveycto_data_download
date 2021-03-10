import ijson
import pandas as pd
import os
import sys
import requests
import ntpath
import time

def get_list_files(dir_path):
    if os.path.isdir(dir_path):
        only_files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
        return only_files
    else:
        print(f'{dir_path} is not a directory')
        return False

def download_file_from_surveycto(file_url, file_path_where_save, username, password):

    try:
        headers = {'X-OpenRosa-Version': '1.0'}
        auth_basic = requests.auth.HTTPBasicAuth(
            username=username, password=password)

        response = requests.get(file_url,
                             headers = headers,
                             auth = auth_basic)

        #Check if error status code
        if response.status_code == 500:
            print(f'Error {response.status_code} when downloading {file_url}')
            print(response.text)
            return False

        #Save response content in file
        data = response.content

        f = open(file_path_where_save, 'wb')
        f.write(data)
        f.close()
        return file_path_where_save

    except Exception as e:
        print("An exception occurred")
        print(e)
        return False

def download_survey_entries(start_day_timespam, server_name, form_id, username, password, dir_where_to_save):

    file_url = f'https://{server_name}.surveycto.com/api/v2/forms/data/wide/json/{form_id}?date={start_day_timespam}'

    now_timespam = int(time.time())
    file_path_where_save = os.path.join(dir_where_to_save,f'{server_name}-{form_id}-{start_day_timespam}_{now_timespam}.json')

    return download_file_from_surveycto(file_url, file_path_where_save, username, password)

def download_attachments(json_file, attachment_columns, dir_path_where_save, username, password):

    files_in_dir = get_list_files(dir_path_where_save)
    if files_in_dir is False:
        print(f'Could not read files from folder {dir_path_where_save}')
    else:
        print(f'Files found in folder {dir_path_where_save}: {files_in_dir}')

    with open(json_file, 'rb') as input_file:
        # load json iteratively
        parser = ijson.parse(input_file)
        for prefix, event, value in parser:
            #Check if prefix we are reading is a json key
            #We know json keys come in the shape "prefix.key"
            if len(prefix.split('.'))>1:
                key = prefix.split('.')[1]

                #Check if key is associated to one of columns with urls to download
                if key in attachment_columns and value !='':

                    #Get file_name
                    file_name = ntpath.basename(value)
                    print('---')
                    print(f'Working on {file_name}')

                    #Check if file already exist in dir_path_where_save. If it does, move to next one.
                    if file_name in files_in_dir:
                        print(f'{file_name} already in {files_in_dir}, skipping')
                        continue

                    #Else, proceed to download

                    #Download file to local if it doesnt exist already
                    file_path = os.path.join(dir_path_where_save, file_name)

                    download_status = download_file_from_surveycto(file_url=value, file_path_where_save=file_path, username=username, password=password)
                    if download_status:
                        print(f'{file_path} succesfully downloaded to boxcryptor folder')
                    else:
                        print(f'Error downloading {file_path} from SurveyCTO. Moving to next one')
                        continue


#python surveycto_data_downloader.py '1615378426' 'bdmaskrct' 'maskrct_phone_followup' $env:SURVEYCTO_USERNAME $env:SURVEYCTO_PASSWORD 'X:\\Box Sync\\MASK Test folder' 'X:\\Box Sync\\MASK Test folder\\media'
if __name__ == '__main__':

    start_day_timespam = sys.argv[1]
    server_name = sys.argv[2]
    form_id = sys.argv[3]
    username=sys.argv[4]
    password=sys.argv[5]
    survey_entries_path_destination=sys.argv[6]
    media_path_destination=sys.argv[7]

    attachment_columns = ['text_audit', 'audio_audit']

    survey_entries_file_name = download_survey_entries(
        start_day_timespam=start_day_timespam,
        server_name=server_name,
        form_id=form_id,
        username=username,
        password=password,
        dir_where_to_save=survey_entries_path_destination
        )

    # download_attachments(
    #     json_file = survey_entries_file_name,
    #     attachment_columns = attachment_columns,
    #     dir_path_where_save= media_path_destination,
    #     username=username,
    #     password=password)




#Deprecated
'''
def safe_delete(file_path):
    try:
        os.remove(file_path)
        return True
    except Excepion as e:
        print("An exception occurred")
        print(e)
        return False


def download_attachments_and_upload_to_box_using_box_api(json_filename, attachment_columns, box_folder_id):

    files_in_box = box_manager.get_list_files(box_folder_id)
    if files_in_box is False:
        print(f'Could not read files from folder {box_folder_id}')
    else:
        print(f'Files found in box folder {box_folder_id}: {files_in_box}')

    with open(json_filename, 'rb') as input_file:
        # load json iteratively
        parser = ijson.parse(input_file)
        for prefix, event, value in parser:
            #Check if prefix we are reading is a json key
            #We know json keys come in the shape "prefix.key"
            if len(prefix.split('.'))>1:
                key = prefix.split('.')[1]

                #Check if key is associated to one of columns with urls to download
                if key in attachment_columns and value !='':

                    #Get file_name
                    file_name = ntpath.basename(value)
                    print('---')
                    print(f'Working on {file_name}')

                    #Check if file already exist in box. If it does, move to next one.
                    if file_name in files_in_box:
                        print(f'{file_name} already in box, skipping')
                        continue

                    #Else, proceed to download to local, upload to Box, delete from local

                    #Download file to local if it doesnt exist already
                    file_path = os.path.join('attachments',file_name)

                    if os.path.isfile(file_path):
                        print(f'{file_path} already downloaded')
                    else:
                        download_status = download_file_from_surveycto(file_url=value, file_path=file_path)
                        if download_status:
                            print(f'{file_path} succesfully downloaded to local')
                        else:
                            print(f'Error downloading {file_path} from SurveyCTO. Moving to next one')
                            continue

                    #Upload file to box
                    upload_status = box_manager.upload_file(box_folder_id, file_path)
                    if upload_status:
                        print(f'{file_path} succesfully uploaded to Box')
                    else:
                        print(f'Error uploading {file_path} to Box. Moving to next one')
                        continue

                    #Delete file from local
                    delete_status = safe_delete(file_path)
                    if delete_status:
                        print(f'{file_path} deleted from local')
                    else:
                        print(f'Error deleting {file_path}. Moving to next one')
                        continue
'''