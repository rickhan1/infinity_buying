import os
import asyncio
from playwright.async_api import async_playwright
from moviepy.editor import ImageClip, AudioFileClip

async def take_dashboard_screenshot(output_path):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # 세로형 쇼츠 9:16 비율 (1080x1920)
        page = await browser.new_page(viewport={"width": 1080, "height": 1920})
        print("🌐 Headless 브라우저를 열어 실시간 대시보드 캡쳐 중...")
        # 앞서 세팅된 Github Pages 라이브 페이지로 접근하여 5분 캐시 딜레이를 고려할 수도 있으나,
        # 가장 안정적이며 디자인된 화면 전체를 그대로 인용합니다.
        await page.goto("https://rickhan1.github.io/infinity_buying/")
        
        # UI 로딩 기다림
        await page.wait_for_selector("text=총 투자 원금", timeout=10000)
        # 애니메이션이 완전히 나타나고 차트가 그려질 때까지 충분히 대기
        await asyncio.sleep(5)  
        
        await page.screenshot(path=output_path, full_page=False)
        await browser.close()
        print(f"📸 고화질 스크린샷 캡쳐 완료: {output_path}")

def render_shorts_video(audio_path, trade_date):
    print("🎬 MoviePy 영상 렌더링 시작...")
    output_dir = os.path.dirname(os.path.abspath(__file__))
    screenshot_path = os.path.join(output_dir, "dashboard_bg.png")
    final_video_path = os.path.join(output_dir, "shorts_final.mp4")

    # 라이브 대시보드를 세로 비율로 찍어옴
    asyncio.run(take_dashboard_screenshot(screenshot_path))

    # 생성된 길이에 맞춘 정지 화상 비디오 클립 생성 (나레이션 음성에 동기화)
    audio_clip = AudioFileClip(audio_path)
    duration = audio_clip.duration

    bg_clip = ImageClip(screenshot_path).set_duration(duration)
    video = bg_clip.set_audio(audio_clip)

    print(f"⌛ 영상 고속 인코딩 중... 예상 길이: {duration:.2f}초")
    # 정지 화상이므로 fps를 낮춰 처리속도 비약적 향상
    video.write_videofile(final_video_path, fps=10, codec="libx264", audio_codec="aac", logger=None)
    
    print(f"✅ 1분 쇼츠 영상 렌더링 성공! {final_video_path}")
    return final_video_path

if __name__ == "__main__":
    from generate_audio import generate_audio
    audio_file, date, script = generate_audio()
    if audio_file:
        render_shorts_video(audio_file, date)
