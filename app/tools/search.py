from tavily import TavilyClient

from app import config


def search_web(query: str, max_results: int = 5) -> list[dict]:
    """
    Search the web using Tavily.

    Args:
        query: The search query.
        max_results: Maximum number of results to return.

    Returns:
        A list of search results containing title, URL, content, and score.
    """

    # 1. Check that the API key exists
    if not config.TAVILY_API_KEY:
        raise ValueError(
            "Tavily API key is missing. Add TAVILY_API_KEY to your .env file."
        )

    # 2. Create the Tavily client
    client = TavilyClient(api_key=config.TAVILY_API_KEY)

    # 3. Send the search request
    response = client.search(
        query=query,
        max_results=max_results,
        search_depth="basic",
        topic="general",
    )

    # 4. Extract and standardize the results
    results = []

    for item in response.get("results", []):
        results.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "content": item.get("content", ""),
            "score": item.get("score", 0.0),
        })

    # 5. Return the standardized results
    return results
