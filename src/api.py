import requests
import re
# import json
import os

class SOOP:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.sooplive.com/"
        })
        self.VOD_API = "https://api.m.sooplive.com/station/video/a/view"
        self.has_cookie = False
        
    def load_cookies_from_file(self, file_path="cookie.txt"):
        """파일에서 쿠키를 읽어 세션에 적용합니다."""
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                cookie_raw = f.read().strip()                
                cookies = {}
                for item in cookie_raw.split(';'):
                    if '=' in item:
                        k, v = item.strip().split('=', 1)
                        cookies[k] = v
                if cookies:
                    self.session.cookies.update(cookies)
                    self.has_cookie = True
                    return True
        return False

    def get_video_info(self, url):
        if "vod.sooplive.com" in url:
            # URL에서 VOD 번호 추출 (예: /player/12345678)
            match = re.search(r"player/(\d+)", url)
            if not match:
                raise ValueError("올바른 VOD URL이 아닙니다.")
            v_no = match.group(1)
            return self.get_video_info_by_vno(v_no)
        else:
            raise ValueError("지원되지 않는 URL 형식입니다.")

    def get_video_info_by_vno(self, v_no):
        # API 요청 데이터
        payload = {
            "nTitleNo": v_no,
            "nApiLevel": "10",
            "nPlaylistidx": "0"
        }
        
        response = self.session.post(self.VOD_API, data=payload)
        response.raise_for_status()
        res_json = response.json()
        # print(json.dumps(res_json, ensure_ascii=False, indent=2))
        
        if res_json.get("result") == 1:
            data = res_json.get("data")
            if data.get("adult_status") == "notLogin":
                raise ValueError("로그인이 필요합니다. 쿠키 파일을 확인하세요.")
        else:
            raise ValueError("VOD 정보를 가져올 수 없습니다. (삭제되었거나 비공개일 수 있음)")
        
        title = data.get("full_title")
        total_file_duration = data.get("total_file_duration")
        file_resolution = data.get("file_resolution")
        file_type = data.get("file_type")
        
        if file_type == "REVIEW":
            id = data.get("writer_id", "")
            nick = data.get("writer_nick", "")
            original_vod = v_no
            broad_start = data.get("broad_start", "")
            
        elif file_type == "CLIP":
            id = data.get("copyright_id", "")
            nick = data.get("copyright_nickname", "")
            original_vod = data.get("original_vod", "")
            broad_start = self.get_video_info_by_vno(original_vod).get("broad_start", "")
            
        stream_url = []
        for files in data.get("files", []):
            quality_list = files.get("quality_info", [])
            best_quality = next((q for q in quality_list if q.get("resolution") == file_resolution), None)
            if not best_quality and len(quality_list) > 1:
                best_quality = quality_list[1] if quality_list[0].get("label") == "자동" else quality_list[0]
            if best_quality:
                stream_url.append((best_quality.get("file"), best_quality.get("resolution"), files.get("duration")))
                
        return {
            "title": title,
            "file_type": file_type,
            "total_file_duration": total_file_duration,
            "file_resolution": file_resolution,
            "stream_url": stream_url,
            "id": id,
            "nick": nick,
            "broad_start": broad_start,
            "original_vod": original_vod
        }

        
