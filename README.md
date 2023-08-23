# atm
Example ATM service with FastAPI
## Prerequisites
* Poetry 
* Docker
* Python >3.10
## Build
```bash
poetry install
```
## Run
### Start mongo
```bash
docker run -d -p 27017:27017 mongo
```
### Start service - dev mode
```bash
poetry run dev
```

## Configuration
You can set env variable `MONGODB_URI` to override the default `localhost:27017`
