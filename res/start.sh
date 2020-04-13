#!/usr/bin/env bash
source ./SERVER-OPTIONS
java -Xmx$MAX_MEMORY -jar "forge-$MC_VERSION-$FORGE_VERSION-universal.jar" nogui
