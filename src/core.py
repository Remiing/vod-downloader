import os
from src.process import FFmpegProcess
from src.util import FileUtil

class SOOPDownloader:
    def __init__(self, ffmpeg_path="ffmpeg"):
        self.ffmpeg = FFmpegProcess(ffmpeg_path)

    def download_video(self, video_info, section, callback=None):
        """
        video_info: VOD 정보 딕셔너리
        section: 다운로드할 파트 번호 집합 ex) {1, 3} 또는 {0} (전체)
        callback: 진행 상황 업데이트를 위한 콜백 함수 (percent, message)
        """
        try:
            # callback이 없어도 에러가 나지 않도록 빈 함수로 대체
            callback = callback or (lambda *args: None)
            
            # 파일명 생성
            filename = FileUtil.generate_filename(video_info)
            if not os.path.exists("vod"): os.makedirs("vod")
            
            stream_url_list = video_info['stream_url']
            
            for i, (stream_url, resolution, duration) in enumerate(stream_url_list, start=1):
                # 사용자가 선택한 파트가 아니면 건너뛰기 (0은 전체 다운로드)
                if i not in section and section != {0}:
                    continue
                
                # 파트로 나누어진 VOD 파일명 처리
                part_filename = filename.replace(".mp4", f"_{i}.mp4") if len(stream_url_list) > 1 else filename
                file_path = os.path.join("vod", part_filename)
                
                # VOD 다운로드
                callback(0, f"준비중")
                proc = self.ffmpeg.download(stream_url, file_path)
                for current_ms in self.ffmpeg.watch_progress(proc):
                    if duration > 0:
                        percent = min(100, int((current_ms / duration) * 100))
                        callback(percent, f"파트 {i}")
                callback(100, f"파트 {i}")
                proc.wait()
            
            return True
            
        except Exception as e:
            callback(-1, f"에러 발생: {str(e)}")
            return False