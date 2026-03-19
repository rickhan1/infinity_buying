import os
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

def get_authenticated_service(lang="ko"):
    creds = None
    token_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'token_{lang}.pickle')
    
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
            
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        else:
            print(f"ℹ️ [{lang.upper()}] 채널용 인증 파일(token_{lang}.pickle)이 없습니다. 유튜브 업로드를 보류합니다.")
            return None
            
    return build('youtube', 'v3', credentials=creds)

def upload_video(video_path, title, description, lang="ko"):
    youtube = get_authenticated_service(lang)
    if not youtube: return False

    request_body = {
        'snippet': {
            'title': title,
            'description': description + "\n\n#Shorts #무한매수법",
            'tags': ['Shorts', '주식투자', '무한매수법', 'TQQQ', '자동매매'],
            'categoryId': '27'
        },
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': False
        }
    }

    media_file = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media_file
    )

    print(f"🚀 유튜브 클라우드로 [{lang.upper()}] 쇼츠 업로드 전송 중... ({title})")
    response = request.execute()
    print(f"✅ 완전 자동 업로드 성공! 동영상 확인 링크: https://youtu.be/{response['id']}")
    return True

if __name__ == "__main__":
    upload_video("shorts_ko.mp4", "무한매수법 테스트 #Shorts", "테스트 영상입니다.", "ko")
