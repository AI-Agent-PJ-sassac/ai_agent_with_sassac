# 클라우드 배포 가이드 (GCP & AWS)

이 문서는 생성된 Docker 환경을 사용하여 Google Cloud Platform (GCP) 또는 Amazon Web Services (AWS)에 배포하는 방법을 설명합니다.

Docker를 사용하면 클라우드 배포가 매우 간편해집니다. 가장 권장되는 방식은 **관리형 컨테이너 서비스** (GCP Cloud Run, AWS App Runner)를 사용하는 것입니다. 서버 관리가 필요 없고, 트래픽에 따라 자동으로 확장됩니다.

---

## 🚀 1. Google Cloud Platform (GCP) - Cloud Run (추천)

Google Cloud Run은 컨테이너를 서버리스로 실행하는 가장 쉬운 방법입니다.

### 사전 준비
1. [Google Cloud Console](https://console.cloud.google.com/)에서 프로젝트 생성.
2. [Google Cloud CLI 설치](https://cloud.google.com/sdk/docs/install).
3. 터미널에서 로그인: `gcloud auth login`
4. 프로젝트 설정: `gcloud config set project [YOUR_PROJECT_ID]`

### 배포 방법 (소스 코드에서 바로 배포)
가장 간단한 방법입니다. 로컬 소스 코드를 구글 클라우드가 빌드하고 배포합니다.

```bash
gcloud run deploy ai-agent-service --source .
```

1. 명령어를 실행하면 리전(Region)을 선택하라고 나옵니다 (예: `asia-northeast3` - 서울).
2. "Allow unauthenticated invocations?" 질문에 `y`를 입력해야 외부에서 접속 가능합니다.
3. 배포가 완료되면 `Service URL`이 출력됩니다. (예: `https://ai-agent-service-xxxxx.a.run.app`)

---

## ☁️ 2. AWS - App Runner (추천)

AWS App Runner는 ECS나 EC2보다 설정이 훨씬 간단하며, Docker 이미지만 있으면 바로 웹 서비스로 띄워줍니다.

### 사전 준비
1. [AWS Console](https://console.aws.amazon.com/) 계정 준비.
2. [AWS CLI 설치](https://aws.amazon.com/cli/).
3. 터미널에서 로그인: `aws configure`

### 배포 방법 (ECR에 이미지 업로드 후 배포)

**1단계: ECR(Elastic Container Registry) 리포지토리 생성**
```bash
aws ecr create-repository --repository-name ai-agent-repo
```

**2단계: Docker 이미지 빌드 및 푸시**
(AWS 콘솔의 ECR 메뉴에서 'View push commands'를 누르면 정확한 명령어를 볼 수 있습니다.)

```bash
# 1. 로그인
aws ecr get-login-password --region [YOUR_REGION] | docker login --username AWS --password-stdin [YOUR_ACCOUNT_ID].dkr.ecr.[YOUR_REGION].amazonaws.com

# 2. 빌드
docker build -t ai-agent-repo .

# 3. 태그 지정
docker tag ai-agent-repo:latest [YOUR_ACCOUNT_ID].dkr.ecr.[YOUR_REGION].amazonaws.com/ai-agent-repo:latest

# 4. 푸시
docker push [YOUR_ACCOUNT_ID].dkr.ecr.[YOUR_REGION].amazonaws.com/ai-agent-repo:latest
```

**3단계: App Runner 서비스 생성**
1. AWS 콘솔에서 **App Runner** 서비스로 이동.
2. **Create service** 클릭.
3. **Source type**: Container registry 선택.
4. **Container image URI**: 방금 올린 ECR 이미지 선택.
5. **Deployment settings**: Automatic (자동 배포) 또는 Manual 선택.
6. **Configuration**: 
   - Port: `8501` (중요!)
7. 배포 완료 후 제공되는 도메인으로 접속.

---

## 🐳 3. 일반적인 VM (EC2 / GCE) 배포

전용 가상 머신(EC2 또는 Compute Engine)을 사용할 수도 있습니다. 비용 조절이 더 쉽지만, 수동 관리가 필요합니다.

1. 인스턴스(VM) 생성 (Ubuntu 추천).
2. 보안 그룹(방화벽)에서 `8501` 포트 개방.
3. SSH로 접속하여 Docker 설치.
4. 프로젝트 코드를 `git clone` 하거나 파일 복사.
5. `docker-compose up -d --build` 실행.
