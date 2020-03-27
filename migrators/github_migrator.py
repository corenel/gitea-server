from github import Github

from misc import setting
from .base_migrator import BaseMigrator


class GitHubMigrator(BaseMigrator):
    def __init__(self) -> None:
        super().__init__()
        # setup github client
        self.github = Github(setting.github_token)

    def migrate_org(self, name):
        # get org details from gitee
        r = self.github.get_organization(name)
        print(f'migrating organization {r.name} ({r.html_url})')

        # create org in gitea
        msg = {
            "description": r.description,
            "full_name": r.name,
            "location": r.location,
            "repo_admin_change_team_access": True,
            "username": r.login,
            "visibility": "public",
            "website": r.blog
        }
        self.gitea_post(
            msg=msg,
            url=f'/admin/users/{self.gitea_username}/orgs',
        )

    def migrate_user(self, name):
        # get user details from github
        r = self.github.get_user(name)
        print(f'migrating user {r.login} ({r.html_url})')

        # create user in gitea
        msg = {
            "email": r.email,
            "full_name": r.name,
            "login_name": r.login,
            "must_change_password": True,
            "password": "a3sHxzpUjk]JwsFx",
            "send_notify": False,
            "source_id": 0,
            "username": r.login
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

        # get gitea uid
        r = self.gitea_get(url='/user')
        gitea_uid = r['id']

        github_repos = list(self.github.get_user().get_repos())
        for idx, repo in enumerate(github_repos):
            # create org and user if not exists
            if repo.organization is not None:
                if repo.organization.login not in gitea_orgs.keys():
                    self.migrate_org(repo.organization.login)
                    gitea_orgs = {
                        o['username']: o['id']
                        for o in self.gitea_get_orgs()
                    }
                uid = gitea_orgs[repo.owner.login]
            elif repo.owner.login not in gitea_users.keys():
                self.migrate_user(repo.owner.login)
                gitea_users = {
                    u['login']: u['id']
                    for u in self.gitea_get_users()
                }
                uid = gitea_users[repo.owner.login]
            else:
                uid = gitea_uid

            # prepare repo details
            print(f'({idx}/{len(github_repos)}) '
                  f'migrating {repo.full_name} ({repo.clone_url})')
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

            # start repo migration
            self.gitea_post(
                msg=msg,
                url=f'/repos/migrate',
            )
