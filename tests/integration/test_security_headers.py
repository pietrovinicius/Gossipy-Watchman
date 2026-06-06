import pytest


@pytest.mark.asyncio
async def test_x_content_type_options(client):
    response = await client.get("/api/v1/health")
    assert response.headers.get("x-content-type-options") == "nosniff"


@pytest.mark.asyncio
async def test_x_frame_options(client):
    response = await client.get("/api/v1/health")
    assert response.headers.get("x-frame-options") == "DENY"


@pytest.mark.asyncio
async def test_x_xss_protection(client):
    response = await client.get("/api/v1/health")
    assert response.headers.get("x-xss-protection") == "1; mode=block"


@pytest.mark.asyncio
async def test_referrer_policy(client):
    response = await client.get("/api/v1/health")
    assert response.headers.get("referrer-policy") == "strict-origin-when-cross-origin"


@pytest.mark.asyncio
async def test_content_security_policy_present(client):
    response = await client.get("/api/v1/health")
    csp = response.headers.get("content-security-policy", "")
    assert "default-src" in csp
