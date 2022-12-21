import os

import yaml
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


OUTPUT_FOLDER = "generations"


class Drive:

    def __init__(self) -> None:
        pass

    def send(self, data) -> None:
        pass

    def save(self, name: str, msg: str, data: bytes) -> None:
        filename = os.path.join(OUTPUT_FOLDER, name + '.png')
        # filename = name + '.png'

        with open(filename, 'wb') as f:
            f.write(data)


if __name__ == "__main__":
    raise NotImplementedError()
