from app.tools.search import search_web


if __name__ == "__main__":
    results = search_web(
        "official government complaint contact Lahore Pakistan",
        max_results=3,
    )

    if not results:
        print("The search completed, but no results were returned.")

    for index, result in enumerate(results, start=1):
        print(f"\nResult {index}")
        print("Title:", result["title"])
        print("URL:", result["url"])
        print("Content:", result["content"])
        print("Score:", result["score"])
