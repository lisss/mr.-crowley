from deduplicator.normalize import normalize_url
from storage import Storage


def filter_unique(storage, seen_key, urls, in_memory_seen):
    seen_in_list = set()
    unique = []
    if storage:
        normalized_urls = []
        for url in urls:
            normalized = normalize_url(url)
            if normalized not in seen_in_list:
                seen_in_list.add(normalized)
                normalized_urls.append(normalized)

        if normalized_urls:
            pipe = storage.pipeline()
            for normalized in normalized_urls:
                pipe.sismember(seen_key, normalized)
            results = pipe.execute()

            pipe = storage.pipeline()
            for i, normalized in enumerate(normalized_urls):
                if not results[i]:
                    unique.append(normalized)
                    pipe.sadd(seen_key, normalized)
            if unique:
                pipe.execute()
    else:
        for url in urls:
            normalized = normalize_url(url)
            if normalized not in in_memory_seen and normalized not in seen_in_list:
                seen_in_list.add(normalized)
                unique.append(normalized)
                in_memory_seen.add(normalized)
    return unique

