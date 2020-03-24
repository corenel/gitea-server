#!/usr/bin/env python

from migrators.gitee_migrator import GiteeMigrator


def main():
    migrator = GiteeMigrator()
    migrator.migrate_repos()


if __name__ == '__main__':
    main()
