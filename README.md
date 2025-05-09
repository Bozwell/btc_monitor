# 비트코인 시세 모니터(feat upbit api)

### Introduction
이 프로젝트는 Upbit API를 사용하여 비트코인 가격을 가져와서 저장하고 시각화 할 목적으로 만들었습니다. 

가져오는 정보
- BTC 분봉(1분 간격)
- BTC ticker (10초 간격)

### Requirements
#### API Credential
본 프로젝트에서는 upbit api를 사용하였습니다. api호출을 위해 회원가입 및 api 접근권한을 획득하여야 합니다.

#### Data Store
api를 통해 가져온 정보는 influxdb에 저장합니다. 연결정보는 .env 파일에 설정합니다.


### 설정
소스를 clone 받고... config/.env.example 를 .env 로 복사하여 필요한 정보를 채워줍니다.
```
https://github.com/Bozwell/btc_monitor.git
cd stock-monitor
cp config/.env.example config/.env
```

#### ddocker build & run
docker가 설치된 환경에서 git 으로 소스를 clone받은후 build.sh를 이용하시면 됩니다.
```
sh build.sh
```