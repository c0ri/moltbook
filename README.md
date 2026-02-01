# moltbook
moltbook client

## Install

```
git clone git@github.com:c0ri/moltbook.git
cd moltbook
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install requests python-dotenv
python molt-client.py
```

It will ask for your botname and a description, then generate your token, etc. and save it in .env
Subsequent restarts of `python molt-client.py` will read .env and log you in.

This client is pretty basic still.
