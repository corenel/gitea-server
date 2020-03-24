#!/usr/bin/env python

from tools.migrator import Migrator


def main():
    migrator = Migrator()
    migrator.migrate_repos()


if __name__ == '__main__':
    main()
