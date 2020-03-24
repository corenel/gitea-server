import json

from github import Github

from misc import setting
from .base_migrator import BaseMigrator


class GitHubMigrator(BaseMigrator):
    def __init__(self) -> None:
        super().__init__()
        # setup github client
        self.github = Github(setting.github_token)

    def migrate_orgs(self):
        # get existed organizations on gitea
        r = self.gitea_get(url='/admin/orgs')
        gitea_orgs = [o['username'] for o in r]

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
                    msg=msg,
                    url=f'/admin/users/{self.gitea_username}/orgs',
                )

    def migrate_repos(self):
        # get existed organizations on gitea
        r = self.gitea_get(url='/admin/orgs')
        gitea_orgs = {o['username']: o['id'] for o in r}

        # get gitea uid
        r = self.gitea_get(url='/user')
        gitea_uid = r['id']

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
                msg=msg,
                url=f'/repos/migrate',
            )
