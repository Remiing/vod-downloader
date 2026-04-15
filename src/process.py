import subprocess

class FFmpegProcess:
    def __init__(self, path):
        self.path = path

    def download(self, url, output_path):
        cmd = [self.path, "-y"]
        
        cmd.extend([
            "-i", url, 
            "-c", "copy", 
            "-map_metadata", "0",
            "-progress", "pipe:1", 
            output_path
        ])
        
        return subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            encoding='utf-8'
        )

    def watch_progress(self, proc):
        """FFmpeg 출력을 읽어 현재 진행 시간(ms) 반환"""
        for line in proc.stdout:
            if "out_time_ms=" in line:
                try:
                    value = int(line.split('=')[1].strip())
                    yield value // 1000
                except (IndexError, ValueError):
                    continue
