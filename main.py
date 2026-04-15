from src.core import SOOPDownloader
from rich.console import Console
from rich.progress import Progress
from src.api import SOOP
import src.util

console = Console()

def main():
    url = console.input("[bold green]URL 입력: [/] ")
    api = SOOP()
    api.load_cookies_from_file()
    video_info = api.get_video_info(url)
    src.util.print_metadata(video_info)
    
    section = console.input("[bold green]다운로드 받을 파트 번호 입력: [/] ")
    section = set(int(x) for x in section.split())
    
    downloader = SOOPDownloader()

    with Progress() as progress:
        current_task = None
        
        def my_callback(percent, msg):
            nonlocal current_task
            if percent == -1: 
                progress.console.print(f"[red]{msg}[/]")
                return
            if msg == "준비중":
                current_task = progress.add_task(msg, total=100)
            if current_task is not None:
                progress.update(current_task, completed=percent, description=msg)

        downloader.download_video(video_info, section, callback=my_callback)

if __name__ == "__main__":
    main()
    