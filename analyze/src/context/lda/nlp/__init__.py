import time
import os
import sys
from pathlib import Path
from functools import partial
import shutil
import json

from joblib import Parallel, delayed
from spacy.util import minibatch
import pandas as pd

from common import get_logger
from context.nlp import nlp

logger = get_logger(__name__)


def process_nlp(batch_id, texts, output_dir, size):
    start_time = time.perf_counter()
    out_path = Path(output_dir) / ("%d.json" % batch_id)
    if out_path.exists():
        return None

    logger.info("Processing batch {}".format(batch_id))
    with out_path.open("w", encoding="utf8") as f:
        for doc in nlp().pipe(texts):
            words = [{
                "raw_text": doc.text,
                "text": token.text,
                "lemma": token.lemma_,
                "pos": token.pos_,
                "tag": token.tag_,
                "dep": token.dep_,
                "shape": token.shape_,
                "is_alpha": token.is_alpha,
                "is_stop": token.is_stop
            } for token in doc]
            f.write(json.dumps(words, ensure_ascii=False))
            f.write("\n")

    logger.info("Saved {} texts to {}.txt = ファイル総数:{} 単一の処理時間: {}".format(len(texts), batch_id, size, time.perf_counter() - start_time))


def run(path, output_dir, n_jobs: int = 4, batch_size: int = 1000):
    """ 自然言語解析"""
    logger.info("====自然言語解析を行います。====")
    logger.info("辞書の作成を行います。")
    n_jobs = int(n_jobs)
    batch_size = int(batch_size)

    if not Path(path).exists():
        logger.error("指定のパスが見つかりませんでした。 {}".format(path))
        sys.exit(1)

    df = pd.read_csv(open(path, 'rU'), encoding="utf-8", engine="c")
    df = df.dropna(how='all')
    docs = df['text'].tolist()

    partitions = minibatch(docs, size=batch_size)
    executor = Parallel(n_jobs=n_jobs, verbose=10, backend="multiprocessing", prefer="processes")
    do = delayed(partial(process_nlp, size=len(docs)/batch_size))
    tasks = (do(i, batch, output_dir(prefix="nlp")()) for i, batch in enumerate(partitions))
    executor(tasks)

    logger.info("====自然言語解析が完了しました。。====")
