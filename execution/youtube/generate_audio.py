import os
import asyncio
import edge_tts
from generate_script import generate_script

# 한국어 자연스러운 여성/남성 음성 (SunHi는 여성음성)
VOICE = "ko-KR-SunHiNeural"  

async def generate_audio_file(text, output_file):
    communicate = edge_tts.Communicate(text, VOICE, rate="+10%")
    await communicate.save(output_file)
    
def generate_audio():
    script_text, trade_date = generate_script()
    
    if "아직 매매 기록이 존재하지 않습니다" in script_text:
        print("매매 기록이 없어 오디오를 생성하지 않습니다.")
        return None, trade_date

    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(output_dir, "narration.mp3")
    
    print(f"🎙️ Edge TTS로 나레이션 생성 중... ({output_file})")
    asyncio.run(generate_audio_file(script_text, output_file))
    print("✅ 나레이션 오디오 파일 생성 완료!")
    
    return output_file, trade_date, script_text

if __name__ == "__main__":
    generate_audio()
