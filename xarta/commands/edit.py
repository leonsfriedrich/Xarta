"""The tag editing command."""


from .base import BaseCommand
from ..database import PaperDatabase
from ..utils import process_and_validate_ref


class Edit(BaseCommand):
    """ Edit the tag information in the database for a paper. """

    def run(self):
        options = self.options
        ref = options["<ref>"]
        tags = options["<tag>"]
        action = options["--action"]

        with PaperDatabase() as paper_database:
            processed_ref = process_and_validate_ref(ref, paper_database)
            paper_database.edit_paper_tags(
                paper_id=processed_ref, tags=tags, action=action
            )
