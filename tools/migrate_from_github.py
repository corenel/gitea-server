#!/usr/bin/env python

from migrators.github_migrator import GitHubMigrator


def main():
    migrator = GitHubMigrator()
    migrator.migrate_orgs()
    migrator.migrate_repos()


if __name__ == '__main__':
    main()
