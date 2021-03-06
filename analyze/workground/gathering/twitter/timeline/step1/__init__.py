from pathlib import Path
import os

from common import get_logger
from repository import FileRepository

from external.twitter.repository import TwitterRepository


logger = get_logger(__file__)


def get_path(path="output"):
    base_path = Path(os.path.dirname(__file__)).resolve()
    return str(base_path / path)


def run(screen_name: str):
    """タイムライン情報取得コマンド"""

    logger.info("{}のタイムライン情報を取得します。".format(screen_name))
    twitter_repository = TwitterRepository()
    time_lines = twitter_repository.get_user_timeline_by_user_id_all(100, **{
        "screen_name": screen_name
    })

    FileRepository.save_json(get_path(), str(screen_name), time_lines)
    logger.info("{}のタイムライン情報を取得しました。".format(screen_name))
