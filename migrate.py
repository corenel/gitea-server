#!/usr/bin/env python -B

from github import Github  # https://github.com/PyGithub/PyGithub
import requests
import json
import sys
import os

gitea_url = "http://127.0.0.1:3000/api/v1"
gitea_token = open(os.path.expanduser("~/.gitea-api")).read().strip()

session = requests.Session()  # Gitea
session.headers.update({
    "Content-type": "application/json",
    "Authorization": "token {0}".format(gitea_token),
})

r = session.get("{0}/user".format(gitea_url))
if r.status_code != 200:
    print("Cannot get user details", file=sys.stderr)
    exit(1)

gitea_uid = json.loads(r.text)["id"]

github_username = "corenel"
github_token = open(os.path.expanduser("~/.github-token")).read().strip()
gh = Github(github_token)

for repo in gh.get_user().get_repos():
    # Mirror to Gitea if I haven't forked this repository from elsewhere
    # if not repo.fork:
    if True:
        m = {
            "repo_name": repo.full_name.replace("/", "-"),
            "description": repo.description or "not really known",
            "clone_addr": repo.clone_url,
            "mirror": True,
            "private": repo.private,
            "uid": gitea_uid,
        }

        if repo.private:
            m["auth_username"] = github_username
            m["auth_password"] = "{0}".format(github_token)

        jsonstring = json.dumps(m)

        r = session.post("{0}/repos/migrate".format(gitea_url),
                         data=jsonstring)
        if r.status_code != 201:  # if not CREATED
            if r.status_code == 409:  # repository exists
                continue
            print(r.status_code, r.text, jsonstring)
