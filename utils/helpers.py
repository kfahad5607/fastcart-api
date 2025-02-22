from datetime import datetime, timezone

def get_total_pages(total_count, page_size):
    return (total_count // page_size) + (1 if total_count % page_size else 0)

def get_current_timestamp():
    return datetime.now(timezone.utc) 