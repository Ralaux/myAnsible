import paramiko
import os
import jinja2

def todo_handler(logging, SSH_client, todo, host_IP):
    if todo["module"] == "copy":
        copy_module(logging, 
                   SSH_client, 
                   todo["params"]["src"], 
                   todo["params"]["dest"], 
                   host_IP, 
                   todo["params"].get("backup"))
    if todo["module"] == "command":
        command_module(logging, 
                      SSH_client, 
                      todo["params"]["command"], 
                      host_IP)
    if todo["module"] == "template":
        template_module(logging, 
                       SSH_client, 
                       todo["params"], 
                       host_IP)
    if todo["module"] == "service":
        service_module(logging, 
                      SSH_client, 
                      todo["params"], 
                      host_IP)
    if todo["module"] == "sysctl":
        sysctl_module(logging,
                     SSH_client, 
                     todo["params"]["attribute"], 
                     todo["params"]["value"], 
                     todo["params"]["permanent"], 
                     host_IP)
    if todo["module"] == "apt":
        apt_module(logging, 
                  SSH_client, 
                  todo["params"]["name"], 
                  todo["params"]["state"], 
                  host_IP)
    else:
        logging.info(f"{host_IP}: Method {todo['module']} is unknown")
        

'''
    Copy a file or a folder from the computer to the host
'''          
def copy_module(logging, SSH_client, src, dest, host_IP, backup = False):
    FTPClient=SSH_client.open_sftp()
    if backup:
        command_module(logging, 
                       SSH_client, 
                       "mv "+dest+"/"+src.split('/')[-1] + " " + dest+"/"+src.split('/')[-1] + ".bkp", 
                       host_IP )
    if os.path.isfile(src):
        FTPClient.put(src, dest+"/"+src.split('/')[-1])
    elif os.path.isdir(src): 
        command_module(logging, 
                       SSH_client, 
                       "mkdir "+dest+"/"+src.split('/')[-1], 
                       host_IP)
        dest = dest+"/"+src.split('/')[-1]
        copy_repo(logging, 
                  FTPClient, 
                  SSH_client, 
                  src, 
                  dest, 
                  host_IP)
    FTPClient.close()
    logging.info(f"{host_IP}: {src} has been copied at {dest} successfully")

def copy_file(logging, FTP_client, src, dest, host_IP):
    try:
        FTP_client.put(src, dest)
    except paramiko.AuthenticationException:
        logging.error(f"{host_IP}: Échec de l'authentification. Vérifiez vos informations de connexion.")
    except paramiko.SSHException as ssh_err:
        logging.error(f"{host_IP}: Erreur SSH : ", ssh_err)

def copy_repo(logging, FTP_client, SSH_client, src, dest, host_IP):
    for item in os.listdir(src):
        if os.path.isfile(src+'/'+item):
            copy_file(logging, 
                      FTP_client, 
                      src+"/"+item, 
                      dest + '/' + item, 
                      host_IP)
        if os.path.isdir(src+'/'+item):
            command_module(logging, 
                           SSH_client, 
                           "mkdir -p "+dest+"/"+item, 
                           host_IP)
            copy_repo(logging, 
                      FTP_client, 
                      SSH_client, 
                      src+"/"+item, 
                      dest+"/"+item, 
                      host_IP)

'''
    Execute a command given in parameter
'''
def command_module(logging, SSH_client, command, host_IP):
    try:
        stdin, stdout, stderr = SSH_client.exec_command(command)
        logging.info(f"{host_IP}: {command} executed")
        logging.info(host_IP + ": "+ stdout.read().decode())
        
    except paramiko.SSHException as ssh_err:
        logging.error(f"{host_IP}: Erreur SSH : ", ssh_err)
    
'''
    Update a file from a template and a set of variables
'''
def template_module(logging, SSH_client, params, host_IP):
    template_content = open(params["src"]).read()
    template = jinja2.Template(template_content)
    rendered_template = template.render(params["vars"])
    remote_file_path = params["dest"]
    command = f'echo "{rendered_template}" > {remote_file_path}'
    command_module(logging, 
                   SSH_client, 
                   command, 
                   host_IP)
    logging.info(f"{host_IP}: Template done with {params['src']} in {params['dest']}")
    
'''
    Update a file from a template and a set of variables
'''
def service_module(logging, SSH_client, params, host_IP):
    if params["state"] == "started":
        command = f"systemctl start {params['name']}"
        command_module(logging, 
                       SSH_client, 
                       command, 
                       host_IP)
        logging.info(f"{host_IP}: system {params['name']} has been started")
    if params["state"] == "stopped":
        command = f"/usr/bin/systemctl stop {params['name']}"
        command_module(logging, 
                       SSH_client, 
                       command, 
                       host_IP)
        logging.info(f"{host_IP}: system {params['name']} has been stopped")
    if params["state"] == "restarted":
        command = f"systemctl restart {params['name']}"
        command_module(logging, 
                       SSH_client, 
                       command, 
                       host_IP)
        logging.info(f"{host_IP}: system {params['name']} has been restarted")
    if params["state"] == "enabled":
        command = f"systemctl enable {params['name']}"
        command_module(logging, 
                       SSH_client, 
                       command,
                       host_IP)
        logging.info(f"{host_IP}: system {params['name']} has been enabled")
    if params["state"] == "disabled":
        command = f"systemctl disable {params['name']}"
        command_module(logging, 
                       SSH_client, 
                       command, 
                       host_IP)
        logging.info(f"{host_IP}: system {params['name']} has been disabled")

'''
    sysctl module modificate kernel params
'''
def sysctl_module(logging, SSH_client, attribute, value, permanent, host_IP):
    if permanent == True :
        command = f"sysctl -w {attribute}={value} && sysctl -p"
        logging.info(f"{host_IP}: the modification is permanent")
    else :
        command = f"sysctl -w {attribute}={value}"
        logging.info(f"{host_IP}: the modification is not permanent")
    command_module(logging, 
                   SSH_client, 
                   command, 
                   host_IP)
    logging.info(f"{host_IP}: sysctl {attribute} has now {value} as a value.")
    
'''
    Install or uninstall a package
'''    
def apt_module(logging, SSH_client, name, state, host_IP):
    if state == "absent":
        logging.info(f"{host_IP}: Uninstalling the package {name}")
        command = f"apt remove -y {name}"
        command_module(logging, 
                       SSH_client, 
                       command, 
                       host_IP)
    else:
        logging.info(f"{host_IP}: Installing the package {name}")
        command = f"apt install -y {name}"
        command_module(logging, 
                       SSH_client, 
                       command, 
                       host_IP)