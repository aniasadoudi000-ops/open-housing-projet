"""Point d'entrée API du POC."""

from fastapi import FastAPI

app = FastAPI(title="Open Housing POC")


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Open Housing POC API"}
