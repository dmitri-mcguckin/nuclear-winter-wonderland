#!/usr/bin/env bash

source ./VERSION

DEPS=( pwd rev cut tar 7z curl html2text )

BASE_NAME=$(pwd | rev | cut -d/ -f1 | rev)-$PACK_VERSION-$FORGE_VERSION
CLIENT_NAME=$BASE_NAME.zip
SERVER_NAME=$BASE_NAME-server.tar.gz

# Dependency check
for dep in ${DEPS[@]}; do
  if [[ -z $(command -v $dep) ]]; then
    echo "$dep must be installed to build!"
    exit -1
  fi
done

# Generate dirs if needed
if [[ ! -d ./build ]]; then mkdir build; fi

# Create the client
mkdir client_build
mkdir client_build/overrides
cp manifest.json client_build
cp modlist.html client_build
cp -r res/config client_build/overrides
7z a $CLIENT_NAME client_build/. >> /dev/null
mv $CLIENT_NAME build

# Create the server
cp -r res server_build
# TODO: Find a way to download via curses janky af API
tar -C server_build -czvf $SERVER_NAME . >> /dev/null
mv $SERVER_NAME build

# Cleanup
rm -rf client_build server_build

# Regenerate the readme
echo -e "# Nuclear Winter Wonderland\n\n### Modlist:$(html2text modlist.html)" > README.md

echo -e "Made files:\n\t$CLIENT_NAME\n\t$SERVER_NAME"
