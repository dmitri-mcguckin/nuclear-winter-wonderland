#!/usr/bin/env bash

source ./VERSION

DEPS=( pwd rev cut tar 7z wget curl html2text )

BASE_NAME=$(pwd | rev | cut -d/ -f1 | rev)-$PACK_VERSION-$FORGE_VERSION
BASE_URL=https://files.minecraftforge.net/maven/net/minecraftforge/forge/
CLIENT_NAME=$BASE_NAME.zip
SERVER_NAME=$BASE_NAME-server.tar.gz

source ./res/SERVER-OPTIONS

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

# Update the server.properties with the new pack version
LINE=$(awk '/motd/{ print NR; exit  }' res/server.properties)
MOTD=$(cat res/server.properties | grep motd | cut -d= -f2)
MSG=$(echo $MOTD | cut -d\| -f1 | xargs)
PV="NWW $PACK_VERSION"
MV=$(echo $MOTD | cut -d\| -f3 | xargs)
MOTD="motd=$MSG | $PV | $MV"
sed -i "43s/.*/$MOTD/" res/server.properties

# Cleanup old forge
rm -rf res/minecraft_server.*  res/forge-* res/libraries

# Install forge
FORGE_JAR="forge-$MC_VERSION-$FORGE_VERSION-installer.jar"
FORGE_URL="$BASE_URL$MC_VERSION-$FORGE_VERSION/$FORGE_JAR"
echo "Retrieving forge from resource: $FORGE_URL"
wget $FORGE_URL
mv $FORGE_JAR res
cd res
java -jar $FORGE_JAR --installServer

# Post-forge-install-cleanup
rm $FORGE_JAR *.log
cd ..

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

if [[ -n $(command -v uperm) ]]; then uperm -c -r -p 700 -y; fi 
