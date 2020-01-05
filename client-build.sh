#!/usr/bin/env bash

source ./VERSION

DEPS=( pwd rev cut 7z html2text )
CLIENT_NAME=$BASE_NAME.zip

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
mkdir staging
mkdir staging/overrides
cp manifest.json staging
cp modlist.html staging
cp -r res/config staging/overrides
7z a $CLIENT_NAME staging/. >> /dev/null
mv $CLIENT_NAME build

# Cleanup
rm -rf staging

# Regenerate the readme
echo -e "# Nuclear Winter Wonderland\n\n### Modlist:$(html2text modlist.html)" > README.md

# Post-build stuff
echo -e "Generated the client: $CLIENT_NAME"
if [[ -n $(command -v uperm) ]]; then uperm -c -r -p 700 -y; fi
