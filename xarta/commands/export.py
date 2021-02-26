"""The export command."""


from arxivcheck.arxiv import check_arxiv_published

from .base import BaseCommand
from ..database import PaperDatabase
from ..utils import XartaError, process_and_validate_ref


class Export(BaseCommand):
    """
    Export the database.
    Currently only exporting to a bibtex file is supported.
    <export-path> should be a path to a directory.
    """

    def run(self):
        options = self.options
        bibtex_file = options["<bibtex-file>"]
        ref = options["--ref"]
        tag = options["<tag>"]
        filter_ = options["--filter"]
        author = options["--author"]
        category = options["--category"]
        title = options["--title"]

        with PaperDatabase(self.database_path) as paper_database:
            if (ref or filter_ or author or category or title) is None and (
                tag is None or tag == []
            ):
                # no search criteria, export all papers
                papers = paper_database.get_all_papers()
            else:

                processed_ref = process_and_validate_ref(ref, paper_database)
                papers = paper_database.query_papers(
                    paper_id=processed_ref,
                    title=title,
                    author=author,
                    category=category,
                    tags=tag,
                    filter_=filter_,
                    silent=True,
                )

            paper_refs = [paper_data[0] for paper_data in papers]

            with open(bibtex_file, "w+") as f:

                if options["arxiv"]:
                    # print bibtex info from arxiv

                    for ref in paper_refs:
                        bib_info = check_arxiv_published(ref)
                        if bib_info[0]:
                            print("Writing bibtex entry for " + ref)
                            f.write(bib_info[2] + "\n\n")

                elif options["inspire"]:
                    # print data from inspire

                    import requests

                    for ref in paper_refs:

                        # request data from inspire
                        url = (
                            "https://inspirehep.net/api/arxiv/" + ref + "?format=bibtex"
                        )
                        response = requests.get(url)

                        # raise error if HTTPS error was returned
                        response.raise_for_status()

                        print("Writing bibtex entry for " + ref)
                        f.write(response.text + "\n")

                print(bibtex_file + " successfully written!")
