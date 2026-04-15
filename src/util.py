import os
import re

class FileUtil:
    @staticmethod
    def clean_name(title: str) -> str:
        """
        윈도우/맥 파일명으로 쓸 수 없는 특수문자를 제거하거나 언더바로 변경합니다.
        """
        # \ / : * ? " < > | 문자를 제거
        clean_title = re.sub(r'[\/:*?"<>|]', "", title)
        # 양 끝 공백 제거 및 너무 긴 파일명 방지 (최대 150자)
        return clean_title.strip()[:150]

    @staticmethod
    def get_unique_path(file_path: str) -> str:
        """
        파일이 이미 존재하면 '제목(1).mp4', '제목(2).mp4' 식으로 유일한 경로를 반환합니다.
        """
        if not os.path.exists(file_path):
            return file_path

        directory, filename = os.path.split(file_path)
        name, ext = os.path.splitext(filename)

        counter = 1
        while True:
            new_name = f"{name}({counter}){ext}"
            new_path = os.path.join(directory, new_name)
            if not os.path.exists(new_path):
                return new_path
            counter += 1
            
    @staticmethod
    def generate_filename(info: dict) -> str:
        """
        메타데이터를 바탕으로 [닉네임] YYMMDD 제목 형태의 파일명을 생성합니다.
        """
        nick = info.get('nick', 'Unknown')
        broad_start = info.get('broad_start', '')
        title = info.get('title', 'Untitled').replace("[클립]", "").strip()
        title = re.sub(r'[\/:*?"<>|]', "", title)

        formatted_date = ""
        if broad_start and len(broad_start) >= 10:
            date_match = re.search(r'(\d{2})(\d{2})-(\d{2})-(\d{2})', broad_start)
            if date_match:
                formatted_date = f"{date_match.group(2)}{date_match.group(3)}{date_match.group(4)}"

        new_name = f"[{nick}] {formatted_date} {title}.mp4"
        return new_name


def ms_to_hms(ms):
    seconds = int(ms) // 1000
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"


def print_metadata(metadata: dict):
    print(f"제목: {metadata.get('title', 'Unknown')}")
    print(f"스트리머: {metadata.get('nick', 'Unknown')} ({metadata.get('id', 'Unknown')})")
    print(f"방송일: {metadata.get('broad_start', 'Unknown')}")
    print(f"유형: {metadata.get('file_type', 'Unknown')}")
    print(f"원본 VOD 번호: {metadata.get('original_vod', 'N/A')}")
    print(f"해상도: {metadata.get('file_resolution', 'Unknown')}")
    print(f"총 재생시간: {ms_to_hms(metadata.get('total_file_duration', 0))} ({metadata.get('total_file_duration', 0)}ms)")
    print(f"전체 파트: {len(metadata.get('stream_url', []))}")
    for i, (m3u8, resolution, duration) in enumerate(metadata.get('stream_url', []), start=1):
        print(f" 파트{i} m3u8: {m3u8}")
        print(f" 파트{i} 해상도: {resolution}")
        print(f" 파트{i} 재생시간: {ms_to_hms(duration)} ({duration}ms)")
            
            
def parse_time_range(range_input):
    start_time, end_time = range_input.split('~')
    return start_time.strip(), end_time.strip()


def time_to_ms(time_str):
    if not time_str:
        return 0
    parts = time_str.split(':')
    parts = [int(part) for part in parts]
    if len(parts) == 3 and 0 <= parts[1] < 60 and 0 <= parts[2] < 60:
        hours, minutes, seconds = parts
        total_ms = (hours * 3600 + minutes * 60 + seconds) * 1000
        return total_ms
    else:
        raise ValueError("시간 형식이 올바르지 않습니다. HH:MM:SS 형식을 사용하세요.")
    
    
def ms_to_time(ms):
    total_seconds = ms // 1000
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"