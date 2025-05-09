import os, sys
import logging
from dotenv import load_dotenv
from influxdb_client import Point, InfluxDBClient

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

# .env 파일 로드
load_dotenv(os.path.join(os.getenv('CONFIG_DIR', 'config'), '.env'))


# -------------------------------------------------
def store_btc_candles(btc_candles):
    # InfluxDB 클라이언트 설정
    client = InfluxDBClient(url=os.getenv('INFLUXDB_URL'),
                        token=os.getenv('INFLUXDB_TOKEN'),
                        org=os.getenv('INFLUXDB_ORG'),
                        connection_pool_maxsize=25)
    write_api = client.write_api()
    
    try:
        if btc_candles:
            logger.info("비트코인 분봉 데이터 저장 중...")

            for candle in btc_candles:
                # InfluxDB에 데이터 저장
                point = Point("btc_minute_candles") \
                    .tag("symbol", "BTC") \
                    .tag("interval", "1m")

                for key, value in candle.items():
                    if isinstance(value, (int, float)):
                        point = point.field(key, value)

                write_api.write(bucket=os.getenv('INFLUXDB_BUCKET'),
                                record=point)
                logger.info(
                    f"비트코인 분봉 데이터 저장 완료 - 현재가: {candle.get('trade_price', 'N/A')}"
                )
        write_api.close()
        client.close()


    except Exception as e:
        logger.error(f"비트코인 분봉 데이터 저장중 오류 발생: {str(e)}")
    finally:
        if write_api:
            write_api.close()
        if client:
            client.close()


def store_btc_ticker(btc_ticker):
    """
    비트코인 현재가 정보를 InfluxDB에 저장하는 함수.
    Args:
        btc_ticker (dict): get_btc_current_price()의 반환값 (딕셔너리)
    """
    client = InfluxDBClient(
        url=os.getenv('INFLUXDB_URL'),
        token=os.getenv('INFLUXDB_TOKEN'),
        org=os.getenv('INFLUXDB_ORG'),
        connection_pool_maxsize=25
    )
    write_api = client.write_api()
    try:
        if btc_ticker:
            logger.info("비트코인 현재가 정보 저장 중...")

            point = Point("btc_ticker") \
                .tag("symbol", "BTC") \
                .tag("market", btc_ticker.get("market", "KRW-BTC")) \
                .tag("change", btc_ticker.get("change", "NONE"))

            # 숫자형 필드 저장 (모든 숫자를 float로 변환)
            for key, value in btc_ticker.items():
                if key in ["timestamp", "trade_timestamp"] and isinstance(value, (int, float)):
                    point = point.field(key, int(value))  # 항상 int로 저장
                elif isinstance(value, (int, float)):
                    point = point.field(key, float(value))

            # 문자열 필드 저장
            string_fields = ['trade_date', 'trade_time', 'trade_date_kst', 'trade_time_kst']
            for field in string_fields:
                if field in btc_ticker and btc_ticker[field] is not None:
                    point = point.field(field, btc_ticker[field])

            write_api.write(
                bucket=os.getenv('INFLUXDB_BUCKET'),
                record=point
            )
            logger.info(
                f"비트코인 현재가 정보 저장 완료 - 현재가: {btc_ticker.get('trade_price', 'N/A')}"
            )
        write_api.close()
        client.close()
    except Exception as e:
        logger.error(f"비트코인 현재가 정보 저장 중 오류 발생: {str(e)}")
    finally:
        if write_api:
            write_api.close()
        if client:
            client.close()


# -------------------------------------------------
if __name__ == '__main__':
    # ticker에서 가져오는 current_price
    current_price = get_btc_current_price()
    print(f"current_price : {current_price}")
    store_btc_ticker(current_price)
