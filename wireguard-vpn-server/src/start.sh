#!/bin/bash

set -e

wg-quick up wg0

trap 'wg-quick down wg0; exit 0' SIGTERM

while :; do
    sleep 3600 &
    wait $!
done