# Week4 - Python Socket Server

curl로 보낸 HTTP 요청을 받아 파일로 저장하는 소켓 서버.

- 실습 1: 요청 원문을 `request/년-월-일-시-분-초.bin` 으로 저장
- 실습 2: multipart로 받은 이미지를 별도 파일로 저장

## 실행

```
python SocketServer.py
```

다른 터미널에서

```
curl -X POST -S -H "Authorization: JWT b181ce4155b7413ebd1d86f1379151a7e035f8bd" -F "author=1" -H 'Accept: application/json' -F "title=curl 테스트" -F "text=API curl로 작성된 AP 테스트 입력 입니다." -F "created_date=2024-06-10T18:34:00+09:00" -F "published_date=2024-06-10T18:34:00+09:00" -F "image=@./KakaoTalk_20260928_000324829.jpg;type=image/jpg" http://127.0.0.1:8000/api_root/Post/
```

## 파일

- `SocketServer.py` - 서버
- `response.bin` - 서버가 보내는 응답 메시지
- `KakaoTalk_20260928_000324829.jpg` - 전송한 이미지
- `request/2026-09-28-00-09-40.bin` - 저장된 요청 원문
- `request/2026-09-28-00-09-40_KakaoTalk_20260928_000324829.jpg` - 추출한 이미지
