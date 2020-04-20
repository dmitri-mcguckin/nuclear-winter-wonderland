#!/usr/bin/env bash
source ./resources.properties
java -Xmx$MAX_MEMORY -jar "forge-$MC_VERSION-$FORGE_VERSION-universal.jar" nogui
