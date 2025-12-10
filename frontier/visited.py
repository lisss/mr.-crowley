from deduplicator.deduplicator import Deduplicator
from storage import Storage


def is_visited(storage, deduplicator, url, visited_key, in_memory_visited):
    normalized = deduplicator.normalize(url)
    if storage:
        return storage.is_in_set(visited_key, normalized)
    return normalized in in_memory_visited


def mark_visited(storage, deduplicator, url, visited_key, in_memory_visited):
    normalized = deduplicator.normalize(url)
    if storage:
        storage.add_to_set(visited_key, normalized)
    else:
        in_memory_visited.add(normalized)
    deduplicator.mark_seen(normalized)
    return normalized


def get_visited_count(storage, visited_key, in_memory_visited):
    if storage:
        return storage.get_set_size(visited_key)
    return len(in_memory_visited)

