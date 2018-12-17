#!/bin/sh

curl https://api.zotero.org/users/4797004/publications/items?linkwrap=1&order=date&sort=desc&start=0&include=data&limit=100&style= \
    | jq '.[] | {date: .date}' 
