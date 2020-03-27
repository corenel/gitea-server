from functools import partial

import requests

from misc import setting
from .base_migrator import BaseMigrator


class GiteeMigrator(BaseMigrator):
    def __init__(self) -> None:
        super().__init__()
        # set up gitee session
        self.gitee = requests.Session()
        self.gitee.headers.update({
            'Content-type': 'application/json',
        })
        self.gitee_get = partial(self.get,
                                 session=self.gitee,
                                 base_url=setting.gitee_url)
        self.gitee_post = partial(self.post,
                                  session=self.gitee,
                                  base_url=setting.gitee_url)
        self.gitee_query = partial(self.query, method=self.gitee_get)

    def migrate_org(self, name):
        # get org details from gitee
        r = self.gitee_get(url=f'/orgs/{name}'
                           f'?access_token={setting.gitee_token}')
        print(f'migrating organization {r["login"]} ({r["url"]})')

        # create org in gitea
        msg = {
            "description": r['description'],
            "full_name": r['name'],
            "location": r['location'],
            "repo_admin_change_team_access": True,
            "username": r['login'],
            "visibility": "public",
            "website": r['url']
        }
        self.gitea_post(
            msg=msg,
            url=f'/admin/users/{self.gitea_username}/orgs',
        )

    def migrate_user(self, name):
        # get user details from gitee
        r = self.gitee_get(url=f'/users/{name}'
                           f'?access_token={setting.gitee_token}')
        print(f'migrating user {r["login"]} ({r["url"]})')

        # create user in gitea
        msg = {
            "email": f'{r["login"]}@zju.edu.cn',
            "full_name": r['name'],
            "login_name": r['login'],
            "must_change_password": True,
            "password": "a3sHxzpUjk]JwsFx",
            "send_notify": False,
            "source_id": 0,
            "username": r['login']
        }
        self.gitea_post(
            msg=msg,
            url=f'/admin/users',
        )

    def migrate_repos(self):
        # get existed organizations on gitea
        gitea_orgs = {o['username']: o['id'] for o in self.gitea_get_orgs()}

        # get existed users on gitea
        gitea_users = {u['login']: u['id'] for u in self.gitea_get_users()}

        # get repos in the enterprise on gitee
        gitee_repos = self.gitee_query(
            url=f'/enterprises/{setting.gitee_enterprise}/repos'
            f'?access_token={setting.gitee_token}'
            '&type=all&per_page=100&page={}')
        print(
            f'#repos in enterprise {setting.gitee_enterprise}: {len(gitee_repos)}'
        )

        # migrate repos from gitee to gitea
        for idx, gitee_repo in enumerate(gitee_repos):
            if gitee_repo['namespace']['type'] == 'group':
                # create organization if not exist
                if gitee_repo['namespace']['path'] not in gitea_orgs.keys():
                    self.migrate_org(gitee_repo['namespace']['path'])
                    gitea_orgs = {
                        o['username']: o['id']
                        for o in self.gitea_get_orgs()
                    }
                # use org's uid
                gitea_uid = gitea_orgs[gitee_repo['namespace']['path']]
            # create user if not exist
            elif gitee_repo['namespace']['type'] == 'personal':
                if gitee_repo['namespace']['path'] not in gitea_users.keys():
                    self.migrate_user(gitee_repo['namespace']['path'])
                    gitea_users = {
                        u['login']: u['id']
                        for u in self.gitea_get_users()
                    }
                # use user's uid
                gitea_uid = gitea_users[gitee_repo['namespace']['path']]
            # create owner account if the repo is directly in the enterprise
            elif gitee_repo['namespace']['type'] == 'enterprise' and \
                    gitee_repo['owner']['login'] not in gitea_users.keys():
                self.migrate_user(gitee_repo['owner']['login'])
                gitea_users = {
                    u['login']: u['id']
                    for u in self.gitea_get_users()
                }
                # use owner's uid
                gitea_uid = gitea_users[gitee_repo['owner']['login']]
            else:
                # use owner's uid
                gitea_uid = gitea_users[gitee_repo['owner']['login']]

            # determine repo desc
            if gitee_repo['description'] != '' and gitee_repo['name'] != '':
                gitea_desc = f'({gitee_repo["name"]}) {gitee_repo["description"]}'
            elif gitee_repo['description'] != '':
                gitea_desc = gitee_repo['description']
            elif gitee_repo['name'] != '':
                # use chinese repo name as desc
                gitea_desc = gitee_repo['name']
            else:
                gitea_desc = 'not really known'

            # prepare repo details
            print(
                f'({idx}/{len(gitee_repos)}) '
                f'migrating {gitee_repo["full_name"]} ({gitee_repo["html_url"]})'
            )
            msg = {
                'repo_name': gitee_repo['path'],
                'description': gitea_desc,
                'clone_addr': gitee_repo['html_url'],
                'mirror': True,
                'private': gitee_repo['private'],
                'uid': gitea_uid,
                "auth_username": setting.gitee_username,
                "auth_password": f'{setting.gitee_token}'
            }

            # start repo migration
            self.gitea_post(
                msg=msg,
                url=f'/repos/migrate',
            )
