#!/bin/bash
source .env

cd polaris-main/

java -Dquarkus.datasource.jdbc.url=$QUARKUS_DATASOURCE_JDBC_URL_LOCAL \
    -Dquarkus.datasource.username=$QUARKUS_DATASOURCE_USERNAME \
    -Dquarkus.datasource.password=$QUARKUS_DATASOURCE_PASSWORD \
    -jar runtime/admin/build/quarkus-app/quarkus-run.jar \
    bootstrap --realm $REALM --credential $REALM,$CLIENT_ID,$CLIENT_SECRET
