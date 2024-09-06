import argparse
import yaml

def arg_parsing(logging):
    # parsing of the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', 
                        dest='todoFile', 
                        action='append')
    parser.add_argument('-i', 
                        dest='inventFile', 
                        action='append')
    parser.add_argument('--debug', 
                        dest='Debug Mode', 
                        action = "store_true")
    files = parser.parse_args()

    # List of todos and inventory file names
    todo = files.todoFile[0]
    inventory = files.inventFile[0]
    
    # Dicts of the content of the todo and inventory files
    todo_args = yaml.load(open(todo), Loader=yaml.FullLoader)
    inventory_args = yaml.load(open(inventory), Loader=yaml.FullLoader)
    
    logging.info(f"todo file: {todo}")
    logging.info(f"{len(todo_args)} todos to be done : \n{todo_args}")
    logging.info(f"inventory file: {inventory}")
    
    IP_list = []
    for key, items in inventory_args.items():
        for key, item in items.items():
            IP_list.append(item["ssh_address"])
    logging.info(f"{len(IP_list)} hosts to be configured : \n{IP_list}")
    
    return todo_args, inventory_args

