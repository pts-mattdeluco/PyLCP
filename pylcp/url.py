def url_path_join(url, path_part):
    """Join a path part to the end of a URL adding/removing slashes as necessary."""
    result = url + '/' if not url.endswith('/') else url
    index = 1 if path_part.startswith('/') else 0
    return result + path_part[index:]
