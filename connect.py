import json
import requests
import time
import os
import utils
import uuid
from selenium import webdriver

import configs

graph_api_endpoint = 'https://graph.microsoft.com/v1.0{0}'
create_folder_url = "/drive/root/{parent_path}children"
create_folder_method = "POST"
list_children_url = "/drive/root:/{item_path}:/children"
list_children_method = "GET"
download_file_url = "/drive/root:/{item_path}/{item_name}:/content"
download_file_accept = "text/plain"
download_file_method = "GET"
upload_file_url = "/drive/root:/{item_path}/{item_name}:/content"
upload_file_method = "PUT"
upload_file_content_type = "text/plain"
authorize_url = 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize'
token_url = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'


class OnedriveException(Exception):
    def __init__(self, action, status_code, url, method, message):
        message = "{}: {} {} {}, {}".format(action, method, status_code, url, message)
        super(OnedriveException, self).__init__(message)
        self.action = action
        self.url = url
        self.method = method
        self.status_code = status_code


class OnedriveStorage(object):
    def __init__(self):
        self.recorder_path = "recorder"
        self.logger = utils.init_logger("OnedriveStorage")
        if os.path.isfile(configs.access_token_path):
            with open(configs.access_token_path) as fin:
                self.access_token = fin.readline()
        else:
            self.access_token = self.authorize()
        self.headers_template = {
            'Authorization': 'Bearer {0}'.format(self.access_token),
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'client-request-id': None,
            'return-client-request-id': 'true'
        }
        self.check_authorize()

    def authorize(self):
        data = {
            'client_id': configs.client_id,
            'response_type': 'token',
            'redirect_uri': 'https://login.microsoftonline.com/common/oauth2/nativeclient',
            "scope": "files.readwrite.all"
        }
        url = authorize_url + "?"
        for key in data:
            url += key + "=" + str(data[key]) + "&"
        url = url[:-1]
        # script_path = os.path.split(os.path.realpath(__file__))[0]
        # firefox = webdriver.Firefox(executable_path=script_path + "/geckodriver")
        firefox = webdriver.Firefox()
        firefox.get(url)
        prefix = "https://login.microsoftonline.com/common/oauth2/nativeclient#access_token="
        while not firefox.current_url.startswith(prefix):
            time.sleep(0.1)
        access_token = firefox.current_url[len(prefix): firefox.current_url.index('&')]
        try:
            firefox.quit()
        except Exception as e:
            self.logger.error(utils.describe_error(e))
        return access_token

    def check_authorize(self):
        try:
            self.list_recorder_folder()
        except OnedriveException as e:
            print "Invalid Access Token"
            self.access_token = self.authorize()
            self.headers_template["Authorization"] = 'Bearer {0}'.format(self.access_token)
        with open(configs.access_token_path, "w") as fout:
            fout.write(self.access_token)

    def list_children(self, item_path):
        headers = self.headers_template.copy()
        headers["client-request-id"] = str(uuid.uuid4())
        resource = list_children_url.format(**{"item_path": item_path})
        url = graph_api_endpoint.format(resource)
        response = requests.request(list_children_method, url, headers=headers)
        if response.status_code / 100 != 2:
            raise OnedriveException("list_children", response.status_code, url, list_children_method, response.text)
        content = json.loads(response.content)
        ans = [f['name'] for f in content["value"]]
        return ans

    def list_recorder_folder(self):
        return self.list_children(self.recorder_path)

    def create_folder(self, parent_path, folder_name):
        parent_path = parent_path.strip()
        if len(parent_path) > 0 and not parent_path.endswith('/'):
            parent_path += '/'
        headers = self.headers_template.copy()
        headers["client-request-id"] = str(uuid.uuid4())
        resource = create_folder_url.format(**{"parent_path": parent_path})
        data = {
            "name": folder_name,
            "folder": {"childCount": 0}
        }
        url = graph_api_endpoint.format(resource)
        response = requests.request(create_folder_method, url, headers=headers, data=data)
        if response.status_code / 100 != 2:
            raise OnedriveException("create_folder", response.status_code, url, create_folder_method, response.text)
        content = json.loads(response.content)
        ans = [f['name'] for f in content["value"]]
        return ans

    def create_recorder_folder(self):
        return self.create_folder(self.recorder_path[:self.recorder_path.rindex("/" + 1)] if "/" in self.recorder_path
                                  else "", self.recorder_path)

    def exist_recorder_file(self, name):
        return name in self.list_recorder_folder()

    def download_file(self, item_path, item_name):
        headers = self.headers_template.copy()
        headers["Accept"] = download_file_accept
        headers["client-request-id"] = str(uuid.uuid4())
        resource = download_file_url.format(**{"item_path": item_path, "item_name": item_name})
        url = graph_api_endpoint.format(resource)
        response = requests.request(download_file_method, url, headers=headers)
        if response.status_code / 100 != 2:
            raise OnedriveException("download_file", response.status_code, url, download_file_method, response.text)
        return response.content

    def download_recorder_file(self, item_name):
        return self.download_file(self.recorder_path, item_name)

    def get_recorder_file_content(self, item_name, empty=None):
        if self.exist_recorder_file(item_name):
            return json.loads(self.download_recorder_file(item_name))
        return empty

    def upload_file(self, item_path, item_name, content):
        headers = self.headers_template.copy()
        headers["Content-Type"] = upload_file_content_type
        headers["client-request-id"] = str(uuid.uuid4())
        resource = upload_file_url.format(**{"item_path": item_path, "item_name": item_name})
        url = graph_api_endpoint.format(resource)
        response = requests.request(upload_file_method, url, headers=headers, data=content)
        if response.status_code / 100 != 2:
            raise OnedriveException("upload_file", response.status_code, url, upload_file_method, response.text)

    def upload_recorder_file(self, item_name, content):
        return self.upload_file(self.recorder_path, item_name, content)

    def save_recorder_file_content(self, item_name, content):
        if not isinstance(content, unicode):
            if isinstance(content, list) or isinstance(content, dict):
                content = json.dumps(content)
            else:
                content = unicode(content)
        return self.upload_recorder_file(item_name, content)

    def refresh_authorize(self):
        self.access_token = self.authorize()


class OnedriveStorageHolder(object):
    def __init__(self):
        self.storage = OnedriveStorage()

    def get_storage(self):
        return self.storage

holder = OnedriveStorageHolder()

if __name__ == "__main__":
    storage = OnedriveStorage()
    print storage.list_recorder_folder()
    print storage.exist_recorder_file("1.txt")
    print storage.upload_recorder_file("1.txt", '["hello"]')
    print storage.get_recorder_file_content("1.txt")
    print storage.list_recorder_folder()

