import os
import asyncio
import edge_tts
from generate_scripts import generate_scripts

# KO: 여성음성(SunHi), EN: 미국 남성음성(Christopher) 또는 여성음성(Aria). 템포 약간 빠르게.
VOICE_KO = "ko-KR-SunHiNeural"
VOICE_EN = "en-US-AriaNeural"  

def format_time(ticks):
    # 1 tick = 100 ns -> 10,000 ticks = 1 ms
    # 10,000,000 ticks = 1 s
    ms = int(ticks / 10000)
    s, ms = divmod(ms, 1000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"

async def generate_audio_and_vtt(text, voice, output_audio, output_vtt):
    communicate = edge_tts.Communicate(text, voice, rate="+10%")
    
    vtt_lines = []
    
    with open(output_audio, "wb") as audio_file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                start_time = format_time(chunk["offset"])
                end_time = format_time(chunk["offset"] + chunk["duration"])
                word = chunk["text"]
                vtt_lines.append(f"{start_time} --> {end_time}\n{word}\n")
                
    with open(output_vtt, "w", encoding="utf-8") as vtt_file:
        vtt_file.write("\n".join(vtt_lines))
        
def generate_all_audios():
    script_ko, script_en, trade_date = generate_scripts()
    
    if not script_ko:
        print("매매 기록이 없어 오디오생성을 스킵합니다.")
        return None, None, trade_date

    out_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("🎙️ 한국어 나레이션 및 VTT 자막 렌더링 중...")
    audio_ko = os.path.join(out_dir, "narration_ko.mp3")
    vtt_ko = os.path.join(out_dir, "subtitles_ko.vtt")
    asyncio.run(generate_audio_and_vtt(script_ko, VOICE_KO, audio_ko, vtt_ko))
    
    print("🎙️ 영어 나레이션 및 VTT 자막 렌더링 중...")
    audio_en = os.path.join(out_dir, "narration_en.mp3")
    vtt_en = os.path.join(out_dir, "subtitles_en.vtt")
    asyncio.run(generate_audio_and_vtt(script_en, VOICE_EN, audio_en, vtt_en))
    
    print("✅ 2개 국어 나레이션 오디오 & 타임스탬프 VTT 생성 완료!")
    return {"ko": (audio_ko, vtt_ko, script_ko), "en": (audio_en, vtt_en, script_en)}, trade_date

if __name__ == "__main__":
    generate_all_audios()
