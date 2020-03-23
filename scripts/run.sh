#!/usr/bin/env bash

if [[ ! -d data/gitea ]]; then
  mkdir -p data/gitea
fi

if [[ ! -d data/postgres ]]; then
  mkdir data/postgres
fi

USER_UID=${UID} USER_GID=${GID} docker-compose up
