import argparse
import yaml

def argParsing(logging):
    # parsing of the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', dest='todoFile', action='append')
    parser.add_argument('-i', dest='inventFile', action='append')
    files = parser.parse_args()

    # List of todos and inventory file names
    todo = files.todoFile[0]
    inventory = files.inventFile[0]
        
    logging.info(f"todo file: {todo}")
    logging.info(f"inventory file: {inventory}")


    # Dicts of the content of the todo and inventory files
    todoArgs = yaml.load(open(todo), Loader=yaml.FullLoader)
    inventoryArgs = yaml.load(open(inventory), Loader=yaml.FullLoader)
    
    return todoArgs, inventoryArgs

