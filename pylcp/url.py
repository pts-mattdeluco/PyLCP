def url_path_join(url, path_part):
    """Join a path part to the end of a URL adding/removing slashes as necessary."""
    result = url + '/' if url[-1:] != '/' else url
    index = 1 if path_part[:1] == '/' else 0
    return result + path_part[index:]
