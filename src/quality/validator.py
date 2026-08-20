"""
IceStream - Validator
Simple entry point wrapping the rules engine for use by the stream processor.
"""
from .rules import validate_record

class Validator:
    def __init__(self):
        self.seen_transaction_ids = set()

    def check(self, record):
        return validate_record(record, seen_transaction_ids=self.seen_transaction_ids)