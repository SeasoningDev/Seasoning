_sitemap = {}

class Page(object):
    
    def __init__(self, url, links=[], reachable_from_everywhere=False):
        self.url = url
        self.links = links
        self.reachable_from_everywhere = reachable_from_everywhere

def register_page(url, links=[], reachable_from_everywhere=False):
    new_page = Page(url, links, reachable_from_everywhere)
    new_page.links.append(new_page.url)
    _sitemap[url] = new_page
    
    for link in links:
        if link not in _sitemap:
            _sitemap[link] = Page(link)
            
    if new_page.reachable_from_everywhere:
        for page in _sitemap.values():
            if new_page.url not in page.links:
                page.links.append(new_page.url)
    
    for page in _sitemap.values():
        if page.reachable_from_everywhere and page.url not in new_page.links:
            new_page.links.append(page.url)

def _get_chain(from_page, to_page):
    if from_page == to_page:
        return [from_page]
    # Simple breadth first search
    visited_pages = [from_page.url]
    queue = [[from_page]]
    while queue:
        current_chain = queue.pop(0)
        leaf = current_chain[-1]
        for link in leaf.links:
            if link in visited_pages:
                continue
            visited_pages.append(link)
            if link == to_page.url:
                current_chain.append(_sitemap[link])
                return current_chain
            else:
                new_chain = current_chain.copy()
                new_chain.append(_sitemap[link])
                queue.append(new_chain)
    return None
    
def find_path(from_url, to_url):
    try:
        start_page = _sitemap[from_url]
    except KeyError:
        start_page = Page(from_url)
        for page in _sitemap.values():
            if page.reachable_from_everywhere:
                start_page.links.append(page.url)
    end_page = _sitemap[to_url]
    
    # Drop the first page in the chain, because this is the current page, we do not need
    # to browse to that page
    chain = _get_chain(start_page, end_page)[1:]
    if chain is None:
        raise Exception('No path was found from "' + from_url + '" to "' + to_url + '"')
    return [page.url for page in chain]