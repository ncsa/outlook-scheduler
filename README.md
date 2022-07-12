# outlook-scheduler
Schedule events in Outlook 365

# Quick start
## Linux
```
branch=shared_cal
docker run --rm -it --pull always \
--mount type=bind,src=$HOME,dst=/home \
-e NETRC=/home/.ssh/netrc \
-e PYEXCH_REGEX_JSON='{"SICK":"sick"}' \
andylytical/outlook-scheduler:$branch
```

## Inside Docker container
* `./run.sh`
