import os
import time
import datetime

from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from quotation_api import get_btc_minute_candles, get_btc_current_price
from utils import store_btc_candles, store_btc_ticker
import logging

from rich.logging import RichHandler
from rich.console import Console
from rich.theme import Theme


# 커스터마이징 
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "red",
    "critical": "red reverse"
})

console = Console(theme=custom_theme)
rich_handler = RichHandler(
    console=console,
    rich_tracebacks=True,
    tracebacks_show_locals=True,
    show_time=True,
    show_path=False
)

# 기본 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[rich_handler]
)

# 로거 가져오기
logger = logging.getLogger(__name__)

# APScheduler 로거 설정
apscheduler_logger = logging.getLogger('apscheduler')
apscheduler_logger.setLevel(logging.ERROR)
apscheduler_logger.handlers = []  # 기존 핸들러 제거
apscheduler_logger.addHandler(rich_handler)

# .env 파일 로드
load_dotenv(os.path.join(os.getenv('CONFIG_DIR', 'config'), '.env'))


# -------------------------------------------------
def main():
    logger.info(
        f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 비트코인 분봉 데이터 조회 시작"
    )

    # BTC 분봉조회
    btc_candles = get_btc_minute_candles()

    # BTC 분봉저장(influxdb)
    store_btc_candles(btc_candles)


# -------------------------------------------------
def ticker_job():
    logger.info(
        f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 비트코인 현재가 조회 시작"
    )
    
    # BTC 현재가 조회
    btc_ticker = get_btc_current_price()
    
    # BTC 현재가 저장(influxdb)
    store_btc_ticker(btc_ticker)


# -------------------------------------------------
if __name__ == "__main__":
    logger.info("BTC 가격 모니터링 시작...")

    # APScheduler 설정
    scheduler = BackgroundScheduler()
    
    # 분봉 데이터 저장 잡
    scheduler.add_job(func=main,
                      trigger=IntervalTrigger(minutes=1),
                      id='btc_minutes_candles_monitor_job',
                      name='비트코인 분봉 모니터링 작업',
                      replace_existing=True)
    
    # 현재가 저장 잡 (10초마다 실행)
    scheduler.add_job(func=ticker_job,
                      trigger=IntervalTrigger(seconds=10),
                      id='btc_ticker_monitor_job',
                      name='비트코인 현재가 모니터링 작업',
                      replace_existing=True)

    # 스케줄러 시작
    scheduler.start()

    try:
        # 메인 스레드가 종료되지 않도록 유지
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        # 프로그램 종료 시 스케줄러 종료
        scheduler.shutdown()
        logger.exception("스케줄러가 종료되었습니다.")
