import re

def get_link_for_js_file_with_queryhash(response):
    link = response.xpath(
        '//link[contains(@href, "/static/bundles/LocationPageContainer.js")]/@href').extract_first()

    return link

def get_queryhash_from_js_file(response):
    pattern = r'(.*)(?P<text_before>locationPosts\.byLocationId\.get\(e\)\.pagination},queryId:\")(?P<query_hash>.*?)(\".*)'
    match = re.match(pattern, response.text)
    query_hash = match.group('query_hash')

    return query_hash
