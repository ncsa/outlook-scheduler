# outlook-scheduler
Schedule events in Outlook 365

# Quick start
## Linux
```
docker run --rm -it --pull always \
--mount type=bind,src=$HOME,dst=/home \
-e NETRC=/home/.ssh/netrc \
-e PYEXCH_REGEX_JSON='{"SICK":"sick"}'
andylytical/outlook-scheduler:main
```

## Inside Docker container
* `./run.sh`
