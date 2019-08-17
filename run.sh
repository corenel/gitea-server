#!/usr/bin/env bash

if [[ ! -d gitea ]]; then
  mkdir gitea
fi

if [[ ! -d postgres ]]; then
  mkdir postgres
fi

USER_UID=${UID} USER_GID=${GID} docker-compose up
