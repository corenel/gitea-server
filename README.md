# gitea-server
Configurations and scripts for self-built gitea server.

## Prerequisites

- Docker
- Python 3.6 or newer (for migration)
- PyGithub (for migration)

## Usage

### Run in Docker

The following commands will start a gitea server and a database server on local:

```bash
$ cd [path/to/repo]
$ ./scripts/run.sh
```

And expose two ports:

- `3000` for [website](http://localhost:3000/)
- `222` for gitea server SSH tunnel

### Migrate form GitHub

1. create and save your Github token at `~/.github-token` and Gitea token at `~/.gitea-api`

2. Modify `misc/settings.py`

3. Run the following commands to migrate all of your orginazations and repositories:

   ```bash
   $ python3 -m tools.migrate
   ```