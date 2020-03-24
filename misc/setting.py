import os

# gitea_url = 'http://127.0.0.1:3000/api/v1'
# gitea_token = open(os.path.expanduser('~/.gitea-api')).read().strip()
gitea_url = 'http://10.12.218.210:32768/api/v1'
gitea_token = open(os.path.expanduser('~/.csc101-gitea-api')).read().strip()

github_username = 'corenel'
github_token = open(os.path.expanduser('~/.github-token')).read().strip()

gitee_username = 'corenel'
gitee_enterprise = 'csc105'
gitee_url = 'https://gitee.com/api/v5'
gitee_token = open(os.path.expanduser('~/.gitee-token')).read().strip()
