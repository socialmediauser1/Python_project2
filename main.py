from datetime import datetime

class MyAPI:
    def __call__(self, environ, start_response):
        try:
            method = environ['REQUEST_METHOD']
            path = environ.get('PATH_INFO', '/')
            query = environ.get('QUERY_STRING', '')

            user_agent = environ.get("HTTP_USER_AGENT", "Unknown")
            accept = environ.get("HTTP_ACCEPT", "Unknown")

            timestamp = datetime.now().isoformat()
            log_line = f"[{timestamp}] METHOD: {method} PATH: {path} QUERY: {query} Headers: User-Agent={user_agent}, Accept={accept}\n"
            with open("logs.txt", "a", encoding="utf-8") as f:
                f.write(log_line)

            if path in ("/about", "/contact") and method != "GET":
                body = "<h1>405 Not Allowed</h1><p>Only GET is allowed on this page.</p>".encode("utf-8")
                headers = [("Content-Type", "text/html"), ("Content-Length", str(len(body))), ("Allow", "GET")]
                start_response("405 Method Not Allowed", headers)
                return [body]

            if method == "GET":
                if path == "/inspect":
                    params = {}
                    q = query or ""
                    if q:
                        for pair in q.split("&"):
                            if "=" in pair:
                                k, v = pair.split("=", 1)
                            else:
                                k, v = pair, ""
                            if k in params:
                                params[k].append(v)
                            else:
                                params[k] = [v]
                    headers_dict = {}
                    for k, v in environ.items():
                        if k.startswith("HTTP_") or k in ("CONTENT_TYPE", "CONTENT_LENGTH"):
                            pretty = k.replace("HTTP_", "").replace("_", "-").title()
                            headers_dict[pretty] = str(v)
                    params_rows = "".join(f"<tr><td>{k}</td><td>{', '.join(v)}</td></tr>" for k, v in params.items()) or "<tr><td colspan='2'><em>No query parameters</em></td></tr>"
                    headers_rows = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in sorted(headers_dict.items())) or "<tr><td colspan='2'><em>No headers</em></td></tr>"
                    html = f"""
                    <html>
                      <head><title>Request Inspection</title></head>
                      <body>
                        <h1>/inspect</h1>
                        <h2>Query Parameters</h2>
                        <table border="1" cellpadding="6" cellspacing="0">
                          <tr><th>Key</th><th>Value</th></tr>
                          {params_rows}
                        </table>
                        <h2>Request Headers</h2>
                        <table border="1" cellpadding="6" cellspacing="0">
                          <tr><th>Header</th><th>Value</th></tr>
                          {headers_rows}
                        </table>
                      </body>
                    </html>
                    """
                    body = html.encode("utf-8")
                    headers = [("Content-Type", "text/html"), ("Content-Length", str(len(body)))]
                    start_response("200 OK", headers)
                    return [body]

                file_map = {
                    "/": "templates/index.html",
                    "/about": "templates/about.html",
                    "/contact": "templates/contact.html",
                }

                if path in file_map:
                    try:
                        with open(file_map[path], "r", encoding="utf-8") as f:
                            content = f.read()
                        body = content.encode("utf-8")
                        headers = [("Content-Type", "text/html"), ("Content-Length", str(len(body)))]
                        start_response("200 OK", headers)
                        return [body]
                    except Exception as e:
                        msg = f"<h1>500 Internal Server Error</h1><p>Failed to load page: {str(e)}</p>"
                        body = msg.encode("utf-8")
                        headers = [("Content-Type", "text/html"), ("Content-Length", str(len(body)))]
                        start_response("500 Internal Server Error", headers)
                        return [body]

                body = "<h1>404 Not Found</h1><p>The page you requested does not exist.</p>".encode("utf-8")
                headers = [("Content-Type", "text/html"), ("Content-Length", str(len(body)))]
                start_response("404 Not Found", headers)
                return [body]

            body = "<h1>405 Method Not Allowed</h1><p>The requested method is not supported.</p>".encode("utf-8")
            headers = [("Content-Type", "text/html"), ("Content-Length", str(len(body)))]
            start_response("405 Method Not Allowed", headers)
            return [body]

        except Exception as e:
            body = f"<h1>500 Internal Server Error</h1><p>{str(e)}</p>".encode("utf-8")
            headers = [("Content-Type", "text/html"), ("Content-Length", str(len(body)))]
            start_response("500 Internal Server Error", headers)
            return [body]

app = MyAPI()