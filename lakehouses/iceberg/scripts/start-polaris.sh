#!/bin/bash
source .env

cd polaris-main/

./gradlew run -Dquarkus.datasource.db-kind=postgresql \
              -Dpolaris.persistence.type=relational-jdbc \
              -Dquarkus.datasource.username=$QUARKUS_DATASOURCE_USERNAME \
              -Dquarkus.datasource.password=$QUARKUS_DATASOURCE_PASSWORD \
              -Dquarkus.datasource.jdbc.url=$QUARKUS_DATASOURCE_JDBC_URL_LOCAL \
