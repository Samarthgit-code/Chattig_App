import os
import requests
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.conf import settings

class NextcloudWebDAVStorage(Storage):
    def __init__(self):
        self.base_url = settings.NEXTCLOUD_BASE_URL  # Must end with /
        self.username = settings.NEXTCLOUD_USERNAME
        self.password = settings.NEXTCLOUD_PASSWORD

    def _get_url(self, name):
        return f"{self.base_url}{name}"

    def _ensure_path(self, name):
        path_parts = name.strip('/').split('/')[:-1]
        current_path = self.base_url
        for part in path_parts:
            current_path += f"{part}/"
            response = requests.request("MKCOL", current_path, auth=(self.username, self.password))
            if response.status_code == 409:
                raise Exception(f"Missing parent folder for: {current_path}")
            if response.status_code not in [201, 405]:  # 201=created, 405=exists
                raise Exception(f"Could not create folder {current_path}: {response.status_code} - {response.text}")


    def _open(self, name, mode='rb'):
        url = self._get_url(name)
        response = requests.get(url, auth=(self.username, self.password))
        if response.status_code == 200:
            return ContentFile(response.content)
        raise FileNotFoundError(f"Unable to open {url}")

    def _save(self, name, content):
        self._ensure_path(name)  # ✅ ensure folders exist
        url = self._get_url(name)
        response = requests.put(url, data=content.read(), auth=(self.username, self.password))
        if response.status_code in (201, 204):
            return name
        raise Exception(f"Failed to upload to Nextcloud: {response.status_code} - {response.text}")

    def exists(self, name):
        url = self._get_url(name)
        response = requests.head(url, auth=(self.username, self.password))
        return response.status_code == 200

    def url(self, name):
        return self._get_url(name)
