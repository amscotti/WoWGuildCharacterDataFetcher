#!/bin/bash

# List from https://www.wowprogress.com/pve/us
declare -a realm_guild_pairs=(
    "Illidan|Liquid"
    "Illidan|BDG"
    "Illidan|BDGG"
    "Mal'Ganis|Instant Dollars"
    "Frostmourne|Honestly"
    "Area 52|xD"
    "Tichondrius|poptart corndoG"
    "Area 52|Vesper"
    "Frostmourne|Ethical"
    "Illidan|Imperative"
    "Zul'jin|vodka"
    "Thrall|Strawberry Puppy Kisses"
    "Area 52|Strawberry Puppy Kisses"
    "Area 52|Infinity"
    "Mal'Ganis|HC"
    "Thrall|Vision"
    "Emerald Dream|Nascent"
    "Tichondrius|Incarnate"
    "Frostmourne|Copium"
    "Sargeras|Humble"
)

for pair in "${realm_guild_pairs[@]}"; do
    IFS='|' read -ra realm_guild <<< "$pair"
    realm=${realm_guild[0]}
    guild=${realm_guild[1]}
    echo "Importing: Realm: $realm, Guild: $guild"
    python import.py "$realm" "$guild"
    echo ""
    sleep 5
done