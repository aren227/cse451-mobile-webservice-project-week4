import os
import re
import socket
from datetime import datetime


class SocketServer:
    def __init__(self):
        self.bufsize = 1024  # 버퍼 크기 설정
        with open('./response.bin', 'rb') as file:
            self.RESPONSE = file.read()  # 응답 파일 읽기
        self.DIR_PATH = './request'
        self.createDir(self.DIR_PATH)

    def createDir(self, path):
        """디렉토리 생성"""
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except OSError:
            print("Error: Failed to create the directory.")

    def recvRequest(self, clnt_sock):
        received = b""
        while b"\r\n\r\n" not in received:
            chunk = clnt_sock.recv(self.bufsize)
            if not chunk:
                return received
            received += chunk

        header, body = received.split(b"\r\n\r\n", 1)

        # 응답해주지 않으면 curl이 1초 기다렸다가 본문을 보낸다
        if re.search(rb"^Expect:\s*100-continue", header, re.I | re.M):
            clnt_sock.sendall(b"HTTP/1.1 100 Continue\r\n\r\n")

        matched = re.search(rb"^Content-Length:\s*(\d+)", header, re.I | re.M)
        if matched:
            length = int(matched.group(1))
            chunks, size = [body], len(body)
            while size < length:
                chunk = clnt_sock.recv(self.bufsize)
                if not chunk:
                    break
                chunks.append(chunk)
                size += len(chunk)
            body = b"".join(chunks)

        return header + b"\r\n\r\n" + body

    def saveImages(self, request, stamp):
        header, _, body = request.partition(b"\r\n\r\n")

        matched = re.search(rb"^Content-Type:\s*multipart/form-data;.*?boundary=(.+?)\s*$",
                            header, re.I | re.M)
        if not matched:
            return []
        boundary = b"--" + matched.group(1).strip(b'"')

        saved = []
        for part in body.split(boundary):
            part_header, sep, content = part.partition(b"\r\n\r\n")
            if not sep:
                continue
            if not re.search(rb"^Content-Type:\s*image/", part_header, re.I | re.M):
                continue

            # 끝의 CRLF는 다음 boundary와 붙어있던 것
            if content.endswith(b"\r\n"):
                content = content[:-2]

            matched = re.search(rb'filename="([^"]*)"', part_header)
            filename = os.path.basename(matched.group(1).decode("utf-8", "replace")) if matched else ""
            if not filename:
                filename = "image." + re.search(rb"image/([\w.+-]+)", part_header, re.I).group(1).decode()

            path = os.path.join(self.DIR_PATH, f"{stamp}_{filename}")
            with open(path, "wb") as file:
                file.write(content)
            saved.append(path)

        return saved

    def run(self, ip, port):
        """서버 실행"""
        # 소켓 생성
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((ip, port))
        self.sock.listen(10)

        print("Start the socket server...")
        print("\"Ctrl+C\" for stopping the server!\r\n")

        try:
            while True:
                # 클라이언트의 요청 대기
                clnt_sock, req_addr = self.sock.accept()
                clnt_sock.settimeout(5.0)  # 타임아웃 설정(5초)

                print("Request message...\r\n")

                response = b""
                # 여기에 구현 하세요
                try:
                    response = self.recvRequest(clnt_sock)
                    print(response.split(b"\r\n\r\n", 1)[0].decode("utf-8", "replace"))
                    print()

                    stamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

                    bin_path = os.path.join(self.DIR_PATH, stamp + ".bin")
                    with open(bin_path, "wb") as file:
                        file.write(response)
                    print(f"Saved request : {bin_path} ({len(response)} bytes)")

                    for path in self.saveImages(response, stamp):
                        print(f"Saved image   : {path} ({os.path.getsize(path)} bytes)")
                    print()

                    # 응답 전송
                    clnt_sock.sendall(self.RESPONSE)
                except socket.timeout:
                    print("Timeout\r\n")
                finally:
                    # 클라이언트 소켓 닫기
                    clnt_sock.close()
        except KeyboardInterrupt:
            print("\r\nStop the server...")
            # 서버 소켓 닫기
            self.sock.close()


if __name__ == "__main__":
    server = SocketServer()
    server.run("127.0.0.1", 8000)
