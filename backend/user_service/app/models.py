from datetime import datetime

ADMIN_EMAILS = ["admin@gmail.com", "knowscope80@gmail.com"]
def user_document(data: dict) -> dict:
    role = "admin" if data["email"] in ADMIN_EMAILS else "user"
    return {
        "google_id": data["google_id"],
        "email": data["email"],
        "name": data.get("name"),
        "picture": data.get("picture"),
        "role": role,
        "created_at": datetime.utcnow()
    }
