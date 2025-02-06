import os
import requests

# 기본 API 엔드포인트 IP 및 변수 설정
default_ip = "10.41.10.3"
def get_api_base_url(ip=default_ip):
    return f"http://{ip}:82/cgi-bin/media.cgi/api/v1"

DEFAULT_MEDIA_TYPE = 1
DEFAULT_PATH = "100SIYI_VID"

default_output_path = "videos"  # 기본 비교 대상 폴더 경로

# 마지막 5개 파일 가져오기 함수
def get_last_files(api_base_url, media_type=DEFAULT_MEDIA_TYPE, path=DEFAULT_PATH, count=5):
    # 파일 개수 확인
    count_url = f"{api_base_url}/getmediacount?media_type={media_type}&path={path}"
    count_response = requests.get(count_url).json()

    if count_response.get("success") and count_response["data"]["count"] > 0:
        total_files = count_response["data"]["count"]
        start_index = max(0, total_files - count)

        # 파일 목록 가져오기
        list_url = f"{api_base_url}/getmedialist?media_type={media_type}&path={path}&start={start_index}&count={count}"
        list_response = requests.get(list_url).json()

        if list_response.get("success"):
            return list_response["data"]["list"]
    return []

# output_path에 없는 파일 찾기 함수
def find_missing_files(output_path, file_list):
    # output_path의 파일 목록 가져오기
    existing_files = set(os.listdir(output_path))

    missing_files = [
        {"name": file["name"], "url": file["url"]}
        for file in file_list if file["name"] not in existing_files
    ]
    return missing_files

# 실행
if __name__ == "__main__":
    last_files = get_last_files(get_api_base_url("10.41.10.3"))
    print(last_files)

    res = find_missing_files("test", last_files)
    print(res)
