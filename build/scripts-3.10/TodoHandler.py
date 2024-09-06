import paramiko
import os
import jinja2

def TodoHandler(logging, SSHClient, todo):
    if todo["module"] == "copy":
        CopyModule(logging, SSHClient, todo["params"]["src"], todo["params"]["dest"], todo["params"].get("backup"))
    if todo["module"] == "command":
        CommandModule(logging, SSHClient, todo["params"]["command"])
    if todo["module"] == "template":
        TemplateModule(logging, SSHClient, todo["params"])
    if todo["module"] == "service":
        ServiceModule(logging, SSHClient, todo["params"])
    if todo["module"] == "sysctl":
        SysctlModule(logging,SSHClient, todo["params"]["attribute"], todo["params"]["value"], todo["params"]["permanent"])
    else:
        logging.info(f"Method {todo['module']} is unknown")
        

'''
    Copy a file or a folder from the computer to the host
'''          
def CopyModule(logging, SSHClient, src, dest, backup = False):
    FTPClient=SSHClient.open_sftp()
    if backup:
        CommandModule(logging, SSHClient, "mv "+dest+"/"+src.split('/')[-1] + " " + dest+"/"+src.split('/')[-1] + ".bkp" )
    if os.path.isfile(src):
        FTPClient.put(src, dest+"/"+src.split('/')[-1])
    elif os.path.isdir(src): 
        CommandModule(logging, SSHClient, "mkdir "+dest+"/"+src.split('/')[-1])
        dest = dest+"/"+src.split('/')[-1]
        CopyRepo(logging, FTPClient, SSHClient, src, dest,)
    FTPClient.close()
    logging.info(f"{src} has been copied at {dest} successfully")

def CopyFile(logging, FTPClient, src, dest):
    try:
        FTPClient.put(src, dest)
    except paramiko.AuthenticationException:
        logging.error("Échec de l'authentification. Vérifiez vos informations de connexion.")
    except paramiko.SSHException as ssh_err:
        logging.error("Erreur SSH : ", ssh_err)

def CopyRepo(logging, FTPClient, SSHClient, src, dest):
    for item in os.listdir(src):
        if os.path.isfile(src+'/'+item):
            CopyFile(logging, FTPClient, src+"/"+item, dest + '/' + item)
        if os.path.isdir(src+'/'+item):
            CommandModule(logging, SSHClient, "mkdir -p "+dest+"/"+item)
            CopyRepo(logging, FTPClient, SSHClient, src+"/"+item, dest+"/"+item)

'''
    Execute a command given in parameter
'''
def CommandModule(logging, SSHClient, command):
    try:
        stdin, stdout, stderr = SSHClient.exec_command(command)
        logging.info(f"{command} executed")
        logging.info(stdout.read().decode())
        
    except paramiko.SSHException as ssh_err:
        logging.error("Erreur SSH : ", ssh_err)
    except :
        logging.error(stderr.read().decode())
    
'''
    Update a file from a template and a set of variables
'''
def TemplateModule(logging, SSHClient, params):
    template_content = open(params["src"]).read()
    template = jinja2.Template(template_content)
    rendered_template = template.render(params["vars"])
    remote_file_path = params["dest"]
    command = f'echo "{rendered_template}" > {remote_file_path}'
    CommandModule(logging, SSHClient, command)
    logging.info(f"Template done with {params['src']} in {params['dest']}")
    
'''
    Update a file from a template and a set of variables
'''
def ServiceModule(logging, SSHClient, params):
    if params["state"] == "started":
        command = f"systemctl start {params['name']}"
        CommandModule(logging, SSHClient, command)
        logging.info(f"system {params['name']} has been started")
    if params["state"] == "stopped":
        command = f"/usr/bin/systemctl stop {params['name']}"
        CommandModule(logging, SSHClient, command)
        logging.info(f"system {params['name']} has been stopped")
    if params["state"] == "restarted":
        command = f"systemctl restart {params['name']}"
        CommandModule(logging, SSHClient, command)
        logging.info(f"system {params['name']} has been restarted")
    if params["state"] == "enabled":
        command = f"systemctl enable {params['name']}"
        CommandModule(logging, SSHClient, command)
        logging.info(f"system {params['name']} has been enabled")
    if params["state"] == "disabled":
        command = f"systemctl disable {params['name']}"
        CommandModule(logging, SSHClient, command)
        logging.info(f"system {params['name']} has been disabled")

'''
    sysctl module modificate kernel params
'''

def SysctlModule(logging,SSHClient, attribute, value, permanent):
    if permanent == True :
        command = f"sysctl -w {attribute}={value} && sysctl -p"
        logging.info("the modification is permanent")
    else :
        command = f"sysctl -w {attribute}={value}"
        logging.info("the modification is not permanent")
    CommandModule(logging, SSHClient, command)
    logging.info(f"sysctl {attribute} has now {value} as a value.")