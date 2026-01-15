# ☁️ Google Cloud Platform (GCP) Deployment Guide

이 문서는 **AI Agent** 서비스를 Google Cloud Platform의 **Compute Engine (VM)** 에 배포하는 방법을 안내합니다.

---

## 📋 1. 사전 준비 (Pre-requisites)
1.  **Google Cloud 계정** 및 결제 계정 등록 완료
2.  **새 프로젝트 생성** (예: `ai-agent-project`)

---

## 🖥️ 2. VM 인스턴스 생성 (Create Instance)
1.  GCP Console > **Compute Engine** > **VM 인스턴스** 로 이동
2.  **[인스턴스 만들기]** 클릭
3.  **설정 값** (권장):
    *   **이름**: `ai-agent-server`
    *   **리전**: `asia-northeast3` (서울)
    *   **머신 유형**: `e2-medium` (vCPU 2개, 4GB 메모리) - *비용 절감 시 e2-small 가능하나 빌드 시 느릴 수 있음*
    *   **부팅 디스크**:
        *   운영체제: **Ubuntu**
        *   버전: **Ubuntu 22.04 LTS** (x86/64)
        *   크기: **20GB** 이상 (Docker 이미지 및 벡터 DB 저장용)
    *   **방화벽**: `HTTP 트래픽 허용`, `HTTPS 트래픽 허용` 체크

4.  **[만들기]** 클릭 (1~2분 소요)

---

## 🛠️ 3. 서버 환경 설정 (Setup Environment)
VM 목록에서 `SSH` 버튼을 눌러 터미널을 엽니다.

### 3.1 Docker & Docker Compose 설치
```bash
# 패키지 업데이트
sudo apt-get update

# 필수 패키지 설치
sudo apt-get install -y ca-certificates curl gnupg

# Docker GPG 키 추가
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Docker Repository 설정
echo \
  "deb [arch=\"$(dpkg --print-architecture)\" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  \"$(. /etc/os-release && echo "$VERSION_CODENAME")\" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Docker 설치
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 권한 설정 (로그아웃 없이 적용)
sudo usermod -aG docker $USER
newgrp docker
```

---

## 🚀 4. 프로젝트 배포 (Deploy Project)

### 4.1 코드 업로드
Github를 사용하거나 로컬 파일을 직접 업로드할 수 있습니다. 여기서는 터미널에서 직접 파일을 생성하는 방식을 예시로 듭니다. (또는 Github Repo가 있다면 `git clone` 사용)

**방법 A: Git 사용 (권장)**
```bash
# 깃허브 레포지토리가 있다면
git clone <YOUR_REPOSITORY_URL>
cd <REPOSITORY_NAME>
```

**방법 B: 파일 직접 전송 (SCP 또는 gcloud CLI)**
로컬 터미널(내 컴퓨터)에서 아래 명령어로 프로젝트 폴더를 서버로 전송합니다.
```bash
# gcloud CLI를 설치했다면
gcloud compute scp --recurse "C:\Users\SSAFY\Desktop\fastcampus\ai_agent_with_sassac" ai-agent-server:~/ai_agent --zone=asia-northeast3-a
```

### 4.2 환경 변수 설정
서버의 프로젝트 폴더 내에 `.env` 파일을 생성합니다.
```bash
cd ~/ai_agent # (프로젝트 폴더명에 맞게 조정)
nano .env
```
(`UPSTAGE_API_KEY=...` 내용을 붙여넣고 `Ctrl+X`, `Y`, `Enter`로 저장)

### 4.3 서비스 실행
```bash
# 빌드 및 백그라운드 실행
docker compose up -d --build
```
*   `e2-medium` 기준 약 5~10분 소요될 수 있습니다.

---

## 🌐 5. 방화벽 설정 (Firewall Rules)
기본적으로 80포트는 열려있지만, 혹시 접속이 안 된다면 VPC 네트워크 설정을 확인해야 합니다.

1.  GCP Console > **VPC 네트워크** > **방화벽**
2.  `default-allow-http` 규칙이 있는지 확인 (포트 80 허용)
3.  만약 API 서버(8000)도 외부에서 직접 접속해야 한다면(보통은 불필요) 8000번도 열어줘야 합니다.

---

## ✅ 6. 접속 확인
브라우저 주소창에 VM의 **외부 IP 주소**를 입력하세요.
Example: `http://34.12.34.56`

인수인계 AI 에이전트가 뜬다면 성공입니다! 🎉

---

## 🔄 7. 유지보수
### 업데이트 시
1.  코드 수정 (git pull 등)
2.  재배포:
    ```bash
    docker compose up -d --build
    ```

### 로그 확인
```bash
docker compose logs -f
```
