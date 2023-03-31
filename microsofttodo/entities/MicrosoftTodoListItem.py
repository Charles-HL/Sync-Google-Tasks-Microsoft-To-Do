"""
Copyright (c) 2023, Charles HL. All rights reserved.
"""


class MicrosoftTodoListItem:
    def __init__(self, etag, display_name, is_owner, is_shared, wellknown_list_name, item_id):
        self.etag = etag
        self.display_name = display_name
        self.is_owner = is_owner
        self.is_shared = is_shared
        self.wellknown_list_name = wellknown_list_name
        self.item_id = item_id
