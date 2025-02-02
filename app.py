from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash
import os
import traceback
from yt_dlp import YoutubeDL
from dotenv import load_dotenv
from googleapiclient.discovery import build
import requests
from flask_caching import Cache

# 환경 변수 로드
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')
app.config['DOWNLOAD_FOLDER'] = os.path.join(os.getcwd(), 'downloads')

# 다운로드 폴더가 없으면 생성
if not os.path.exists(app.config['DOWNLOAD_FOLDER']):
    os.makedirs(app.config['DOWNLOAD_FOLDER'])

# 캐싱 설정 (간단한 메모리 캐시 사용)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# YouTube API 설정
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

def get_client_country(ip_address):
    """
    클라이언트 IP를 기반으로 국가 코드를 반환합니다.
    ip-api.com 무료 API 사용
    """
    cached_country = cache.get(ip_address)
    if cached_country:
        return cached_country

    try:
        response = requests.get(f"http://ip-api.com/json/{ip_address}")
        data = response.json()
        if data.get('status') == 'success':
            country_code = data.get('countryCode')
            cache.set(ip_address, country_code, timeout=60*60)  # 1시간 캐시
            return country_code
        else:
            return 'KR'  # 기본값: 한국
    except Exception as e:
        print("Error fetching geolocation data:", e)
        return 'KR'

def get_trending_videos(country_code):
    """
    지정된 국가의 트렌딩 동영상을 YouTube API로 가져옵니다.
    """
    try:
        request_trending = youtube.videos().list(
            part='snippet,contentDetails,statistics',
            chart='mostPopular',
            regionCode=country_code,
            maxResults=6
        )
        response = request_trending.execute()
        videos = []
        for item in response.get('items', []):
            video = {
                'title': item['snippet']['title'],
                'thumbnail': item['snippet']['thumbnails']['high']['url'],
                'url': f"https://www.youtube.com/watch?v={item['id']}"
            }
            videos.append(video)
        return videos
    except Exception as e:
        print("Error fetching trending videos:", e)
        return []

@app.route('/', methods=['GET', 'POST'])
def index():

        
    if request.method == 'POST' and 'youtube_url' in request.form:
        youtube_url = request.form.get('youtube_url')
        format_choice = request.form.get('format')
        filename = None

        if not youtube_url:
            flash('유튜브 링크를 입력해주세요.')
            return redirect(url_for('index'))

        if format_choice not in ['mp4', 'mp3']:
            flash('지원하지 않는 형식입니다.')
            return redirect(url_for('index'))

        try:
            if format_choice == 'mp4':
                ydl_opts = {
                    # MP4 컨테이너(비디오) + M4A(AAC 오디오)를 우선적으로 선택
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
                    
                    # 다운로드 파일명 설정
                    'outtmpl': os.path.join(app.config['DOWNLOAD_FOLDER'], '%(title)s.%(ext)s'),
                    
                    # 최종 출력 파일 컨테이너
                    'merge_output_format': 'mp4',
                }
            elif format_choice == 'mp3':
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(app.config['DOWNLOAD_FOLDER'], '%(title)s.%(ext)s'),
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                }

            # 다운로드 실행
            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(youtube_url, download=True)
                filename = ydl.prepare_filename(info_dict)

                if format_choice == 'mp3':
                    filename = os.path.splitext(os.path.basename(filename))[0] + '.mp3'
                else:
                    filename = os.path.basename(filename)

            return redirect(url_for('download_file', filename=filename))
        except Exception as e:
            error_message = traceback.format_exc()
            print(f'오류 발생: {error_message}')
            flash(f'다운로드 중 오류가 발생했습니다: {str(e)}')
            return redirect(url_for('index'))
    ip_address = request.remote_addr
    country_code = get_client_country(ip_address)
    trending_videos = get_trending_videos(country_code)
    return render_template('index.html', country_code=country_code, trending_videos=trending_videos)
    
@app.route('/download/<filename>')
def download_file(filename):
    safe_filename = os.path.basename(filename)
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], safe_filename, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

