import os
import re
import asyncio
from playwright.async_api import async_playwright
from moviepy.editor import ImageClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips

def parse_time(time_str):
    parts = time_str.replace(',', '.').split(':')
    if len(parts) == 3:
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + float(s)
    elif len(parts) == 2:
        m, s = parts
        return int(m) * 60 + float(s)
    return float(time_str)

import platform
import PIL.Image

# 최신 Pillow(>=10.0) 버전과 MoviePy 리사이즈 모듈 호환성 해결을 위한 몽키 패치
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

# 폰트 호환성 및 퀄리티 업그레이드를 위한 BlackHanSans 폰트 절대경로
FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'BlackHanSans.ttf')

def parse_vtt(vtt_path):
    subs = []
    with open(vtt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    blocks = re.split(r'\n\n+', content.strip())
    for block in blocks:
        lines = block.strip().split('\n')
        # WEB VTT format parser
        time_line = None
        text_lines = []
        for line in lines:
            if '-->' in line:
                time_line = line
            elif time_line and line.strip() and not line.startswith('WEBVTT'):
                text_lines.append(line.strip())
        
        if time_line and text_lines:
            start_str, end_str = time_line.split(' --> ')
            start_time = parse_time(start_str.strip())
            end_time = parse_time(end_str.strip())
            text = " ".join(text_lines)
            subs.append({'start': start_time, 'end': end_time, 'text': text})
    return subs

def determine_scenes(subs, total_duration):
    scenes = []
    current_bg = "tqqq_chart"
    last_time = 0.0
    
    tqqq_seen = False
    solx_seen = False
    
    for sub in subs:
        word = sub['text'].upper()
        t = sub['start']
        
        # TQQQ 언급시 차트로 (최초 1회)
        if not tqqq_seen and ("TQQQ" in word):
            tqqq_seen = True
            scenes.append({"bg": current_bg, "start": last_time, "end": t})
            current_bg = "tqqq_chart"
            last_time = t
            
        # 히스토리 언급시 표로 스크롤
        elif tqqq_seen and not solx_seen and any(k in word for k in ["히스토리", "표", "현황", "TABLE", "HISTORY", "TRANSACTION"]):
            if current_bg == "tqqq_chart":
                scenes.append({"bg": current_bg, "start": last_time, "end": t})
                current_bg = "tqqq_table"
                last_time = t
                
        # SOLX 언급시 탭 변경
        elif not solx_seen and ("SOLX" in word):
            solx_seen = True
            scenes.append({"bg": current_bg, "start": last_time, "end": t})
            current_bg = "solx_chart"
            last_time = t
            
        # SOLX 히스토리
        elif solx_seen and any(k in word for k in ["히스토리", "표", "현황", "TABLE", "HISTORY", "TRANSACTION", "SPECIFIC"]):
            if current_bg == "solx_chart":
                scenes.append({"bg": current_bg, "start": last_time, "end": t})
                current_bg = "solx_table"
                last_time = t

    scenes.append({"bg": current_bg, "start": last_time, "end": total_duration})
    
    # 0초짜리 씬 제거
    return [s for s in scenes if s["end"] > s["start"]]

def determine_scenes_fallback(script_text, total_duration):
    scenes = []
    current_bg = "tqqq_chart"
    last_time = 0.0
    total_chars = len(script_text)
    if total_chars == 0: return [{"bg": current_bg, "start": 0, "end": total_duration}]
    time_per_char = total_duration / total_chars
    
    idx_tqqq = script_text.find("TQQQ")
    idx_solx = script_text.find("SOLX")
    
    t_tqqq = idx_tqqq * time_per_char if idx_tqqq != -1 else -1
    t_solx = idx_solx * time_per_char if idx_solx != -1 else -1
    
    idx_t_hist = max(script_text.find("히스토리", max(0, idx_tqqq)), script_text.find("history", max(0, idx_tqqq)))
    t_t_hist_time = idx_t_hist * time_per_char if idx_t_hist > 0 else -1
    
    idx_s_hist = max(script_text.find("히스토리", max(0, idx_solx)), script_text.find("history", max(0, idx_solx)))
    t_s_hist_time = idx_s_hist * time_per_char if idx_s_hist > 0 else -1

    times = [
        (t_tqqq, "tqqq_chart"),
        (t_t_hist_time, "tqqq_table"),
        (t_solx, "solx_chart"),
        (t_s_hist_time, "solx_table")
    ]
    
    valid_times = sorted([x for x in times if x[0] > 0], key=lambda x: x[0])
    
    for t_val, bg in valid_times:
        if t_val > last_time:
            scenes.append({"bg": current_bg, "start": last_time, "end": t_val})
            current_bg = bg
            last_time = t_val
            
    scenes.append({"bg": current_bg, "start": last_time, "end": total_duration})
    return scenes

def generate_subs_fallback(script_text, total_duration, lang):
    total_chars = len(script_text)
    if total_chars == 0: return []
    
    words = script_text.split()
    subs = []
    
    current_chunk = []
    char_limit = 14 if lang == 'ko' else 26
    
    chunks = []
    for word in words:
        current_chunk.append(word)
        joined = " ".join(current_chunk)
        # 구두점으로 끝나거나 일정 길이에 도달하면 자막 한 줄로 배정
        if len(joined) >= char_limit or word[-1] in ".,!?\n":
            chunks.append(joined)
            current_chunk = []
    if current_chunk:
        chunks.append(" ".join(current_chunk))
        
    search_idx = 0
    for chunk in chunks:
        idx = script_text.find(chunk, search_idx)
        if idx == -1: continue # 만약 매치 실패 시 건너뜀
        
        start_time = (idx / total_chars) * total_duration
        end_time = ((idx + len(chunk)) / total_chars) * total_duration + 0.3
        
        # 이전 자막의 끝 시간을 현재 시작 시간으로 맞춰 겹침 방지 (연속성 부여)
        if subs and subs[-1]['end'] > start_time:
            subs[-1]['end'] = start_time
            
        subs.append({'start': start_time, 'end': min(end_time, total_duration), 'text': chunk.strip()})
        search_idx = idx + len(chunk)
        
    if subs:
        subs[-1]['end'] = total_duration
        
    return subs

async def take_screenshots(out_dir, lang="ko"):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # 📱 모바일 UX 퀄리티를 폭발시키기 위해 iPhone 14 Pro Max급 세로형 고해상도(3x) 뷰포트로 강제 렌더링
        context = await browser.new_context(
            viewport={'width': 430, 'height': 932},
            device_scale_factor=3
        )
        page = await context.new_page()
        
        # ⚡ 데이터 동기화 레이스 컨디션 방지 아키텍처
        # 깃허브 페이지 배포 지연(~1분)을 우회하고 가장 타임스탬프가 빠른 최신 데이터를 캡처하기 위해, 로컬 서버(localhost:5173)를 타겟팅합니다.
        # Vite의 base 설정(/infinity_buying/)을 반드시 경로에 포함해야 합니다.
        url = f"http://localhost:5173/infinity_buying/?lang={lang}"
        print(f"🌐 라이브 대시보드({lang.upper()}) 모바일 씬(Scene)별 캡쳐 중... (URL: {url})")
        await page.goto(url)
        
        wait_text = "text=총 투자 원금" if lang == "ko" else "text=Initial Capital"
        # 서버 기동 및 데이터 로딩 시간을 고려하여 30초로 넉넉하게 연장
        await page.wait_for_selector(wait_text, timeout=30000)
        await asyncio.sleep(5)
        
        # 1. TQQQ Chart (Top)
        await page.screenshot(path=os.path.join(out_dir, "tqqq_chart.png"))
        print("- TQQQ 차트 캡쳐")
        
        # 2. TQQQ Table (Scroll down)
        await page.evaluate("window.scrollBy(0, 800)")
        await asyncio.sleep(1)
        await page.screenshot(path=os.path.join(out_dir, "tqqq_table.png"))
        print("- TQQQ 상세 표 캡쳐")
        
        # 3. SOLX Chart (Click SOLX tab, scroll top)
        await page.evaluate("window.scrollTo(0, 0)")
        await page.click("text=SOLX")
        await asyncio.sleep(2)
        await page.screenshot(path=os.path.join(out_dir, "solx_chart.png"))
        print("- SOLX 차트 캡쳐")
        
        # 4. SOLX Table (Scroll down)
        await page.evaluate("window.scrollBy(0, 800)")
        await asyncio.sleep(1)
        await page.screenshot(path=os.path.join(out_dir, "solx_table.png"))
        print("- SOLX 상세 표 캡쳐")
        
        await browser.close()
        
def render_dynamic_video(audio_path, vtt_path, lang, output_filename, script_text=""):
    print(f"🎬 {lang.upper()} 동적 영상 렌더링 시작...")
    output_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 각 언어마다 새로운 스크린샷 캡처
    asyncio.run(take_screenshots(output_dir, lang))

    audio_clip = AudioFileClip(audio_path)
    total_duration = audio_clip.duration
    
    subs = parse_vtt(vtt_path)
    if not subs and script_text:
        print("⚠️ VTT 파일이 비어있습니다. 자체 Fallback(비율 연산) 엔진으로 자막과 씬을 복구합니다.")
        subs = generate_subs_fallback(script_text, total_duration, lang)
        scenes = determine_scenes_fallback(script_text, total_duration)
    else:
        scenes = determine_scenes(subs, total_duration)
    
    bg_clips = []
    for s in scenes:
        img_path = os.path.join(output_dir, f"{s['bg']}.png")
        if not os.path.exists(img_path):
            img_path = os.path.join(output_dir, "tqqq_chart.png") # 펠백
        dur = s['end'] - s['start']
        if dur < 0.1: dur = 0.1
        
        # 기본 클립
        clip = ImageClip(img_path).set_start(s['start']).set_duration(dur)
        
        # 🎬 시네마틱 줌 / 트래킹 효과 적용
        if "chart" in s['bg']:
            # 차트는 가로 기준 1.7배까지 시원하게 줌인 (화면 꽉 차게)
            # 최근 데이터가 우측에 있으므로, 처음엔 우측 끝을 비추다가 서서히 좌측으로 이동하는 패닝 효과
            clip = clip.resize(width=1080 * 1.7)
            # 람다식으로 시간에 따른 x 좌표를 동적 계산 (-400 부터 시작해서 부드럽게 글라이딩)
            clip = clip.set_position(lambda t, d=dur: (int(-400 + 150 * (t / d)), 'center'))
        elif "table" in s['bg']:
            # 히스토리 상세 표는 가로 1.3배 줌인하여 텍스트 가독성 극대화
            # 가장 중요한 '오늘 발생한 매매내역'이 테이블 최상단에 있으므로 y위치를 위쪽(Top)에 포커스
            clip = clip.resize(width=1080 * 1.3)
            # y축을 살짝 위(150px)에서 아래 방향으로 느리게 훑어 내림
            clip = clip.set_position(lambda t, d=dur: ('center', int(150 - 100 * (t / d))))
            
        bg_clips.append(clip)

    # 상단 대제목 텍스트 클립 (고정)
    # 이모지는 ImageMagick 외부 폰트 연동 시 에러를 유발하므로 제거하고 간결하고 임팩트 있는 제목 구사
    title_text = "기계의 무한매수 실전" if lang == 'ko' else "Emotionless Trading"
    title_clip = TextClip(title_text, font=FONT_PATH, fontsize=100, color='yellow', 
                          stroke_color='black', stroke_width=5, align='center', method='label')
    # 제목은 최상단으로 한껏 올려 시야 확보
    title_clip = title_clip.set_position(('center', 150)).set_duration(total_duration)

    # VTT 자막 텍스트 클립 (트렌디한 쇼츠/틱톡 스타일)
    subtitle_clips = []
    for sub in subs:
        word = sub['text'].replace('.','').replace(',','') # 영상 표시용으로는 구두점 제거
        if not word.strip(): continue
        dur = sub['end'] - sub['start']
        if dur < 0.1: dur = 0.1 
        
        try:
            # 폰트 사이즈 대폭 상향, 프리미엄 폰트로 강렬한 시인성
            txt_clip = TextClip(word, font=FONT_PATH, fontsize=110, color='white', 
                                stroke_color='black', stroke_width=6, method='caption', size=(950, None))
            # 화면 가장 하단(y축 1550)으로 내려 중앙의 차트/표를 가리지 않음
            txt_clip = txt_clip.set_position(('center', 1550)).set_start(sub['start']).set_duration(dur)
            subtitle_clips.append(txt_clip)
        except Exception as e:
            print(f"자막 렌더링 중 오류 발생: {e}")
            
    final_video = CompositeVideoClip(bg_clips + [title_clip] + subtitle_clips, size=(1080, 1920)).set_duration(total_duration)
    final_video = final_video.set_audio(audio_clip)

    out_path = os.path.join(output_dir, output_filename)
    print(f"⌛ [렌더링 타임라인] 총 길이: {total_duration:.2f}초, 컷 수: {len(scenes)}, 단어 자막 수: {len(subs)}")
    final_video.write_videofile(out_path, fps=24, codec="libx264", audio_codec="aac", logger=None)
    print(f"✅ {lang.upper()} 영상 렌더링 완료! {out_path}")
    return out_path

if __name__ == "__main__":
    from generate_audios import generate_all_audios
    res, _ = generate_all_audios()
    if res:
        ko_data = res.get("ko")
        en_data = res.get("en")
        if ko_data:
            render_dynamic_video(ko_data[0], ko_data[1], 'ko', "shorts_ko.mp4", ko_data[2])
        if en_data:
            render_dynamic_video(en_data[0], en_data[1], 'en', "shorts_en.mp4", en_data[2])
