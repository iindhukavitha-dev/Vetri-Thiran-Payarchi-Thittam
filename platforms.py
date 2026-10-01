from urllib.parse import quote_plus


PLATFORM_DOMAINS = {
    "Amazon": "https://www.amazon.in/s?k={query}",
    "Flipkart": "https://www.flipkart.com/search?q={query}",
    "IKEA": "https://www.ikea.com/in/en/search/?q={query}",
    "Swiggy": "https://www.swiggy.com/search?query={query}",
    "Zomato": "https://www.zomato.com/search?q={query}",
    "OYO": "https://www.oyorooms.com/search?location={query}",
}


def get_search_url(
    platform: str,
    query: str,
) -> str:
    template = PLATFORM_DOMAINS.get(platform)

    if not template:
        template = "https://www.google.com/search?q={query}"

    return template.format(
        query=quote_plus(query)
    )
