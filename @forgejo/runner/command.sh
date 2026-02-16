#!/bin/bash
set -e

if [ -z "$FORGEJO_RUNNER_REGISTRATION_TOKEN" ]; then
    echo 'Waiting for Token...';
    sleep 10;
    exit 1;
fi;

if [ ! -f /data/.runner ]; then
    echo 'First time setup: Registering runner...';
    forgejo-runner register \
        --no-interactive \
        --instance "$FORGEJO_INSTANCE_URL" \
        --token "$FORGEJO_RUNNER_REGISTRATION_TOKEN" \
        --name home-runner \
        --config /data/config.yml;
fi;

echo 'Starting runner daemon...';
exec forgejo-runner daemon --config /data/config.yml;