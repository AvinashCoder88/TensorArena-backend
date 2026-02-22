import os
from fastapi import APIRouter

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.get("/erp")
async def get_erp_status():
    provider = os.getenv("ERP_PROVIDER")
    tenant = os.getenv("ERP_TENANT")
    client_id = os.getenv("ERP_CLIENT_ID")
    client_secret = os.getenv("ERP_CLIENT_SECRET")

    if not provider or not tenant or not client_id or not client_secret:
        return {
            "status": "not_configured",
            "message": "ERP integration is not configured. Using local database.",
        }

    return {
        "status": "configured",
        "provider": provider,
        "tenant": tenant,
    }


@router.post("/erp")
async def sync_erp_placeholder():
    provider = os.getenv("ERP_PROVIDER")
    tenant = os.getenv("ERP_TENANT")
    client_id = os.getenv("ERP_CLIENT_ID")
    client_secret = os.getenv("ERP_CLIENT_SECRET")

    if not provider or not tenant or not client_id or not client_secret:
        return {
            "status": "using_local_db",
            "message": "No ERP configured. Using local database for now.",
        }

    return {
        "status": "queued",
        "message": "ERP sync placeholder. External sync will be wired later.",
        "provider": provider,
        "tenant": tenant,
    }
