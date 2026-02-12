"""Elasticsearch index mapping definitions for Athena indices."""

# Mapping for athena-notes index
# content_semantic uses semantic_text type for ELSER inference
NOTES_INDEX_MAPPING: dict = {
    "mappings": {
        "properties": {
            "title": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "content": {"type": "text"},
            "content_semantic": {"type": "semantic_text", "inference_id": "elser-endpoint"},
            "tags": {"type": "keyword"},
            "note_type": {"type": "keyword"},
            "path": {"type": "keyword"},
            "vault_relative_path": {"type": "keyword"},
            "word_count": {"type": "integer"},
            "created_at": {"type": "date"},
            "updated_at": {"type": "date"},
            "indexed_at": {"type": "date"},
            "checksum": {"type": "keyword"},
        }
    }
}

# Mapping for athena-conversations index
CONVERSATIONS_INDEX_MAPPING: dict = {
    "mappings": {
        "properties": {
            "summary": {"type": "text"},
            "summary_semantic": {"type": "semantic_text", "inference_id": "elser-endpoint"},
            "topics": {"type": "keyword"},
            "extracted_tasks": {"type": "text"},
            "task_ids_created": {"type": "keyword"},
            "timestamp": {"type": "date"},
        }
    }
}
