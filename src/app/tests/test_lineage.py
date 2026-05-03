import pytest
from httpx import AsyncClient


# Tells pytest this file contains async tests
pytestmark = pytest.mark.asyncio

async def test_cycle_detection(async_client: AsyncClient):
    # Create datasets
    dataset_a = await async_client.post("/datasets/", json={"name": "Dataset A"})
    dataset_b = await async_client.post("/datasets/", json={"name": "Dataset B"})
    dataset_c = await async_client.post("/datasets/", json={"name": "Dataset C"})
    # Create edges to form a cycle: A -> B -> C -> A
    edge_ab = await async_client.post("/lineage/edges", json={"upstream_id": dataset_a.json()["id"], "downstream_id": dataset_b.json()["id"]})
    edge_bc = await async_client.post("/lineage/edges", json={"upstream_id": dataset_b.json()["id"], "downstream_id": dataset_c.json()["id"]})
    
    # This should fail due to cycle detection
    edge_ca_response = await async_client.post("/lineage/edges", json={"upstream_id": dataset_c.json()["id"], "downstream_id": dataset_a.json()["id"]})
    
    assert edge_ca_response.status_code == 400
    assert "cycle" in edge_ca_response.json().get("detail", "").lower()

