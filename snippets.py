import psycopg2
import logging
import argparse

logging.debug("Connecting to PostgreSQL")
connection = psycopg2.connect(database="snippets")
logging.debug("Database connection established.")

# Set the log output file, and the log level
logging.basicConfig(filename="snippets.log", level=logging.DEBUG)

def search(string):
    """
    Searches and displays all records containing given string
    """
    logging.info("Searching for keywords containing {!r}".format(string))
    with connection, connection.cursor() as cursor:
        command = "select * from snippets where keyword like '%{}%' and not hidden".format(string)
        cursor.execute(command)
        row = cursor.fetchall()
    logging.debug("All keywords containing string retrieved successfully")
    if not row:
        return string, "No records returned"
    else:
        return string, row

def catalog():
    """
    Lists all records
    """
    logging.info("Displaying catalog")
    with connection, connection.cursor() as cursor:
        command = "select keyword from snippets where not hidden order by keyword"
        cursor.execute(command)
        row = cursor.fetchall()
    logging.debug("All records retrieved successfully")
    if not row:
        return "No records exist"
    else:
        return row

def put(name, snippet, hidden):
    """
    Store a snippet with an associated name.
    
    Returns the name and the snippet
    """
    logging.info("Storing snippet {!r}: {!r}".format(name, snippet))
    with connection, connection.cursor() as cursor:
        try:
            command = "insert into snippets values (%s, %s, %s)"
            cursor.execute(command, (name, snippet))
        except psycopg2.IntegrityError as e:
            connection.rollback()
            command = "update snippets set message=%s where keyword=%s"
            cursor.execute(command, (snippet, name))
    logging.debug("Snippet stored successfully.")
    return name, snippet, hidden
    
def get(name):
    """Retrieve the snippet with a given name.
    If there is no such snippet, return '404: Snippet Not Found'.
    Returns the snippet.
    """
    logging.info("Retrieving snippet {!r}".format(name))
    with connection, connection.cursor() as cursor:
        command = "select message from snippets where keyword = (%s)"
        cursor.execute(command, (name,))
        row = cursor.fetchone()
    logging.debug("Snippet retrieved successfully.")
    if not row:
        return "404: Snippet Not Found"
    else:
        return row[0]
        
        #look up definition of fetchone
        
    
def delete(name):
    """deletes the snippet with a given name.
    
    If there is no such snippet, return '404: Snippet Not Found'.
    
    Returns the snippet.
    """
    logging.info("Deleting snippet {!r}".format(name))
    cursor = connection.cursor()
    command = "delete from snippets where keyword = (%s)"
    cursor.execute("select message from snippets where keyword = (%s)", (name,))
    row = cursor.fetchone()
    cursor.execute(command, (name,))
    connection.commit()
    logging.debug("Snippet deleted successfully.")
    if not row:
        return "404 Snippet not Found."
    else:
        return name
    
def patch(name, snippet):
    """
    Updates the snippet with the associated name.
    
    Returns the name and the snippet
    """
    logging.info("updating snippet {!r} to {!r}".format(name, snippet))
    cursor = connection.cursor()
    command = "update snippets set message = (%s) where keyword = (%s)"
    cursor.execute(command, (snippet, name))
    connection.commit()
    logging.debug("Snippet updated successfully")
    return name, snippet
    
def main():
    """Main function"""
    logging.info("Constructing parser")
    parser = argparse.ArgumentParser(description="Store and retrieve snippets of text")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    #Subparser for the search command
    logging.debug("Constructing string subparser")
    search_parser = subparsers.add_parser("search", help="Search a string in a keyword")
    search_parser.add_argument("string", help="String to search for")
    
    #Subparser for the catalog command
    logging.debug("Constructing catalog subparser")
    _ = subparsers.add_parser("catalog", help="List all records")
    
    #Subparser for the put command
    logging.debug("Constructing put subparser")
    put_parser = subparsers.add_parser("put", help="Store a snippet")
    put_parser.add_argument("name", help="Name of the snippet")
    put_parser.add_argument("snippet", help="Snippet text")
 ###   put_parser.add_argument("-h", type=bool, help="Hides the snippet from catalog and search", action="store_true")

    #subparser for the get command
    logging.debug("Constructing get subparser")
    get_parser = subparsers.add_parser("get", help="Retrieve a snippet")
    get_parser.add_argument("name", help="content of the name")
    
    #subparser for the delete command
    logging.debug("Constructing delete subparser")
    delete_parser = subparsers.add_parser("delete", help="Delete a snippet")
    delete_parser.add_argument("name", help="content of the name")
    
    #Subparser for the patch command
    logging.debug("Constructing patch subparser")
    patch_parser = subparsers.add_parser("patch", help="Update a snippet")
    patch_parser.add_argument("name", help="Name of the snippet")
    patch_parser.add_argument("snippet", help="Snippet text")
    
    arguments = parser.parse_args()
    #convert parsed arguments from Namespace to a dictionary
    arguments = vars(arguments)
    command = arguments.pop("command")
    
    if command == "put":
        name, snippet, hidden = put(**arguments)
    ###    if arguments.h == 1:
    ###        put.hidden = 't'
        else:
            put.hidden = 'f'
        print("Stored {!r} as {!r}".format(snippet, name))
    elif command == "get":
        snippet = get(**arguments)
        print("Retrieved snippet: {!r}".format(snippet))
    elif command == "patch":
        name, snippet = patch(**arguments)
        print("Updated snippet {!r} to {!r}".format(name, snippet))
    elif command == "delete":
        name = delete(**arguments)
        print("Deleted snippet {!r}".format(name))
    elif command == "catalog":
        row = catalog(**arguments)
        for r in row:
            print(r[0])
    elif command == "search":
        string, row = search(**arguments)
        print("Displaying snippets with keyword containing {!r}:".format(string))
        for r in row:
            print(r)
    
if __name__ == "__main__":
    main()
    