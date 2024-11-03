const express = require('express');
const { exec } = require('child_process');
const fs = require('fs');  // fs 모듈을 파일 상단에서 불러옵니다.
const app = express();
const PORT = 3000;
const cors = require('cors');

app.use(cors()); // 모든 도메인에서의 요청을 허용


// 다운로드 폴더 경로
const DOWNLOAD_DIR = './downloads/';

// 서버 시작 시 폴더 확인 및 생성
if (!fs.existsSync(DOWNLOAD_DIR)) {
  fs.mkdirSync(DOWNLOAD_DIR, { recursive: true });
}




function sendActualFileName(res, downloadPath) {
  fs.readdir(downloadPath, (err, files) => {
    if (err) {
      console.error(`Error reading directory: ${err}`);
      res.status(500).send('Failed to read download directory.');
      return;
    }
    const downloadedFile = files.find(file => file.startsWith('downloaded'));
    if (downloadedFile) {
      res.send(`Download completed! File saved as ${downloadedFile}`);
    } else {
      res.status(404).send('Downloaded file not found.');
    }
  });
}
function downloadVideo(url, format, res) {
  const outputPath = `./downloads/downloaded.%(ext)s`;
  const command = `yt-dlp -f ${format} "${url}" -o "${outputPath}"`;
  
  exec(command, (error, stdout, stderr) => {
    if (error) {
      console.error(`exec error: ${error}`);
      console.error(`stderr: ${stderr}`);
      res.status(500).send('Error occurred during download.');
      return;
    }
    console.log(`stdout: ${stdout}`);
    console.error(`stderr: ${stderr}`);
    sendActualFileName(res, './downloads'); // 파일 저장 폴더 경로
  });
}


// 비디오 변환 함수
function convertVideo(input, output, format, res) {
  const command = `ffmpeg -i ${input} -c:v ${format} ${output}`;
  
  exec(command, (error, stdout, stderr) => {
    if (error) {
      console.error(`exec error: ${error}`);
      res.status(500).send('Error occurred during conversion.');
      return;
    }
    console.log(`stdout: ${stdout}`);
    console.error(`stderr: ${stderr}`);
    res.send(`Conversion completed! Output file saved as ${output}`);
  });
}

// 다운로드 요청 처리 라우트
app.post('/download', (req, res) => {
  const { url, format } = req.body;
  downloadVideo(url, format, res);
});


// 변환 요청 처리 라우트
app.post('/convert', (req, res) => {
  const { input, output, format } = req.body;
  if (!input || !output || !format) {
    res.status(400).send('Missing required parameters: input, output, or format');
    return;
  }
  convertVideo(input, output, format, res);
});

// 서버 실행
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
