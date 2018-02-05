import sqlite3
import os
from .utils import get_arxiv_data, list_to_string, expand_tag

HOME = os.path.expanduser('~')

class PaperDatabase():
    def __init__(self, path):
        self.path = path

    def create_connection(self):
        """ Create a database connection to a SQLite database. """
        print('Creating new database at ' + self.path + '...')
        conn = sqlite3.connect(self.path)
        conn.close()
        with open(HOME+'/.xarta', 'w') as xarta_file:
            xarta_file.write(self.path)

    def initialise_database(self):
        """ Initialise database with empty table. """
        conn = sqlite3.connect(self.path)
        c = conn.cursor()
        print('Initialising database...')
        c.execute('''CREATE TABLE papers (id text, title text, authors text, category text, tags text);''')
        # c.execute('''CREATE TABLE tags (abbrev text, full text);''') # TODO fix this up...
        conn.commit()
        conn.close()
        print('Database initialised!')

    # TODO add check to see if paper already in database
    def add_paper(self, paper_id, tags):
        """ Add paper to database. """
        conn = sqlite3.connect(self.path)
        c = conn.cursor()
        data = get_arxiv_data(paper_id)
        author_string = list_to_string(data['authors'])
        tags = [expand_tag(tag, data) for tag in tags]
        tags = list_to_string(tags)

        insert_command = f'''INSERT INTO papers (id, title, authors, category, tags) VALUES ("{paper_id}", "{data['title']}", "{author_string}", "{data['category']}", "{tags}");'''
        c.execute(insert_command)
        print(f"{paper_id} added to database!")
        conn.commit()
        conn.close()

    def delete_paper(self, paper_id):
        """ Remove paper from database. """

        conn = sqlite3.connect(self.path)
        c = conn.cursor()
        data = get_arxiv_data(paper_id)
        delete_command = f'''DELETE FROM papers WHERE id = "{paper_id}";'''
        c.execute(delete_command)
        print(f"{paper_id} deleted from database!")
        conn.commit()
        conn.close()

    # def query_papers(self, paper_id, author, tag, title):
    def query_papers(self, silent=False):
        """ Query information about a paper in the databse. """
        conn = sqlite3.connect(self.path)
        c = conn.cursor()
        query_command = f'''SELECT * FROM papers;'''
        query_results = c.execute(query_command)
        all_rows = c.fetchall()
        to_be_printed = [[(c if len(c) < 40 else c[:37] + "...")
                          for c in row]
                         for row in all_rows]
        if not silent:
            from tabulate import tabulate
            # TODO make this code look prettier
            really_to_be_printed = [['arXiv:'+row[0], row[1], row[2], row[3], row[4]]
                                    for row in to_be_printed]
            print(
                tabulate(really_to_be_printed,
                         headers=['Ref', 'Title', 'Authors', 'Category', 'Tags'],
                         tablefmt="simple"))
        conn.close()
        return all_rows

    def query_papers_contains(self, paper_id, title, author, category, tag, silent=False):
        library_data = self.query_papers(silent=True)
        to_be_printed = []
        for row in library_data:
            if paper_id is not None and paper_id in row[0]:
                to_be_printed.append(row)
                continue
            elif title is not None and title in row[1]:
                to_be_printed.append(row)
                continue
            elif author is not None and author in row[2]:
                to_be_printed.append(row)
                continue
            elif category is not None and category in row[3]:
                to_be_printed.append(row)
                continue
            # TODO This will only work for one tag now... FIX
            elif tag != [] and tag[0] in row[4]: # TODO will need to write out entire string
                to_be_printed.append(row)
                continue

        if not silent:
            from tabulate import tabulate
            r_to_be_printed = [[(c if len(c) < 40 else c[:37] + "...")
                                for c in row]
                               for row in to_be_printed]
            rr_to_be_printed = [['arXiv:'+row[0], row[1], row[2], row[3], row[4]]
                                for row in r_to_be_printed]
            print(
                tabulate(rr_to_be_printed,
                         headers=['Ref', 'Title', 'Authors', 'Category', 'Tags'],
                         tablefmt="simple"))
        return to_be_printed
