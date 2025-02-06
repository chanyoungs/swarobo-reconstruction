import socket
import ssl
from urllib.parse import urlparse

def parse_url(url):
    """
    http://example.com:80/path/to/file
    https://example.com/path/to/file
    등등의 URL을 파싱해서 (host, path, port, use_ssl) 형태로 반환
    """
    parsed = urlparse(url)
    host = parsed.hostname
    path = parsed.path or '/'
    scheme = parsed.scheme.lower()

    # 쿼리스트링이 있다면 path 뒤에 붙인다
    if parsed.query:
        path += '?' + parsed.query

    if scheme == 'https':
        port = parsed.port if parsed.port else 443
        use_ssl = True
    else:
        port = parsed.port if parsed.port else 80
        use_ssl = False

    return host, path, port, use_ssl


def http_head(host, path, port=80, use_ssl=False, timeout=5):
    """
    HTTP/1.0 HEAD 요청을 보내고, 응답 헤더 전체(바이너리)를 반환.
    Content-Length 등은 응답 헤더에서 직접 파싱.
    """
    # 소켓 생성
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)

    # 필요시 SSL 감싸기
    if use_ssl:
        s = ssl.wrap_socket(s)

    s.connect((host, port))

    # HTTP/1.0 + Connection: close
    # Host 헤더는 가급적 넣어준다.
    request_header = (
        f"HEAD {path} HTTP/1.0\r\n"
        f"Host: {host}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )
    s.sendall(request_header.encode('utf-8'))

    response = b""
    while True:
        try:
            chunk = s.recv(4096)
            if not chunk:
                break
            response += chunk
        except socket.timeout:
            break

    s.close()
    return response


def extract_content_length(response):
    """
    HEAD 응답(바이너리)에서 Content-Length 값을 파싱해서 정수로 반환.
    없거나 잘못된 경우 0 반환.
    """
    # 바이너리를 문자열로 변환 (HTTP 헤더는 보통 ASCII 기준)
    header_str = response.decode('iso-8859-1', errors='replace')

    # HTTP 헤더는 빈 줄("\r\n\r\n")이 나오기 전까지
    # 여기서는 간단히 Content-Length 줄을 찾는다.
    # 대소문자 구분 없이 찾기 위해 lower() 처리
    lines = header_str.split("\r\n")
    length_val = 0
    for line in lines:
        low = line.lower()
        if "content-length:" in low:
            # 예) Content-Length: 12345
            try:
                length_val = int(low.split(":", 1)[1].strip())
            except ValueError:
                pass
            break
    return length_val


def http_get_stream(host, path, port=80, use_ssl=False, desired_speed=2.4 * 1024 * 1024):
    """
    HTTP/1.0 GET 요청을 보내고, 서버가 연결을 끊을 때까지 소켓에서 직접 데이터를 읽어들이는 제너레이터.
    원하는 경우 응답 헤더를 첫 번째로 반환. 이후로는 콘텐츠를 스트리밍한다.
    desired_speed: 초기 속도 제한 (byte/s)
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(10)
    if use_ssl:
        s = ssl.wrap_socket(s)
    s.connect((host, port))

    # HTTP/1.0 GET, Accept-Encoding: identity, Connection: close
    # Content-Length 무시를 위해 chunked 전송 등은 피하고, 서버가 끝날 때까지 받는다
    request_header = (
        f"GET {path} HTTP/1.0\r\n"
        f"Host: {host}\r\n"
        "Accept-Encoding: identity\r\n"
        "Connection: close\r\n"
        "\r\n"
    )
    s.sendall(request_header.encode('utf-8'))

    # 첫 번째 응답에서 헤더 추출
    response = b""
    while b"\r\n\r\n" not in response:
        response += s.recv(1024)
    headers_data, content_data = response.split(b"\r\n\r\n", 1)

    # 헤더 바이너리를 파싱하여 딕셔너리에 저장
    header_lines = headers_data.decode('iso-8859-1').split("\r\n")
    headers = {}
    for line in header_lines[1:]:
        if ": " in line:
            key, value = line.split(": ", 1)
            headers[key.lower()] = value

    yield headers

    # 콘텐츠 스트림은 기존 방식으로 처리
    chunk_size = 1024  # 1KB
    while True:
        try:
            chunk = content_data or s.recv(chunk_size)
            if not chunk:
                break
            content_data = None
            yield chunk, chunk_size, desired_speed
        except socket.timeout:
            continue

    s.close()


def bytes_to_mb_str(byte_value):
    """
    바이트 값을 MB 단위로 변환하여 반환.
    """
    return f"{byte_value / (1024 * 1024):.2f}"
