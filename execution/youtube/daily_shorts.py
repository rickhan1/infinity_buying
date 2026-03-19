import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from youtube.generate_audios import generate_all_audios
from youtube.render_videos import render_dynamic_video
from youtube.upload_youtube import upload_video

def main():
    print("======================================================")
    print("🤖 [자동화] 다국어 고품질 유튜브 쇼츠 통합 파이프라인 가동")
    print("======================================================")
    
    # 1. 한국어/영어 분석 완료 대본 생성 & 타임스탬프 기반 VTT 자막 추출
    audio_data, trade_date = generate_all_audios()
    if not audio_data:
        print("생성할 쇼츠 분량이 없어 무시합니다.")
        return
        
    for lang in ['ko', 'en']:
        if lang in audio_data:
            audio_path, vtt_path, script_text = audio_data[lang]
            video_filename = f"shorts_final_{lang}.mp4"
            
            # 2. 실시간 라이브 대시보드 무인 접속 -> 동적 화면 캡처 분할 렌더링 -> 자막 합성! (Fallback 적용 완료)
            video_path = render_dynamic_video(audio_path, vtt_path, lang, video_filename, script_text)
            
            # 3. 채널별 맞춤 자동 업로드! (로컬 시청 피드백 완료 -> 실배포 가동!)
            upload_ready = True
            
            if upload_ready:
                if lang == "ko":
                    title = f"무한매수법 챌린지 {trade_date} 매매 일지 #Shorts"
                    desc = f"📈 TQQQ, SOLX 무한매수법 실전 투자 기록입니다.\n\n날짜: {trade_date}\n오늘의 매매 현황과 계좌 상태를 공유합니다.\n매일 꾸준한 기록으로 성취감을 쌓아갑니다. 함께 성투해요! 🚀"
                else:
                    title = f"Infinity Buying Strategy Day {trade_date} #Shorts"
                    desc = f"📈 Real-world TQQQ & SOLX trading log.\nDate: {trade_date}\n\nSharing today's trading status and portfolio updates. Let's keep marching forward together! 🚀"
                
                upload_video(video_path, title, desc, lang)
            else:
                print(f"🛑 유튜브 업로드 자동화가 임시 비활성화되어 있습니다. 맥북 로컬 파일({video_filename})을 열어 퀄리티를 직접 확인해 보세요!")

    print("\n🎉 모든 유튜브 다국어 파이프라인 체인이 성공적으로 완료되었습니다!")

if __name__ == "__main__":
    main()
