#!/usr/bin/env python

import migrators
import argparse
import sys
from misc import setting
from misc import util


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f',
                        '--from',
                        dest='source_site',
                        required=True,
                        choices=['gitee', 'github'],
                        help='Source site')
    args = parser.parse_args()

    if args.source_site == 'github':
        print(f'Migrate from Github to self-hosted Gitea')
        print(f'\tGitHub username: {setting.github_username}')
        print(f'\tGitea url: {setting.gitea_url}')
        migrator = migrators.GitHubMigrator()
    elif args.source_site == 'gitee':
        print(f'Migrate from Gitee to self-hosted Gitea')
        print(f'\tGitee username: {setting.gitee_username}')
        print(f'\tGitee enterprise: {setting.gitee_enterprise}')
        print(f'\tGitea url: {setting.gitea_url}')
        migrator = migrators.GiteeMigrator()
    else:
        print(f'Unsupported source site: {args.source_site}')
        sys.exit(1)

    if util.confirm('Are you OK', fg='magenta'):
        migrator.migrate_repos()


if __name__ == '__main__':
    main()
