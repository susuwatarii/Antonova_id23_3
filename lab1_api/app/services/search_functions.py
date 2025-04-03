import time


def search(corpus_text, word, algorithm):
    """
    Выбор типа поиска, запуск поиска и замер времени
    (подсчет операций удаления, вставки и замены)

    Args:
        corpus_text (String): текст для поиска в нем
        word (String): слово для поиска
        algorithm (String): тип алгоритма поиска

    Returns:
        float: время поиска
        list: список слов и расстояний до них [{"word": "some_word", "distance": 2}, ...]
    """
    corpus_lst = corpus_text.split(" ")
    corpus_lst = list(set(corpus_lst))
    all_res_dict = {}
    start_time = time.perf_counter()
    if algorithm in ("levenshtein", "l"):
        for corpus_word in corpus_lst:
            dist = levenstein_search(corpus_word, word)
            all_res_dict[corpus_word] = dist
    else:  # "damerau levenshtein", "dl"
        for corpus_word in corpus_lst:
            dist = damerau_levenshtein_search(corpus_word, word)
            all_res_dict[corpus_word] = dist

    res_lst = [{"word": key, "distance": value} for key, value in all_res_dict.items()]
    return round((time.perf_counter() - start_time) * 1000, 4), res_lst


def damerau_levenshtein_search(corpus_word, word):
    """
    Расстояние Дамерау-Левенштейна между двумя словами
    (подсчет операций удаления, вставки, замены и перестановки символов)

    Args:
        corpus_word (String): слово
        word (String): слово

    Returns:
        int: Расстояние между словами
    """
    func_dict = {}
    len1 = len(corpus_word)
    len2 = len(word)
    for i in range(-1, len1 + 1):
        func_dict[(i, -1)] = i + 1
    for j in range(-1, len2 + 1):
        func_dict[(-1, j)] = j + 1

    for i in range(len1):
        for j in range(len2):
            if corpus_word[i] == word[j]:
                cost = 0
            else:
                cost = 1
            func_dict[(i, j)] = min(
                func_dict[(i - 1, j)] + 1,  # deletion
                func_dict[(i, j - 1)] + 1,  # insertion
                func_dict[(i - 1, j - 1)] + cost,  # substitution
            )
            if i and j and corpus_word[i] == word[j - 1] and corpus_word[i - 1] == word[j]:
                # Если текущий и предыдущий символы в словах поменяны местами (i-2, j-2) + 1
                func_dict[(i, j)] = min(func_dict[(i, j)], func_dict[i - 2, j - 2] + 1)  # transposition

    return func_dict[len1 - 1, len2 - 1]


def levenstein_search(corpus_word, word):
    """
    Расстояние Левенштейна между двумя словами

    Args:
        corpus_word (String): слово
        word (String): слово

    Returns:
        int: Расстояние между словами
    """
    len1, len2 = len(corpus_word), len(word)
    if len1 > len2:  # В целях минимизации используемой памяти располагаем слова так, чтобы длины строк были минимальны
        corpus_word, word = word, corpus_word
        len1, len2 = len2, len1

    curr_row = range(len1 + 1)
    for i in range(1, len2 + 1):  # хранить всю матрицу в памяти не имеет смысла, достаточно текущей и предыдущей строк
        prev_row, curr_row = curr_row, [i] + [0] * len1  # [i, 0 , 0, ...]
        for j in range(1, len1 + 1):
            add, delete, change = prev_row[j] + 1, curr_row[j - 1] + 1, prev_row[j - 1]
            if corpus_word[j - 1] != word[i - 1]:
                change += 1
            curr_row[j] = min(add, delete, change)

    return curr_row[len1]
