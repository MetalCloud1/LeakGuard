from fastapi import FastAPI

app = FastAPI()


@app.get("/users")
def get_users():
    return [{"id": 1, "name": "G"}]


@app.get("/health")
def health_check():
    return {"status": "ok"}
