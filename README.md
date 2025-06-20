# JSRecon
# 🔍 JavaScript Endpoint Extractor

A powerful Python-based tool to extract endpoints (URLs, API paths, `.php`, `.json`, `.js` files) from JavaScript files linked on a given webpage. Supports inline JS, recursive crawling of JS files, and optional authentication headers.

---

## ✨ Features

- 🔎 Parses external & inline JavaScript
- 🔁 Recursive parsing of discovered JS files (default: unlimited)
- 🧠 Regex-based extraction of:
  - Full URLs (`https://...`, `//...`)
  - Relative paths (`/api/...`)
  - File references (`.php`, `.json`, `.js`)
- 🔐 Supports custom HTTP headers (e.g., Authorization tokens)
- 💾 Saves results to `discovered_endpoints.txt`
- 📏 Logs JS file sizes for recon analysis

---

## 🧪 Example Output

```bash
[*] Parsing https://example.com/assets/main.js
    [~] https://example.com/assets/main.js - 12432 bytes
[*] Inline script - 830 bytes: 3 links found

[+] Discovered 6 endpoints:
https://example.com/api/user/login
https://example.com/config/settings.json
https://cdn.example.net/lib.js
...
[+] Saved to discovered_endpoints.txt
