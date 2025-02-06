import os
import socket
import ssl
import time
from urllib.parse import urlparse
import http_utils

def conditional_download(url, output_path='.'):
    host, path, port, use_ssl = http_utils.parse_url(url)

    obj_name = os.path.basename(path)

    os.makedirs(output_path, exist_ok=True)
    output_file = os.path.join(output_path, obj_name)

    # (1) threshold_before_download가 될 때까지 HEAD로 대기
    threshold_before_download = 10 * 1024 * 1024
    while True:
        head_resp = http_utils.http_head(host, path, port, use_ssl)
        total_size = http_utils.extract_content_length(head_resp)

        current_size_mb = total_size / (1024 * 1024)
        print(f"대기 중: 현재 파일 크기 = {current_size_mb:.2f} MB", end="\r", flush=True)
        if total_size >= threshold_before_download:
            break
        time.sleep(2)

    print("\n다운로드를 시작...")

    # (2) 다운로드 시작
    #     기본 속도 제한: 2.0MB/s
    desired_speed = 2.0 * 1024 * 1024  # byte/s
    checking_interval = 1
    downloaded_size = 0

    # 속도 조절용 시간/용량 체크
    start_time = time.time()
    last_check_time = start_time
    next_check_time = start_time + checking_interval
    last_file_size = total_size

    threshold_low_speed = 10 * 1024 * 1024
    threshold_full_speed = 20 * 1024 * 1024

    stream =  http_utils.http_get_stream( host, path, port, use_ssl, desired_speed)
    headers = next(stream)

    with open(output_file, 'wb') as f:
        for chunk, chunk_size, cur_speed in stream:
            # chunk 저장
            f.write(chunk)
            downloaded_size += len(chunk)

            # 현재 chunk에 대한 속도 제한
            # (chunk_size / desired_speed) 만큼 sleep
            if desired_speed:
                time.sleep(chunk_size / desired_speed)

            # 10초마다 HEAD 요청으로 파일 크기 확인
            current_time = time.time()
            if current_time >= next_check_time:
                head_resp = http_utils.http_head(host, path, port, use_ssl)
                new_total_size = http_utils.extract_content_length(head_resp)

                elapsed = current_time - start_time
                speed_mb_s = http_utils.bytes_to_mb_str(downloaded_size / elapsed if elapsed > 0 else 0)

                diff = new_total_size - downloaded_size
                size_growth = new_total_size - last_file_size

                # 서버상의 파일 상태와 다운로드 받은 크기에 따른 속도 스로틀링
                if size_growth == 0 or diff >= threshold_full_speed:
                    # 크기 증가가 없거나(촬영종료) threshold_full_speed 이상이면 - Full Speed Mode
                    desired_speed = 0

                elif diff <= threshold_low_speed:
                    # 5MB 이하이면 1MB/s로 제한 - Low Speed Mode
                    desired_speed = 1 * 1024 * 1024

                else:
                    # 5MB 이상이면 파일 증가량 기반으로 재계산 - Normal Speed Mode
                    time_diff = current_time - last_check_time
                    if time_diff > 0 and size_growth > 0:
                        desired_speed = size_growth / time_diff


                downloaded_size_mb = http_utils.bytes_to_mb_str(downloaded_size)
                new_total_size_mb = http_utils.bytes_to_mb_str(new_total_size)
                desired_speed_mb_s = http_utils.bytes_to_mb_str(desired_speed) if desired_speed else "-"

                print(
                    f"  {downloaded_size_mb} / {new_total_size_mb} MB "
                    f"- {speed_mb_s} ({desired_speed_mb_s}) MB/s"
                    , end='\r'
                    , flush=True
                )

                last_file_size = new_total_size
                last_check_time = current_time
                next_check_time = current_time + checking_interval

    print(f"\n다운로드 완료: 총 다운로드 크기 = {http_utils.bytes_to_mb_str(downloaded_size)} MB")


if __name__ == "__main__":
    test_url = "http://10.41.10.3:82/mp4/100SIYI_VID/REC_0020.mp4"
    conditional_download(test_url)
