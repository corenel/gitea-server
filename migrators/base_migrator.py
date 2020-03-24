import requests
import json
import sys

from functools import partial
from misc import setting


class BaseMigrator:
    def __init__(self) -> None:
        super().__init__()

        # set up gitea session
        self.gitea = requests.Session()
        self.gitea.headers.update({
            'Content-type':
            'application/json',
            'Authorization':
            f'token {setting.gitea_token}',
        })

        self.gitea_get = partial(self.get,
                                 session=self.gitea,
                                 base_url=setting.gitea_url)
        self.gitea_post = partial(self.post,
                                  session=self.gitea,
                                  base_url=setting.gitea_url)
        self.gitea_query = partial(self.query, method=self.gitea_get)

        # get gitea uid
        r = self.gitea_get(url='/user')
        self.gitea_uid = r['id']
        self.gitea_username = r['login']

    @staticmethod
    def get(session: requests.Session, base_url: str, url: str):
        r = session.get(f'{base_url}{url}')
        if r.status_code != 200:
            print(f'Cannot get {base_url}{url}', file=sys.stderr)
            exit(1)
        return json.loads(r.text)

    @staticmethod
    def post(session: requests.Session, base_url: str, msg: dict, url: str):
        data = json.dumps(msg)
        r = session.post(f'{base_url}{url}', data=data)
        if r.status_code != 201:  # if not CREATED
            if r.status_code == 409:  # if item already exists
                pass
            print(r.status_code, r.text, data)

    @staticmethod
    def query(method, url):
        page_idx = 0
        results = []
        while True:
            r = method(url=url.format(page_idx))
            if len(r) == 0:
                break
            results.extend(r)
            page_idx += 1
        return results

    def gitea_get_orgs(self):
        return self.gitea_get(url='/admin/orgs')

    def gitea_get_users(self):
        return self.gitea_get(url='/admin/users')
