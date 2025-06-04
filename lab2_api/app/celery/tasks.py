from app.celery.config import celery_app
from app.services.search_functions import levenstein_search, damerau_levenshtein_search
import time


@celery_app.task(bind=True)  # bind=True - внутри доступ к самому объекту задачи через self
def search_task(self, corpus_text: str, word: str, algorithm: str):
    self.update_state(state='STARTED', meta={
        'status': 'STARTED',
        'word': word,
        'algorithm': algorithm
    })

    corpus_lst = list(set(corpus_text.lower().split()))
    total = len(corpus_lst)
    all_res_dict = {}
    start_time = time.perf_counter()

    for idx, corpus_word in enumerate(corpus_lst, 1):
        time.sleep(0.15)
        if algorithm in ("levenshtein", "l"):
            dist = levenstein_search(corpus_word, word.lower())
        else:  # "damerau levenshtein", "dl"
            dist = damerau_levenshtein_search(corpus_word, word.lower())

        all_res_dict[corpus_word] = dist

        # Прогресс каждые 20%
        if idx % max(1, total // 5) == 0:
            progress = int((idx / total) * 100)
            self.update_state(state='PROGRESS', meta={
                'status': 'PROGRESS',
                'progress': progress,
                'current_word': corpus_word
            })

    execution_time = round((time.perf_counter() - start_time) * 1000, 4)
    results = [{"word": k, "distance": v} for k, v in all_res_dict.items()]
    results = sorted(results, key=lambda x: x['distance'])

    return {
        "status": "COMPLETED",
        "execution_time": execution_time,
        "results": results
    }
