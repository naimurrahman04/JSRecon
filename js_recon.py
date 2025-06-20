#!/usr/bin/env python3
import re
import sys
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import os

# Default headers (browser-like)
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.0.0 Safari/537.36"
}

# ➕ Add any Authorization or custom headers here:
CUSTOM_HEADERS = {
    # Example:
    # "Authorization": "Bearer YOUR_TOKEN",
    # "X-API-Key": "abc123"
}

HEADERS = {**DEFAULT_HEADERS, **CUSTOM_HEADERS}

# Regex for detecting URLs and file paths
JS_REGEX = re.compile(
    r"""(?:"|')(
        (?:[a-zA-Z]{1,10}://|//)[^"'\\]{1,}     |   # Full URLs
        /(?:[^"'\\])+                          |   # Absolute paths
        [a-zA-Z0-9_\-/\.]+\.(?:php|json|js)        # File references
    )(?:"|')""",
    re.VERBOSE
)

def extract_links(js_text, base_url):
    found = set()
    try:
        for match in JS_REGEX.finditer(js_text):
            link = match.group(1)
            if link.startswith("//"):
                link = "https:" + link
            elif link.startswith("/"):
                link = urljoin(base_url, link)
            elif not link.startswith("http"):
                link = urljoin(base_url, "/" + link)
            found.add(link)
    except Exception as e:
        print(f"[!] Regex error: {e}")
    return found

def fetch_and_parse_js(js_url, base_url, verbose=False, recursion_depth=float("inf"), visited=None):
    if visited is None:
        visited = set()
    if js_url in visited or recursion_depth <= 0:
        return set()
    
    visited.add(js_url)
    links_found = set()

    try:
        resp = requests.get(js_url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            if verbose:
                print(f"    [~] {js_url} - {len(resp.text)} bytes")
            new_links = extract_links(resp.text, base_url)
            links_found.update(new_links)

            for link in new_links:
                if link.endswith('.js') and link not in visited:
                    links_found.update(
                        fetch_and_parse_js(link, base_url, verbose, recursion_depth - 1, visited)
                    )
        else:
            if verbose:
                print(f"    [!] {js_url} returned HTTP {resp.status_code}")
    except requests.RequestException as e:
        if verbose:
            print(f"    [!] Error fetching {js_url} - {e}")
    return links_found

def get_js_links_and_inline_scripts(html_text):
    try:
        soup = BeautifulSoup(html_text, 'html.parser')
        js_links = [script['src'] for script in soup.find_all('script', src=True)]
        inline_scripts = [script.string for script in soup.find_all('script') if not script.get('src') and script.string]
        return js_links, inline_scripts
    except Exception as e:
        print(f"[!] HTML parse error: {e}")
        return [], []

def main(target_url, verbose=True, recursion_depth=float("inf")):
    try:
        response = requests.get(target_url, headers=HEADERS, timeout=10)
    except Exception as e:
        print(f"[!] Error fetching {target_url} - {e}")
        return

    base_url = f"{urlparse(target_url).scheme}://{urlparse(target_url).netloc}"
    js_files, inline_scripts = get_js_links_and_inline_scripts(response.text)

    all_links = set()

    for js in js_files:
        full_url = urljoin(base_url, js)
        if verbose:
            print(f"[*] Parsing {full_url}")
        links = fetch_and_parse_js(full_url, base_url, verbose, recursion_depth)
        all_links.update(links)

    for inline_script in inline_scripts:
        try:
            links = extract_links(inline_script, base_url)
            if verbose:
                print(f"[*] Inline script - {len(inline_script)} bytes: {len(links)} links found")
            all_links.update(links)
        except Exception as e:
            print(f"[!] Inline JS error: {e}")

    print(f"\n[+] Discovered {len(all_links)} endpoints:")
    for link in sorted(all_links):
        print(link)

    try:
        with open("discovered_endpoints.txt", "w") as f:
            for link in sorted(all_links):
                f.write(link + "\n")
        print("[+] Saved to discovered_endpoints.txt")
    except IOError as e:
        print(f"[!] Failed to write to file: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python3 {os.path.basename(__file__)} https://target.com [recursion_depth]")
        sys.exit(1)
    url = sys.argv[1]
    try:
        depth = float(sys.argv[2]) if len(sys.argv) > 2 else float("inf")
    except ValueError:
        print("[!] Recursion depth must be a number or leave blank for unlimited.")
        sys.exit(1)
    main(url, verbose=True, recursion_depth=depth)
