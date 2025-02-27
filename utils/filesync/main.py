#!/Users/bluedisk/anaconda3/bin/python
import os
import argparse
import time
import logging
import sync
from stream_download import conditional_download

default_ip = "10.41.10.3"
default_output_path = "videos"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def main(ip, output_path):
    # 파라미터 파서 설정
    
    api_base_url = sync.get_api_base_url(ip)

    os.makedirs(output_path, exist_ok=True)

    last_files = sync.get_last_files(api_base_url, count=1)
    missing_files = sync.find_missing_files(output_path, last_files)

    if missing_files:
        for idx, file in enumerate(missing_files):
            logging.info(f"===== {idx + 1}/{len(missing_files)} Name: {file['name']}, URL: {file['url']}")
            url = f"http://{ip}:82/mp4/100SIYI_VID/{file['name']}"
            print("Download from", url)
            conditional_download(f"http://{ip}:82/mp4/100SIYI_VID/{file['name']}", output_path)

    # while True:
    #     logging.info(f"Checking... Sync from IP: {ip}, to: {output_path}")

    #     # API에서 마지막 5개의 파일 가져오기
    #     last_files = sync.get_last_files(api_base_url)

    #     if not last_files:
    #         logging.error("파일 목록을 가져올 수 없습니다.")
    #     else:
    #         # output_path와 비교하여 없는 파일 출력
    #         missing_files = sync.find_missing_files(output_path, last_files)

    #         if missing_files:
    #             for idx, file in enumerate(missing_files):
    #                 logging.info(f"===== {idx + 1}/{len(missing_files)} Name: {file['name']}, URL: {file['url']}")
    #                 url = f"http://{ip}:82/mp4/100SIYI_VID/{file['name']}"
    #                 print("Download from", url)
    #                 conditional_download(f"http://{ip}:82/mp4/100SIYI_VID/{file['name']}", output_path)

    #     # 1초 대기
    #     time.sleep(1)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Fetch and compare media files.")
    parser.add_argument("-i", "--ip", type=str, default=default_ip, help="API 서버 IP 주소 (기본값: 10.41.10.3)")
    parser.add_argument("-o", "--output_path", type=str, default=default_output_path, help="비교 대상 폴더 경로 (기본값: videos)")

    args = parser.parse_args()
    main(ip=args.ip, output_path=args.output_path)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
