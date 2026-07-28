"""Tüm hataları tek ve anlaşılır bir gövde biçimine çevirir.

Cevap biçimi:

```json
{"detail": "...", "error": {"code": "...", "message": "...", "fields": [...]}}
```

`detail` alanı FastAPI'nin varsayılan sözleşmesiyle uyumlu kalması için korunur.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

# Pydantic hata tiplerinin Türkçe karşılıkları.
VALIDATION_MESSAGES = {
    "missing": "Bu alan zorunlu.",
    "string_type": "Metin bekleniyor.",
    "int_type": "Tam sayı bekleniyor.",
    "int_parsing": "Tam sayı bekleniyor.",
    "list_type": "Liste bekleniyor.",
    "too_short": "Yeterli sayıda değer gönderilmedi.",
    "too_long": "İzin verilenden fazla değer gönderildi.",
    "string_too_short": "Bu alan boş bırakılamaz.",
    "string_pattern_mismatch": "Değer beklenen biçimde değil.",
    "literal_error": "Bu alan için geçersiz bir değer gönderildi.",
    "greater_than_equal": "Değer izin verilen alt sınırın altında.",
    "less_than_equal": "Değer izin verilen üst sınırın üstünde.",
    "json_invalid": "Gövde geçerli bir JSON değil.",
}

STATUS_MESSAGES = {
    404: "İstenen kayıt bulunamadı.",
    405: "Bu adres için kullanılan HTTP metodu desteklenmiyor.",
    500: "Sunucuda beklenmeyen bir hata oluştu.",
}


def error_body(code: str, message: str, fields: list[dict] | None = None) -> dict:
    return {
        "detail": message,
        "error": {"code": code, "message": message, "fields": fields or []},
    }


def _field_path(location: tuple) -> str:
    # ("body", "interest_ids", 0) -> "interest_ids.0"
    parts = [str(part) for part in location if part not in {"body", "query", "path"}]
    return ".".join(parts) or "body"


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(_: Request, exc: RequestValidationError):
        fields = [
            {
                "field": _field_path(error["loc"]),
                "message": VALIDATION_MESSAGES.get(error["type"], error["msg"]),
                "type": error["type"],
            }
            for error in exc.errors()
        ]
        names = ", ".join(dict.fromkeys(field["field"] for field in fields))
        return JSONResponse(
            status_code=422,
            content=error_body(
                "validation_error",
                f"İstek gövdesi geçersiz. Kontrol edilmesi gereken alanlar: {names}.",
                fields,
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(_: Request, exc: StarletteHTTPException):
        if isinstance(exc.detail, dict) and "error" in exc.detail:
            return JSONResponse(status_code=exc.status_code, content=exc.detail)

        message = str(exc.detail) if exc.detail else STATUS_MESSAGES.get(exc.status_code, "Hata.")
        return JSONResponse(
            status_code=exc.status_code,
            content=error_body(f"http_{exc.status_code}", message),
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(_: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content=error_body("internal_error", STATUS_MESSAGES[500]),
        )
