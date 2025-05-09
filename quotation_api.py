import json
import requests
import logging
import datetime


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


# -------------------------------------------------
def get_btc_minute_candles(count=1, to_time=None):
    """
    BTC 분 캔들을 가져오는 함수.
    
    Args:
        count (int): 가져올 캔들의 개수 (기본값: 1)
        to_time (str): 마지막 캔들의 시간 (ISO 8601 형식, 예: "2024-03-20T00:00:00Z")
    
    Returns:
        list or None: 성공 시 캔들 데이터 리스트, 실패 시 None
    """
    # 파라미터 유효성 검사
    if count <= 0:
        logger.error("count는 양수여야 합니다.")
        return None

    if to_time:
        try:
            datetime.fromisoformat(to_time.replace('Z', '+00:00'))
        except ValueError:
            logger.error("잘못된 to_time 형식입니다.")
            return None

    url = "https://api.upbit.com/v1/candles/minutes/1"
    params = {"market": "KRW-BTC", "count": count}
    headers = {"accept": "application/json"}

    if to_time:
        params["to"] = to_time

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()

        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"API 요청 에러: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"JSON 디코딩 에러: {e}")
        return None
    except Exception as e:
        logger.error(f"비트코인 분봉 데이터 조회 중 오류 발생: {str(e)}")
        return None


# -------------------------------------------------
def get_btc_current_price():
    """
    현재 비트코인 가격을 조회하는 함수.
    
    Returns:
        float or None: 성공 시 현재 거래 가격, 실패 시 None
    """
    try:
        params = {"markets": "KRW-BTC"}
        url = "https://api.upbit.com/v1/ticker"

        res = requests.get(url, params=params)
        res.raise_for_status()
        
        data = res.json()
        if not data or not isinstance(data, list) or len(data) == 0:
            logger.exception("API 응답이 비어있거나 잘못된 형식입니다.")
            return None
            
        return data[0]
    except (requests.exceptions.RequestException, json.JSONDecodeError, KeyError, IndexError) as e:
        logger.exception(f"가격 조회 중 오류 발생: {str(e)}")
        return None


# -------------------------------------------------
if __name__ == '__main__':
    candles = get_btc_minute_candles()
    if candles:
        print(json.dumps(candles, indent=2))

    current_price = get_btc_current_price()
    print(json.dumps(current_price, indent=2))


