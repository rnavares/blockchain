**Activate the virtual environment**

```
source venv/bin/activate
```

**Intall packages**

```
pip install -r requirements.txt
```

**Run tests**

Make sure to activate venv

```
python -m pytest backend/tests
```

**Run the app**

Make sure to activate venv

```
python -m backend.app
```

**Run a peer instance**

Make sure to activate venv

```
export PEER=True && python -m backend.app
```

**Run the frontend***

In the frontend directory:

```
npm run start
```

**Seed backend with data**

Make sure to activate venv

```
export SEED_DATA=True && python -m backend.app
```
