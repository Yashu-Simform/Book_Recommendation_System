from app.main import app
from fastapi import Request, responses as res, status
from app.modules.auth import exceptions as exc

@app.exception_handler(exc.InvalidToken)
async def invalid_ref_token_handler(req: Request, exc: exc.InvalidToken):
    return res.JSONResponse(content=str(exc), status_code=status.HTTP_400_BAD_REQUEST)