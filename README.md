# this is my first repo
updated 

## screenshot_sync.py

A small personal tool to take a screenshot on one of your own computers and
sync it to your other computer through this GitHub repo.

**Setup** (on each computer, inside a clone of this repo):

```
pip install mss
```

**Take a screenshot and push it:**

```
python screenshot_sync.py
```

Screenshots are saved under `screenshots/` (named `<hostname>_<timestamp>.png`),
then committed and pushed.

**On your other computer, get the latest screenshots:**

```
python screenshot_sync.py --pull    # or just: git pull
```

Other options: `--no-push` saves locally without pushing.
