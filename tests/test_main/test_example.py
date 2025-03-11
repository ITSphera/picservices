# @pytest.mark.asyncio
class TestExample:
    """
    Test example
    """

    async def test_example(self, async_client):
        response = await async_client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Hello World"}
        assert response.headers["Content-Type"] == "application/json"
