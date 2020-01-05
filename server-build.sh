#!/usr/bin/env bash

source ./VERSION

DEPS=( pwd rev cut tar wget )
SERVER_NAME=$BASE_NAME-server.tar.gz
MOD_DIR=$MC_HOME/$BASE_NAME/minecraft/mods

source ./res/SERVER-OPTIONS

if [[ -z $MC_HOME ]]; then
  echo -e "Evironment variable MC_HOME must be set in order to build the server!"
  exit -1
elif [[ ! -d $MOD_DIR ]]; then
  echo -e "Client version of the pack must be staged first before building server!"
  exit -1
fi

# Update the server.properties with the new pack version
LINE=$(awk '/motd/{ print NR; exit  }' res/server.properties)
MOTD=$(cat res/server.properties | grep motd | cut -d= -f2)
MSG=$(echo $MOTD | cut -d\| -f1 | xargs)
PV="NWW $PACK_VERSION"
MV=$(echo $MOTD | cut -d\| -f3 | xargs)
MOTD="motd=$MSG | $PV | $MV"
sed -i "43s/.*/$MOTD/" res/server.properties

# Generate dirs if needed
if [[ ! -d ./build ]]; then mkdir build; fi

# Create the server
mkdir staging
cp -r res/* staging
cp -r $MOD_DIR staging

# Cleanup old forge
rm -rf res/minecraft_server.*  res/forge-* res/libraries

# Install forge
FORGE_JAR="forge-$MC_VERSION-$FORGE_VERSION-installer.jar"
FORGE_URL="$BASE_URL$MC_VERSION-$FORGE_VERSION/$FORGE_JAR"
echo "Retrieving forge from resource: $FORGE_URL"
wget $FORGE_URL
mv $FORGE_JAR staging
cd staging
java -jar $FORGE_JAR --installServer

# Post-forge-install-cleanup
rm $FORGE_JAR *.log
cd ..

# Package
tar -C staging -czvf $SERVER_NAME . >> /dev/null
mv $SERVER_NAME build

# Cleanup
rm -rf staging

# Post-build stuff
echo -e "Generated the server: $SERVER_NAME"
if [[ -n $(command -v uperm) ]]; then uperm -c -r -p 700 -y; fi
