from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash
import os
import traceback
from yt_dlp import YoutubeDL
from pydub import AudioSegment
from dotenv import load_dotenv
from googleapiclient.discovery import build
import requests
from flask_caching import Cache  # Cache 임포트 추가

# 환경 변수 로드
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')
app.config['DOWNLOAD_FOLDER'] = os.path.join(os.getcwd(), 'downloads')

# 다운로드 폴더가 없으면 생성
if not os.path.exists(app.config['DOWNLOAD_FOLDER']):
    os.makedirs(app.config['DOWNLOAD_FOLDER'])

# 캐싱 설정
cache = Cache(app, config={'CACHE_TYPE': 'simple'})  # app이 먼저 정의되어야 함

# YouTube API 설정
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

def get_client_country(ip_address):
    """
    IP 주소를 기반으로 클라이언트의 국가 코드를 반환합니다.
    ip-api.com의 무료 API를 사용합니다.
    """
    cached_country = cache.get(ip_address)
    if cached_country:
        return cached_country

    try:
        response = requests.get(f"http://ip-api.com/json/{ip_address}")
        data = response.json()
        if data['status'] == 'success':
            country_code = data['countryCode']
            cache.set(ip_address, country_code, timeout=60*60)  # 1시간 동안 캐싱
            return country_code
        else:
            return 'KR'  # 기본값: 한국
    except Exception as e:
        print("Error fetching geolocation data:", e)
        return 'KR'  # 기본값: 한국

def get_trending_videos(country_code):
    """
    YouTube Data API를 사용하여 지정된 국가의 트렌딩 동영상을 가져옵니다.
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
    # 클라이언트의 IP 주소 가져오기
    if request.headers.getlist("X-Forwarded-For"):
        ip_address = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip_address = request.remote_addr

    # 클라이언트의 국가 코드 가져오기
    country_code = get_client_country(ip_address)
    print(f"Detected country code: {country_code}")  # 국가 코드 출력
    trending_videos = get_trending_videos(country_code)
    
    if request.method == 'POST':
        youtube_url = request.form.get('youtube_url')
        format_choice = request.form.get('format')

        # 유튜브 URL 유효성 검사
        if not youtube_url:
            flash('유튜브 링크를 입력해주세요.')
            return redirect(url_for('index'))

        try:
            ydl_opts = {}
            if format_choice == 'mp4':
                ydl_opts = {
                    'format': 'bestvideo+bestaudio/best',
                    'outtmpl': os.path.join(app.config['DOWNLOAD_FOLDER'], '%(title)s.%(ext)s'),
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
            else:
                flash('지원하지 않는 형식입니다.')
                return redirect(url_for('index'))

            with YoutubeDL(ydl_opts) as ydl:
                if format_choice == 'mp3':
                    filename = os.path.splitext(os.path.basename(filename))[0] + '.mp3'
                else:
                    filename = os.path.basename(filename)

            return redirect(url_for('download_file', filename=filename))

        except Exception as e:
            error_message = traceback.format_exc()
            print(error_message)
            flash(f'다운로드 중 오류가 발생했습니다: {str(e)}')
            return redirect(url_for('index'))

    return render_template('index.html', trending_videos=trending_videos, country_code=country_code)

@app.route('/download/<filename>')
def download_file(filename):
    # 파일명에서 디렉토리 경로를 제거하고, 안전하게 파일을 전달
    safe_filename = os.path.basename(filename)
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], safe_filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
