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
                    query_params = {}
                    query_string = query or ""
                    if query_string:
                        for pair in query_string.split("&"):
                            if "=" in pair:
                                key, value = pair.split("=", 1)
                            else:
                                key, value = pair, ""
                            if key in query_params:
                                query_params[key].append(value)
                            else:
                                query_params[key] = [value]

                    request_headers = {}
                    for header_key, header_value in environ.items():
                        if header_key.startswith("HTTP_") or header_key in ("CONTENT_TYPE", "CONTENT_LENGTH"):
                            header_name = header_key.replace("HTTP_", "").replace("_", "-").title()
                            request_headers[header_name] = str(header_value)

                    params_rows = "".join(
                        f"<tr><td>{key}</td><td>{', '.join(values)}</td></tr>"
                        for key, values in query_params.items()
                    ) or "<tr><td colspan='2'><em>No query parameters</em></td></tr>"

                    headers_rows = "".join(
                        f"<tr><td>{name}</td><td>{value}</td></tr>"
                        for name, value in sorted(request_headers.items())
                    ) or "<tr><td colspan='2'><em>No headers</em></td></tr>"

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
                        with open(file_map[path], "r", encoding="utf-8") as file:
                            content = file.read()
                        body = content.encode("utf-8")
                        headers = [("Content-Type", "text/html"), ("Content-Length", str(len(body)))]
                        start_response("200 OK", headers)
                        return [body]
                    except Exception as exception:
                        msg = f"<h1>500 Internal Server Error</h1><p>Failed to load page: {str(exception)}</p>"
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

        except Exception as exception:
            body = f"<h1>500 Internal Server Error</h1><p>{str(exception)}</p>".encode("utf-8")
            headers = [("Content-Type", "text/html"), ("Content-Length", str(len(body)))]
            start_response("500 Internal Server Error", headers)
            return [body]

app = MyAPI()