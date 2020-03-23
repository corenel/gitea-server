import os

gitea_url = "http://127.0.0.1:3000/api/v1"
gitea_token = open(os.path.expanduser("~/.gitea-api")).read().strip()

github_username = "corenel"
github_token = open(os.path.expanduser("~/.github-token")).read().strip()
