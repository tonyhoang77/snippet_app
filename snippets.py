import psycopg2
import logging
import argparse

logging.debug("Connecting to PostgreSQL")
connection = psycopg2.connect(database="snippets")
logging.debug("Database connection established.")

# Set the log output file, and the log level
logging.basicConfig(filename="snippets.log", level=logging.DEBUG)

def put(name, snippet):
    """
    Store a snippet with an associated name.
    
    Returns the name and the snippet
    """
    logging.info("Storing snippet {!r}: {!r}".format(name, snippet))
    cursor = connection.cursor()
    command = "insert into snippets values (%s, %s)"
    cursor.execute(command, (name, snippet))
    connection.commit()
    logging.debug("Snippet stored successfully.")
    return name, snippet
    
def get(name):
    """Retrieve the snippet with a given name.
    If there is no such snippet, return '404: Snippet Not Found'.
    Returns the snippet.
    """
    logging.info("Retrieving snippet {!r}".format(name))
    cursor = connection.cursor()
    command = "select message from snippets where keyword = (%s)"
    cursor.execute(command, (name,))
    row = cursor.fetchone()
    logging.debug("Snippet retrieved successfully.")
    if not row:
        return None
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
    row = cursor.fetchone()
    cursor.execute(command, (name,))
    logging.debug("Snippet deleted successfully.")
    if not row:
        return None
    else:
        return row[0]
    
def patch(name, snippet):
    """
    Updates the snippet with the associated name.
    
    Returns the name and the snippet
    """
    logging.info("updating snippet {!r} from {!r} to {!r}".format(name, snippet.snippet, snippet))
    cursor = connection.cursor()
    command = "update snippets set message = (%s) where keyword = (%s)"
    cursor.execute(command, (snippet, name))
    row = cursor.fetchone()
    logging.debug("Snippet updated successfully")
    if not row:
        return None
    else:
        return row[0]
    
def main():
    """Main function"""
    logging.info("Constructing parser")
    parser = argparse.ArgumentParser(description="Store and retrieve snippets of text")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    #Subparser for the put command
    logging.debug("Constructing put subparser")
    put_parser = subparsers.add_parser("put", help="Store a snippet")
    put_parser.add_argument("name", help="Name of the snippet")
    put_parser.add_argument("snippet", help="Snippet text")
    
    #subparser for the get command
    logging.debug("Constructing get subparser")
    get_parser = subparsers.add_parser("get", help="Retrieve a snippet")
    get_parser.add_argument("name", help="content of the name")
    
    arguments = parser.parse_args()
    #convert parsed arguments from Namespace to a dictionary
    arguments = vars(arguments)
    command = arguments.pop("command")
    
    if command == "put":
        name, snippet = put(**arguments)
        print("Stored {!r} as {!r}".format(snippet, name))
    elif command == "get":
        snippet = get(**arguments)
        print("Retrieved snippet: {!r}".format(snippet))
    
if __name__ == "__main__":
    main()
    
    
    #write note to c9, pip search has psycopg2, but cant