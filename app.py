import string
import random
from datetime import datetime

import uvicorn
from fastapi import FastAPI, Request, Query, HTTPException

app = FastAPI()


@app.get("/whoami")
async def whoami(request: Request):
    user_agent = request.headers.get("user-agent")
    user_ip = request.client.host
    current_time = datetime.now()

    return {
        "User-Agent": user_agent,
        "User-IP": user_ip,
        "Time": current_time,
    }


@app.get("/source_code")
async def source_code():
    with open(__file__, "r") as f:
        code = f.read()

    return code


@app.get("/random")
async def get_random_string(
    length: int = Query(8, ge=1, le=100),
    specials: int = Query(0, ge=0, le=1),
    digits: int = Query(0, ge=0, le=1),
):
    if specials not in (0, 1) or digits not in (0, 1):
        raise HTTPException(
            status_code=400, detail="specials and digits must be 0 or 1"
        )

    chars = list(string.ascii_letters)
    if specials:
        chars.extend('!"№;%:?*()_+')
    if digits:
        chars.extend(string.digits)

    if not chars:
        raise HTTPException(status_code=400, detail="No characters to generate from")

    result = "".join(random.choice(chars) for _ in range(length))
    return {"result": result}


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=5000, reload=True)
