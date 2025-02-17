import orjson
from imapclient import IMAPClient
from urllib.request import urlopen
from imapclient.exceptions import LoginError


class GettingIMAPServerError(Exception):
    ...


def get_imap_server(email: str):
    with urlopen('https://emailsettings.firetrust.com/settings?q=' + email) as response:
        if response.getcode() == 200:
            source = response.read()
            data = orjson.loads(source)
            for i in range(0, len(data["settings"]) + 1):
                if data["settings"][i]["protocol"] == "IMAP":
                    imap_server = data["settings"][i]["address"]
                    return imap_server

    raise GettingIMAPServerError()


def check_password(email: str, password: str):
    try:
        server = get_imap_server(email)
        client = IMAPClient(server).login(username=email, password=password)
    except (LoginError, GettingIMAPServerError):
        return False

    return True
