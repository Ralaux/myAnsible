import paramiko

def start_connection(logging, host_infos):
    # Informations de connexion
    ip = host_infos["ssh_address"]
    port = host_infos["ssh_port"]
    username = host_infos["ssh_user"]
    password = host_infos["ssh_password"]

    # Création d'une instance SSHClient
    client = paramiko.SSHClient()

    # Ajout de la clé de l'hôte à la liste des clés connues (ignorer les erreurs)
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connexion à la VM
        client.connect(ip, port=port, username=username, password=password)
        return client

    except paramiko.AuthenticationException:
        logging.error("Échec de l'authentification. Vérifiez vos informations de connexion.")
        exit()
    except paramiko.SSHException as ssh_err:
        logging.error("Erreur SSH : ", ssh_err)
        exit()
    except paramiko.socket.error as e:
        logging.error("Erreur de connexion : ", e)
        exit()
    except paramiko.ssh_exception.NoValidConnectionsError as e:
        logging.error("Erreur de connexion : ", e)
        exit()


def stop_connection(client):
    client.close()