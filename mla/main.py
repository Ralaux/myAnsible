import logging
import datetime
import my_parser
import SSH_handler
import todo_handler
import sys

def main():
    if "--debug" in sys.argv:
        log_level = logging.DEBUG
    else :
        log_level = logging.INFO
    log_filename = datetime.datetime.now().strftime("logs/nux4_logfile_%Y-%m-%d_%Hh%Mm%Ss.log")
    logging.basicConfig(filename=log_filename, 
                        filemode='w', 
                        level=log_level, 
                        format='%(asctime)s %(levelname)s: %(message)s')

    todo_args, inventory_args = my_parser.arg_parsing(logging)

    for host, infos in inventory_args["hosts"].items():
        logging.info(f"Connecting to the host {host}.")
        SSH_client = SSH_handler.start_connection(logging, infos)
        for todo in todo_args:
            logging.info(f"{infos['ssh_address']}: Performing {todo} on host {host}.")
            todo_handler.todo_handler(logging, 
                                    SSH_client, 
                                    todo, 
                                    infos["ssh_address"])
        SSH_handler.stop_connection(SSH_client)

if __name__ == '__main__':
    main()
