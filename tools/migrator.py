from github import Github
import requests
import json
import sys

from tools import setting


class Migrator:
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

        # get gitea uid
        r = self.gitea.get(f'{setting.gitea_url}/user')
        if r.status_code != 200:
            print('Cannot get user details', file=sys.stderr)
            exit(1)
        self.gitea_uid = json.loads(r.text)['id']
        self.gitea_username = json.loads(r.text)['login']

        # setup github client
        self.github = Github(setting.github_token)

    def gitea_get(self, url):
        r = self.gitea.get(url)
        if r.status_code != 200:
            print(f'Cannot get {url}', file=sys.stderr)
            exit(1)
        return r

    def gitea_post(self, msg: dict, url: str):
        data = json.dumps(msg)
        r = self.gitea.post(url, data=data)
        if r.status_code != 201:  # if not CREATED
            if r.status_code == 409:  # item already exists
                pass
            print(r.status_code, r.text, data)

    def migrate_orgs(self):
        # get existed organizations on gitea
        r = self.gitea_get(f'{setting.gitea_url}/admin/orgs')
        gitea_orgs = [o['username'] for o in json.loads(r.text)]

        # get gitea username
        r = self.gitea_get(f'{setting.gitea_url}/user')
        gitea_username = json.loads(r.text)['login']

        # migrate organizations from github to gitea
        for org in self.github.get_user().get_orgs():
            if org.login not in gitea_orgs:
                print(f'migrating organization {org.login} ({org.html_url})')
                msg = {
                    "description": org.description,
                    "full_name": org.name,
                    "location": org.location,
                    "repo_admin_change_team_access": True,
                    "username": org.login,
                    "visibility": "public",
                    "website": org.blog
                }
                self.gitea_post(
                    msg,
                    f'{setting.gitea_url}/admin/users/{gitea_username}/orgs',
                )

    def migrate_repos(self):
        # get existed organizations on gitea
        r = self.gitea_get(f'{setting.gitea_url}/admin/orgs')
        gitea_orgs = {o['username']: o['id'] for o in json.loads(r.text)}

        # get gitea uid
        r = self.gitea_get(f'{setting.gitea_url}/user')
        gitea_uid = json.loads(r.text)['id']

        for repo in self.github.get_user().get_repos():
            # Mirror to Gitea if I haven't forked this repository from elsewhere
            # if not repo.fork:
            if repo.owner.login in gitea_orgs.keys():
                uid = gitea_orgs[repo.owner.login]
            else:
                uid = gitea_uid
            print(f'migrating {repo.full_name} ({repo.clone_url})')
            msg = {
                'repo_name':
                repo.name,
                'description':
                repo.description or 'not really known',
                'clone_addr':
                repo.clone_url.replace(
                    '//', f'//{setting.github_token}:x-oauth-basic@'),
                'mirror':
                True,
                'private':
                repo.private,
                'uid':
                uid,
            }

            if repo.private:
                msg["auth_username"] = setting.github_username
                msg["auth_password"] = "{0}".format(setting.github_token)

            self.gitea_post(
                msg,
                f'{setting.gitea_url}/repos/migrate',
            )
