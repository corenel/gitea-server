#!/usr/bin/env python -B

from github import Github
import requests
import json
import sys
import os

import setting

if __name__ == '__main__':
    session = requests.Session()  # Gitea
    session.headers.update({
        'Content-type': 'application/json',
        'Authorization': f'token {setting.gitea_token}',
    })

    r = session.get(f'{setting.gitea_url}/user')
    if r.status_code != 200:
        print('Cannot get user details', file=sys.stderr)
        exit(1)

    gitea_uid = json.loads(r.text)["id"]

    gh = Github(setting.github_token)

    for repo in gh.get_user().get_repos():
        # Mirror to Gitea if I haven't forked this repository from elsewhere
        # if not repo.fork:
        if True:
            print(f'migrating {repo.full_name} ({repo.clone_url})')
            m = {
                'repo_name':
                    repo.full_name.replace('/', '-'),
                'description':
                    repo.description or "not really known",
                'clone_addr':
                    repo.clone_url.replace(
                        '//', f'//{setting.github_token}:x-oauth-basic@'),
                'mirror':
                    True,
                'private':
                    repo.private,
                'uid':
                    gitea_uid,
            }

            # if repo.private:
            #     m["auth_username"] = setting.github_username
            #     m["auth_password"] = "{0}".format(setting.github_token)

            jsonstring = json.dumps(m)

            r = session.post(f'{setting.gitea_url}/repos/migrate',
                             data=jsonstring)
            if r.status_code != 201:  # if not CREATED
                if r.status_code == 409:  # repository exists
                    continue
                print(r.status_code, r.text, jsonstring)
