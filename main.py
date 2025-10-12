from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}
@app.get('/dead')
def dead_boy(name:str):
    return {'hello':name}
