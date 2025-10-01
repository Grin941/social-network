#!/bin/sh

readonly CONTAINER_IP=$(hostname --ip-address)
readonly CONTAINER_API_ADDR="${CONTAINER_IP}:${PATRONI_API_CONNECT_PORT}"
readonly CONTAINER_POSTGRE_ADDR="${CONTAINER_IP}:5432"

export PATRONI_NAME="${PATRONI_NAME:-$(hostname)}"
export PATRONI_RESTAPI_CONNECT_ADDRESS="$CONTAINER_API_ADDR"
export PATRONI_RESTAPI_LISTEN="$CONTAINER_API_ADDR"
export PATRONI_POSTGRESQL_CONNECT_ADDRESS="$CONTAINER_POSTGRE_ADDR"
export PATRONI_POSTGRESQL_LISTEN="$CONTAINER_POSTGRE_ADDR"

cp /patroni.yml /var/lib/postgresql/patroni${PATRONI_NAME}.yml

cat << EOF >> /var/lib/postgresql/patroni${PATRONI_NAME}.yml
  - host replication $PATRONI_REPLICATION_USERNAME 0.0.0.0/0 md5
  post_bootstrap: psql -c "CREATE DATABASE $DB__NAME OWNER $DB__USER;"
EOF

exec /usr/bin/patroni /var/lib/postgresql/patroni${PATRONI_NAME}.yml
