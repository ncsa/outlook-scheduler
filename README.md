# outlook-scheduler
Schedule events in Outlook 365

# Quick start
## Linux
```
d_username=andylytical
d_image=outlook-scheduler
branch=shared_cal

docker run --rm -it --pull always \
--mount type=bind,src=$HOME,dst=/home \
-e NETRC=/home/.ssh/netrc \
-e PYEXCH_REGEX_JSON='{"ALL":""}' \
${d_username}/${d_image}:${branch}
```

## Inside Docker container
* `./run.sh`
