#!/bin/bash
source .env

storage_location="file:///var/tmp/$CATALOG_NAME/"
storage_config_info="{\"storageType\": \"FILE\", \"allowedLocations\": [\"$storage_location\"]}"

TOKEN=$(curl -s $CATALOG_URI/v1/oauth/tokens \
  --user ${CLIENT_ID}:${CLIENT_SECRET} \
  -H "Polaris-Realm: $REALM" \
  -d grant_type=client_credentials \
  -d scope=PRINCIPAL_ROLE:ALL | jq -r .access_token)

if [ -z "${TOKEN}" ]; then
  echo "Failed to obtain access token."
  exit 1
fi

echo Token is $TOKEN

echo Creating a catalog named $CATALOG_NAME in realm $REALM...

PAYLOAD='{
   "catalog": {
     "name": "'$CATALOG_NAME'",
     "type": "INTERNAL",
     "readOnly": false,
     "properties": {
       "default-base-location": "'$storage_location'"
     },
     "storageConfigInfo": '$storage_config_info'
   }
 }'

echo $PAYLOAD

curl -s -H "Authorization: Bearer ${TOKEN}" \
   -H 'Accept: application/json' \
   -H 'Content-Type: application/json' \
   -H "Polaris-Realm: $realm" \
   http://localhost:8181/api/management/v1/catalogs \
   -d "$PAYLOAD" -v

echo
echo Done.