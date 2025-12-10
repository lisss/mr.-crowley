from collections import deque
from deduplicator.deduplicator import Deduplicator
from storage import Storage


def init_queue(storage, deduplicator, normalized_start, max_level):
    if storage:
        queue_length = storage.get_list_length("crawley:queue")
        if queue_length == 0:
            if not storage.is_in_set("crawley:queued", normalized_start):
                storage.add_to_list("crawley:queue", normalized_start)
                storage.add_to_set("crawley:queued", normalized_start)
                storage.client.hset("crawley:level", normalized_start, 0)
        return None, None, None, None
    else:
        return deque([(normalized_start, 0)]), {normalized_start}, set(), {normalized_start: 0}


def has_next(storage, in_memory_to_visit):
    if storage:
        return storage.get_list_length("crawley:queue") > 0
    return len(in_memory_to_visit) > 0


def get_next(storage, in_memory_to_visit, in_memory_queued, max_level):
    if storage:
        url = storage.pop_from_list("crawley:queue")
        if url:
            storage.remove_from_set("crawley:queued", url)
            level_str = storage.client.hget("crawley:level", url)
            if level_str:
                level = int(level_str.decode() if isinstance(level_str, bytes) else level_str)
            else:
                level = max_level + 1 if max_level is not None else 0
            return url, level
        return None, None
    url, level = in_memory_to_visit.popleft()
    in_memory_queued.discard(url)
    return url, level


def add_urls(storage, deduplicator, urls, current_level, max_level, visited_key, queued_key, queue_key, level_key, in_memory_to_visit, in_memory_queued, in_memory_visited):
    if max_level is not None and current_level >= max_level:
        return []

    unique_urls = deduplicator.filter_unique(urls)
    added = []
    next_level = current_level + 1

    if max_level is not None and next_level > max_level:
        return []

    if storage:
        if not unique_urls:
            return added

        pipe = storage.pipeline()
        for url in unique_urls:
            pipe.sismember(visited_key, url)
            pipe.sismember(queued_key, url)
        results = pipe.execute()

        to_add = []
        pipe = storage.pipeline()
        for i, url in enumerate(unique_urls):
            visited = results[i * 2]
            queued = results[i * 2 + 1]
            if not visited and not queued:
                to_add.append(url)
                pipe.rpush(queue_key, url)
                pipe.sadd(queued_key, url)
                pipe.hset(level_key, url, next_level)

        if to_add:
            pipe.execute()
            added = to_add
            for url in to_add:
                if len(storage._queued_cache) < storage._cache_size_limit:
                    storage._queued_cache.add(url)
    else:
        for url in unique_urls:
            normalized = deduplicator.normalize(url)
            if normalized not in in_memory_visited and url not in in_memory_queued:
                in_memory_to_visit.append((url, next_level))
                in_memory_queued.add(url)
                added.append(url)
    return added

