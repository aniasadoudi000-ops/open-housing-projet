"""Point d'entrée API du MVP."""

from fastapi import FastAPI

app = FastAPI(title="Open Housing MVP")


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Open Housing MVP API"}
