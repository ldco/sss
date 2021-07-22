import sys, os, subprocess

try:
    import json, paramiko, random, csv
    from scp import SCPClient
except ImportError:
    subprocess.call(["pip3", "install", json])
    subprocess.call(["pip3", "install", paramiko])
    subprocess.call(["pip3", "install", scp])
    subprocess.call(["pip3", "install", random])
    subprocess.call(["pip3", "install", csv])

FILENAME = "settings_secret.json"
FILE = open(FILENAME, "r+")
SETTINGS = json.load(FILE)
class Serve:
    def __init__(self, index):
        self.index = index
        self.list = SETTINGS["servers"]
        self.ip = self.index
        self.name = self.list.get(self.index)["name"]
        self.user = self.list.get(self.index)["user"]
        self.root_pass = self.list.get(self.index)["root_pass"]
        self.user_pass = self.list.get(self.index)["user_pass"]
        self.stored_user_pass = ""
        self.server = self.list.get(self.index)["server"]
        self.lang = self.list.get(self.index)["language"]
        self.db = self.list.get(self.index)["db"]
        self.domains = self.list.get(self.index)["domains"]
        self.apps = self.list.get(self.index)["apps"]
        self.files = self.list.get(self.index)["files"]
        self.misc = self.list.get(self.index)["misc"]
        self.mail = self.list.get(self.index)["mail"]
        self.pass_format = self.list.get(self.index)["password_format"]
        #shared
        self.sh_apps = SETTINGS["shared"]["apps"]
        self.sh_files = SETTINGS["shared"]["files"]
        self.sh_misc = SETTINGS["shared"]["misc"]
        self.passwsettings = SETTINGS["shared"]["passwords"]

    # main method
    def make(self):
        self.create_new_user()
        self.put_files_on_server(self.sh_files)
        if len(self.files) > 0:
           self.put_files_on_server(self.files)
        self.firewall()
        self.update()
        self.install_apps()
        self.fail2ban()
        self.update()
        self.install_all_langs()
        self.update()
        self.install_server()
        self.install_db()
        self.update()
        self.install_all_domains()
        self.update()
        self.install_misc()
        self.update()
        self.reboot_server()
        self.generate_final_file()
        self.mail_final_file()

    #ssh methods
    def ssh(self, root: bool):
        user = ""
        passw = ""
        if root:
            user ="root"
            passw = self.root_pass
        else:
            user = self.user
            if self.stored_user_pass == "":
                passw = self.user_pass
            else:
                passw = self.stored_user_pass
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            print(f"Connecting to {user.upper()} {self.ip} ...")
            client.connect(hostname = self.ip, username = user, password = passw, allow_agent=False,look_for_keys=False)
            print("Connected\n")
            return client
        except paramiko.AuthenticationException as error:
            print(error)
            return False

    def run_cmd(self, client, cmd, text):
        passw = ""
        if self.stored_user_pass == "":
            passw = self.user_pass
        else:
            passw = self.stored_user_pass
        print(f"Executing {text}")
        try:
            cmd_pass = f"echo {passw} | sudo -S {cmd}"
            stdin, stdout, stderr = client.exec_command(cmd_pass, get_pty=True)
            cmd_result = stdout.read().decode("utf8"), stderr.read().decode("utf8")
            for line in cmd_result:
                print(line)
        except paramiko.SSHException as e:
            print(str(e))

    def reboot_server(self):
        ssh = self.ssh(False)
        if ssh:
            self.run_cmd(ssh, f"sudo reboot", f"REBOOT SERVER")
            ssh.close()

    #special methods
    def generate_token(self, custom: list): 
        #length:int|upper:bool|specials:bool|digits:bool
        length = ""
        isupper = ""
        isspecials = ""
        isdigits = ""
        upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        specials = "~@_+:#^%;="
        digits = "01234567890"
        alls = "abcdefghijklmnopqrstuvwxyz"
        if custom is False:
            obj = self.passwsettings
            length = obj["length"]
            isupper = obj["upper"]
            isspecials =obj["specials"]
            isdigits = obj["digits"]
        else:
            length = custom[0]
            isupper = custom[1]
            isspecials = custom[2]
            isdigits = custom[3]
        if isupper:
            alls += upper
        if isspecials:
            alls += specials
        if isdigits:
            alls += digits
        generated = ""
        for i in range(length):
            generated = generated + random.choice(alls)
        return generated

    def update_json(self, path, value):
        fl = FILENAME
        try:
            with open(fl, "r+") as f:
                json_data = json.load(f)
                data = json_data["servers"].get(self.index)
                key_list = path.split(".")
                for k in key_list[:-1]:
                    data = data[k]
                print(f"Writing {path} to {fl}")
                data[key_list[-1]] = value
                f.seek(0)
                f.write(json.dumps(json_data))
                f.truncate()
        except:
            print(f"Error writing to {fl}")

    def update(self):
        ssh = self.ssh(False)
        if ssh:
            self.run_cmd(ssh, f"sudo apt update -y", f"Update")
            self.run_cmd(ssh, f"sudo apt dist-upgrade -y", f"Distupgrade")
            self.run_cmd(ssh, f"sudo apt update -y", f"Update")
            self.run_cmd(ssh, f"sudo apt upgrade -y", f"Upgrade")
            self.run_cmd(ssh, f"sudo apt --purge autoremove -y", f"Autoremove")
            self.run_cmd(ssh, f"sudo apt update -y", f"Update")
            ssh.close()

    def ap(self, wait, text):
        #animated print
        pass

    def generate_final_file(self):
        x = self.pass_format
        obj = {
            "project name": self.name,
            "ip" : self.ip,
            "ssh root": f"root@{self.ip}",
            "root pass": self.root_pass,
            "ssh user": f"{self.user}@{self.ip}",
            "user pass" : self.user_pass
        }
        
        for k, v in self.db.items():
            if k == "maria":
                obj["mariadb"] = {
                    "rootpass": self.db["maria"]["rootpass"],
                    "userpass":self.db["maria"]["userpass"],
                    "dbuser":self.db["maria"]["dbuser"],
                    "dbname":self.db["maria"]["dbname"]
                }
                if "gui" in self.db["maria"] and self.db["maria"]["gui"] != "":
                    obj["mariadb"]["gui"] = self.db["maria"]["gui"]
            if k == "mongo":
                if "StringURI" in self.db["mongo"]:
                    obj["mongodb"] = self.db["mongo"]["StringURI"]
                else:
                    print("No StringURI in Mongodb!")
                if "gui" in self.db["mongo"] and self.db["mongo"]["gui"] != "":
                    obj["mongodb"]["gui"] = self.db["mongo"]["gui"]

        if "phpmyadmin" in self.list[self.index]:
                obj["phpmyadmin"] = self.list[self.index]["phpmyadmin"]["secure_address"]

        success = ""
        try:
            if len(x) != 0:
                if "pdf" in x[0]:
                    self.generate_final_file_pdf(obj)
                if "txt" in x[0] or len(x[0]):
                    self.generate_final_file_txt(obj)
            else:
                self.generate_final_file_txt(obj)
            success = True
            print(f"Secrets file for {self.ip} generated")
        except:
            print(f"Error generating secrets for {self.ip}")
            success = False

        if success:
            fl = FILENAME
            try:
                with open(fl, 'r+') as f:
                    json_data = json.load(f)
                    data = json_data["servers"]
                    data[self.index] = ""
                    f.seek(0)
                    f.write(json.dumps(json_data))
                    f.truncate()
            except:
                print(f"Error deleting for {self.ip}")

    def mail_final_file(self):
        pass

    def checkstatus(self):
        pass

    #first degree methods
    def create_new_user(self):
        name = self.user
        ssh = self.ssh(True)
        if ssh:
            if self.user_pass == "":
                print(f"Generating password for user {name}...")
                passw = self.generate_token([64, True, False, True])
                print("Password generated")
                self.stored_user_pass = passw
                self.run_cmd(ssh, f"adduser --disabled-password --gecos '' {name}", f"Create new user {name}")
                self.run_cmd(ssh, f"echo '{name}:{passw}' | sudo chpasswd", f"Create password")
                self.run_cmd(ssh, f"usermod -aG sudo {name}", f"adding {name} to group")
                self.update_json("user_pass", passw)
                ssh.close()
            else:
                print(f"User {name} exist, closing connection")
                ssh.close()
                

    def put_files_on_server(self, listt: list):
        ssh = self.ssh(True)
        if ssh:
            user = self.user
            host = self.ip
            try:
                print("SCP connection")
                scp = SCPClient(ssh.get_transport())
                for x in listt:
                    try:
                        print(f"Copying {x} to {host}/home/{user}")
                        scp.put(f"files/{x}", f"/home/{user}/")
                    except:
                        print("File copying Error")
            except paramiko.SSHException as e:
                print(str(e))
            finally:
                scp.close()
                ssh.close()

    def firewall(self):
        ssh = self.ssh(False)
        if ssh:
            self.run_cmd(ssh, "sudo ufw allow OpenSSH", "Allow OpenSSH")
            self.run_cmd(ssh, "sudo ufw --force enable", "Enable ufw")
            ssh.close()
            
    def install_apps(self):
        ssh = self.ssh(False)
        apps = self.sh_apps
        if self.apps != "":
            apps += self.apps
        if ssh:
            self.run_cmd(ssh, f"sudo apt install -y {self.sh_apps}", "Installing apps")
            ssh.close()

    def fail2ban(self):
        ssh = self.ssh(False)
        if ssh:
            self.run_cmd(ssh, "sudo systemctl enable fail2ban", "Enable fail2ban")
            ssh.close()

    def install_all_langs(self):
        l = []
        for k, v in self.lang.items():
            l.append(k)
        if len(l) == 0:
                print("No languages to install")
        else:
            print(f"Langs to install: \n")
            for k, v in self.lang.items():
                print(f"    {k}: {v['v']}\n    With libraries: {v['req']}\n")
            for k, v in self.lang.items():
                if k == "python":
                    self.install_python(v['v'], v['req'])
                if k == "php":
                    self.install_php(v['v'], v['req'])

    def install_server(self):
        option = self.server
        print("Server to install: ")
        if option == "1":
            print("Apache")
            self.install_apach()
        elif option == "2":
            print("NGINX")
            self.install_nginx()
        elif option == "3":
            print("Apache with NGINX as reverse proxy")
            self.install_nginx_on_apach()
        else:
            print(f"No option for server, not installing server")

    def install_all_domains(self):
        
        for k in self.domains.items():
            self.install_domain(k[0], k[1])


    def install_db(self):
        l = []
        for k, v in self.db.items():
            l.append(k)
        if len(l) == 0:
                print("No databases to install")
        else:
            print(f"Databases to install: \n")
            for k, v in self.db.items():
                if k == "maria":
                    gui_ma = ""
                    dbname_ma = ""
                    dbuser_ma = ""
                    if "gui" not in self.db["maria"]:
                        gui_ma = ""
                    else:
                        gui_ma = self.db["maria"]["gui"]
                    if "dbname" not in self.db["maria"] or self.db["maria"]["dbname"] == "":
                        dbname_ma = "main_db"
                    else:
                        dbname_ma = self.db["maria"]["dbname"]
                    if "dbuser" not in self.db["maria"] or self.db["maria"]["dbuser"] == "":
                        dbuser_ma = "admin"
                    else:
                        dbuser_ma = self.db["maria"]["dbuser"]
                    print(f"Mariadb, user: {dbuser_ma}, db: {dbname_ma}")
                    self.install_maria(gui_ma, dbname_ma, dbuser_ma)
                if k == "mongo":
                    gui_mo = ""
                    dbname_mo = ""
                    dbuser_mo= ""
                    if "gui" not in self.db["mongo"]:
                        gui_mo = ""
                    else:
                        gui_mo = self.db["mongo"]["gui"]
                    if "dbname" not in self.db["mongo"] or self.db["mongo"]["dbname"] == "":
                        dbname_mo = "main_db"
                    else:
                        dbname_mo = self.db["mongo"]["dbname"]
                    if "dbuser" not in self.db["mongo"] or self.db["mongo"]["dbuser"] == "":
                        dbuser_mo = "admin"
                    else:
                        dbuser_mo = self.db["mongo"]["dbuser"]
                    print(f"Mongodb, user: {dbuser_mo}, db: {dbname_mo}")
                    self.install_mongo(gui_mo, dbname_mo, dbuser_mo)

    def install_misc(self):
        if "cockpit" in self.misc.keys() and self.misc["cockpit"] == "true":
            self.install_cockpit()
        if "certbot" in self.sh_misc.keys() and self.sh_misc["certbot"] == "true":
            self.install_certbot()

    #second degree methods
    def install_apach(self):
        ssh = self.ssh(False)
        if ssh:
            cmd_1 = f"sudo apt install -y apache2"
            cmd_2 = f"sudo ufw allow 'Apache'"
            cmd_777 = f"sudo chmod 777 /etc/apache2"
            cmd_777F = f"sudo chmod 777 /etc/apache2/apache2.conf"
            cmd_3 = f"sudo echo 'ServerName localhost' >> /etc/apache2/apache2.conf"
            cmd_700F = f"sudo chmod 700 /etc/apache2"
            cmd_700 = f"sudo chmod 700 /etc/apache2"
            cmd_php_4 = f"sudo systemctl reload apache2"
            self.run_cmd(ssh, cmd_1, f"Install Apache")
            self.run_cmd(ssh, cmd_2, f"Utf allow 'Apache Full'")
            self.run_cmd(ssh, cmd_777, f"chmod 777 to /etc/apache2")
            self.run_cmd(ssh, cmd_777F, f"chmod 777 to /etc/apache2/apache2.conf")
            self.run_cmd(ssh, cmd_3, f"'ServerName localhost' in apache2.conf")
            self.run_cmd(ssh, cmd_700F, f"chmod 700 to /etc/apache2/apache2.conf")
            self.run_cmd(ssh, cmd_700, f"chmod 700 to /etc/apache2")
            self.run_cmd(ssh, cmd_php_4, f"Reload apache2")
            l = []
            for k, v in self.lang.items():
                l.append(k)
            if "php" in l:
                phpv = self.lang["php"]["v"]
                print(f"PHP version: {phpv}")
                cmd_php_1 = f"sudo a2enmod proxy_fcgi setenvif"
                cmd_php_2 = f"sudo systemctl restart apache2"
                cmd_php_3= f"sudo a2enconf php{phpv}-fpm"
                self.run_cmd(ssh, cmd_php_1, f"a2enmod proxy_fcgi")
                self.run_cmd(ssh, cmd_php_2, f"Restart apache2")
                self.run_cmd(ssh, cmd_php_3, f"a2enconf php{phpv}-fpm")
                self.run_cmd(ssh, cmd_php_4, f"Reload apache2")
            ssh.close()

    def install_nginx(self):
        ssh = self.ssh(False)
        if ssh:
            cmd_1 = f"sudo apt install -y nginx"
            cmd_2 = f"sudo ufw allow 'Nginx HTTP'"
            self.run_cmd(ssh, cmd_1, f"Install NGINX")
            self.run_cmd(ssh, cmd_2, f"Utf allow 'Nginx HTTP'")
            ssh.close()

    def install_nginx_on_apach(self):
        print("Nginx as reverse proxy option not available in this version")

    def install_python(self, v, req):
        ssh = self.ssh(False)
        if ssh:
            cmd = f"sudo apt install -y python{v} python3-apt python-pil.imagetk python3-pip python3-dev"
            self.run_cmd(ssh, cmd, f"Install Python {v}")
            if req != "":
                cmd_req = f"sudo pip3 install {req}"
                self.run_cmd(ssh, cmd_req, f"Pip install")
                ssh.close()

    def install_php(self, v, req):
        ssh = self.ssh(False)
        if ssh:
            php_ppa = "ppa:ondrej/php"
            composer_url = "https://getcomposer.org/installer"
            cmd_ppa = f"sudo add-apt-repository -y {php_ppa}"
            cmd_php = f"sudo apt install -y php{v} php{v}-cli libapache2-mod-php{v}"
            cmd_php_libs = f"sudo apt install -y php{v}-{{{req}}}"
            cmd_comp = f"curl -s {composer_url} -o composer-setup.php && sudo php composer-setup.php --install-dir=/usr/local/bin --filename=composer"
            self.run_cmd(ssh, cmd_ppa, f"Adding PPA {php_ppa}")
            self.run_cmd(ssh, "sudo apt update", f"Updating server")
            self.run_cmd(ssh, cmd_php, f"Install PHP {v}")
            self.run_cmd(ssh, cmd_php_libs, f"Install PHP {v} libraries")
            self.run_cmd(ssh, cmd_comp, f"Install Composer")
            ssh.close()

    def install_domain(self, domain, system):
        ssh = self.ssh(False)
        if ssh:
            cmd_mkdir = f"sudo mkdir /var/www/{domain}/public_html"
            cmd_chown = f"sudo chown -R $USER:$USER /var/www/{domain}/public_html"
            cmd_chmod = f"sudo chmod -R 777 /var/www/"
            echo_text = f"<VirtualHost *:80>\nServerAdmin {self.mail}\nServerName {domain}\nServerAlias www.{domain}\nDocumentRoot /var/www/{domain}/public_html/\nErrorLog ${{APACHE_LOG_DIR}}/error.log\nCustomLog ${{APACHE_LOG_DIR}}/access.log combined\n</VirtualHost>"
            cmd_touch1 = f"touch /etc/apache2/sites-available/{domain}.conf"
            cmd_777ap = f"sudo chmod -R 777 /etc/apache2"
            cmd_777F = f"sudo chmod -R 777 /etc/apache2/sites-available/{domain}.conf"
            cmd_echo = f"sudo echo '{echo_text}' > /etc/apache2/sites-available/{domain}.conf"
            cmd_700F = f"sudo chmod -R 700 /etc/apache2/sites-available/{domain}.conf"
            cmd_700ap = f"sudo chmod -R 777 /etc/apache2"
            cmd_a2ensite = f"sudo a2ensite {domain}.conf"
            cmd_a2dis = f"sudo a2dissite 000-default.conf"
            cmd_apache = f"sudo apache2ctl configtest"
            cmd_restart = f"sudo systemctl restart apache2"
            echo_html = f"<html><head><title></title></head><body><h1>{domain}</h1></body></html>EOF"
            cmd_touch2 = f"touch /var/www/{domain}/public_html/index.html"
            cmd_777F2 = f"sudo chmod -R 777 /var/www/{domain}/public_html/index.html"
            cmd_echo2 = f"sudo echo '{echo_html}' > /var/www/{domain}/public_html/index.html"
            cmd_700F2 = f"sudo chmod -R 700 /var/www/{domain}/public_html/index.html"

            self.run_cmd(ssh, cmd_mkdir, f"mkdir /var/www/{domain}/public_html")
            self.run_cmd(ssh, cmd_chown, f"chown /var/www/{domain}/public_html")
            self.run_cmd(ssh, cmd_chmod, f"chmod 755 /var/www")
            self.run_cmd(ssh, cmd_touch1, f"creating /etc/apache2/sites-available/{domain}.conf")
            self.run_cmd(ssh, cmd_777ap, f"777 /etc/apache2")
            self.run_cmd(ssh, cmd_777F, f"777 /etc/apache2/sites-available/{domain}.conf")
            self.run_cmd(ssh, cmd_echo, f"echo /etc/apache2/sites-available/{domain}.conf")
            self.run_cmd(ssh, cmd_700F, f"700 /etc/apache2/sites-available/{domain}.conf")
            self.run_cmd(ssh, cmd_700ap, f"777 /etc/apache2")
            self.run_cmd(ssh, cmd_a2ensite, f"")
            self.run_cmd(ssh, cmd_a2dis, f"a2ensite {domain}.conf")
            self.run_cmd(ssh, cmd_apache, f"apache2ctl configtest")
            self.run_cmd(ssh, cmd_restart, f"restart apache2")
            self.run_cmd(ssh, cmd_touch2, f"creating /var/www/{domain}/public_html/index.html")
            self.run_cmd(ssh, cmd_777F2, f"777 /var/www/{domain}/public_html/index.html")
            self.run_cmd(ssh, cmd_echo2, f"echo /var/www/{domain}/public_html/index.html")
            self.run_cmd(ssh, cmd_700F2, f"700 /var/www/{domain}/public_html/index.html")
            self.run_cmd(ssh, cmd_restart, f"restart apache2")
            if system == "wp":
                self.install_wordpress(domain)
            if system == "django":
                self.install_django(domain)
            ssh.close()

    def install_mongo(self, gui, db, user):
        ssh = self.ssh(False)
        if ssh:
            #install
            print(self.db["mongo"])
            if "StringURI" not in self.db["mongo"] or self.db["mongo"]["StringURI"] == "":
                cmd_inst = "sudo apt install -y mongodb"
                cmd_start = "sudo service mongodb start"
                cmd_enable = "sudo systemctl enable mongodb"
                self.run_cmd(ssh, cmd_inst, f"Install Mongodb")
                self.run_cmd(ssh, cmd_start, f"Start Mongodb")
                self.run_cmd(ssh, cmd_enable, f"Enable Mongodb")
                db_user_pass = self.generate_token([64, True, False, False])
                #create user and db
                create_user = f"mongo admin --eval \"db.createUser({{user: '{user}', pwd: '{db_user_pass}', roles: [ {{ role: 'userAdminAnyDatabase', db: 'admin' }}, 'readWriteAnyDatabase' ]}})\""
                create_db = f"mongo {db} --eval \"db.user.insert({{name: 'user'}})\""
                self.run_cmd(ssh, create_user, f"Creating admin user {user}")
                self.run_cmd(ssh, create_db, f"Creating db {db}")
                #enable auth
                auth = "mongod --auth --port 27017 --dbpath /var/lib/mongodb"
                self.run_cmd(ssh, auth, f"Enabling mongo auth")
                #generate url
                StringURI = f"mongodb://{user}:{db_user_pass}@{self.ip}/{db}?authSource=admin"
                #write credentials
                self.update_json("db.mongo", {"StringURI": StringURI})
            else:
                print("\nStringURI for Mongodb allready exist,\n Skipping install Mongodb\n")
            ssh.close()

    def install_maria(self, gui, db_name, db_user):
        ssh = self.ssh(False)
        if ssh:
            #install
            if "rootpass" not in self.db["maria"] or self.db["maria"]["rootpass"] == "":
                cmd_inst = "sudo apt install -y mariadb-server"
                cmd_update = "sudo apt update"
                cmd_enab = "sudo systemctl enable mariadb"
                self.run_cmd(ssh, cmd_inst, f"Install Mariadb")
                self.run_cmd(ssh, cmd_update, f"Update")
                self.run_cmd(ssh, cmd_enab, f"Enable Mariadb")
                #sql queries
                db_root_pass = ""
                db_user_pass = ""
                db_shell = f"sudo mysql -u root -e"
                
                db_root_pass = self.generate_token(False)
                sql_secure = f"\"UPDATE mysql.user SET Password=PASSWORD('{db_root_pass}') WHERE User='root'; DELETE FROM mysql.user WHERE User=''; DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1'); DROP DATABASE IF EXISTS test; DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';FLUSH PRIVILEGES;\""
                self.run_cmd(ssh, f"{db_shell} {sql_secure}", f"Secure Installation")

                if "userpass" not in self.db["maria"] or self.db["maria"]["userpass"] == "":
                    db_user_pass = self.generate_token(False)
                    db_shell_root = f"sudo mysql -u root -p'{db_root_pass}' -e"
                    sql_create_user = f"\"CREATE USER '{db_user}'@'localhost' IDENTIFIED BY '{db_user_pass}'; GRANT ALL ON *.* TO '{db_user}'@'localhost' IDENTIFIED BY '{db_user_pass}' WITH GRANT OPTION; FLUSH PRIVILEGES;\""
                    self.run_cmd(ssh, f"{db_shell_root} {sql_create_user}", f"Create admin user - {db_user}")
                else:
                    db_user_pass = self.db["maria"]["userpass"]
                    print(f"Password for {db_user} exist, skipping creating user {db_user}")
                sql_create_db = f"\"CREATE DATABASE IF NOT EXISTS {db_name} DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci;\""
                self.run_cmd(ssh, f"{db_shell_root} {sql_create_db}", f"Create DB - {db_name}")
                #write credentials
                self.update_json("db.maria", {"gui":gui, "dbname" : db_name, "rootpass" : db_root_pass, "dbuser" : db_user, "userpass" : db_user_pass})
                ssh.close()
                if gui == "phpmyadmin":
                    self.install_phpmyadmin()
            else:
                db_root_pass = self.db["maria"]["rootpass"]
                print("Root password in Mariadb already exist, skipping Install Mariadb")

    def install_phpmyadmin(self):
        ssh = self.ssh(False)
        if ssh:
            php_secure_address = self.generate_token([32, False, False, True])
            blowfish_secret = self.generate_token([64, True, False, True])
            phpmyadmin_v = "5.0.3"
            zip_file = f"phpMyAdmin-{phpmyadmin_v}-all-languages"
            cmd_wget = f"wget https://files.phpmyadmin.net/phpMyAdmin/{phpmyadmin_v}/{zip_file}.zip"
            cmd_unzip = f"unzip {zip_file}.zip"
            cmd_rm = f"sudo rm {zip_file}.zip"
            cmd_mv = f"sudo mv {zip_file} /usr/share/phpmyadmin"
            cmd_mkd = f"sudo mkdir /usr/share/phpmyadmin/tmp"
            cmd_chown = f"sudo chown -R www-data:www-data /usr/share/phpmyadmin"
            cmd_chmod = f"sudo chmod 755 /usr/share/phpmyadmin/tmp"
            text_echo1 =f"Alias /{php_secure_address} /usr/share/phpmyadmin\n<Directory /usr/share/phpmyadmin/>AddDefaultCharset UTF-8\n<IfModule mod_authz_core.c><RequireAny>Require all granted</RequireAny></IfModule></Directory>\n<Directory /usr/share/phpmyadmin/setup/><IfModule mod_authz_core.c><RequireAny>Require all granted</RequireAny></IfModule></Directory>"
            cmd_755 = f"sudo chmod 755 /etc/apache2"
            cmd_touch1 = "sudo touch /etc/apache2/conf-available/phpmyadmin.conf"
            cmd_777F = f"sudo chmod 777 /etc/apache2/conf-available/phpmyadmin.conf"
            cmd_echo1 = f"sudo echo '{text_echo1}' >> /etc/apache2/conf-available/phpmyadmin.conf"
            cmd_700F = f"sudo chmod 700 /etc/apache2/conf-available/phpmyadmin.conf"
            cmd_700 = f"sudo chmod 700 /etc/apache2"
            cmd_a2e = f"sudo a2enconf phpmyadmin"
            cmd_restart = f"sudo systemctl restart apache2"
            text_echo2 = f"$cfg['Servers'][$i]['auth_type'] = 'cookie';\n$cfg['Servers'][$i]['AllowRoot'] = FALSE;\n$cfg['blowfish_secret'] = '{blowfish_secret}';"
            cmd_755_2 = f"sudo chmod 755 /usr/share/"
            cmd_touch2 = f"sudo touch /usr/share/phpmyadmin/config.inc.php"
            cmd_777F_2 = f"sudo chmod 777 /usr/share/phpmyadmin/config.inc.php"
            cmd_echo2 = f"sudo echo '{text_echo2}' > /usr/share/phpmyadmin/config.inc.php"
            cmd_700F_2 = f"sudo chmod 700 /usr/share/phpmyadmin/config.inc.php"
            cmd_700_2 = f"sudo chmod 700 /usr/share/"
            self.run_cmd(ssh, cmd_wget, f"wget PhpMyAdmin")
            self.run_cmd(ssh, cmd_unzip, f"Unzip PhpMyAdmin")
            self.run_cmd(ssh, cmd_rm, f"removing {zip_file}.zip")
            self.run_cmd(ssh, cmd_mv, f"Moving to /usr/share/phpmyadmin")
            self.run_cmd(ssh, cmd_mkd, f"New dir /usr/share/phpmyadmin/tmp")
            self.run_cmd(ssh, cmd_chown, f"Chown dir")
            self.run_cmd(ssh, cmd_chmod, f"Chmod dir")
            self.run_cmd(ssh, cmd_755, f"chmod 755 to /etc/apache2")
            self.run_cmd(ssh, cmd_touch1, f"touch /etc/apache2/conf-available/phpmyadmin.conf")
            self.run_cmd(ssh, cmd_777F, f"chmod 755 to /etc/apache2/conf-available/phpmyadmin.conf")
            self.run_cmd(ssh, cmd_echo1, f"Writing to /etc/apache2/conf-available/phpmyadmin.conf")
            self.run_cmd(ssh, cmd_700F, f"chmod 700 to /etc/apache2/conf-available/phpmyadmin.conf")
            self.run_cmd(ssh, cmd_700, f"chmod 700 to /etc/apache2")
            self.run_cmd(ssh, cmd_a2e, f"a2enconf phpmyadmin")
            self.run_cmd(ssh, cmd_restart, f"restart apache2")
            self.run_cmd(ssh, cmd_755_2, f"chmod 755 to /usr/share")
            self.run_cmd(ssh, cmd_touch2, f"touch /usr/share/phpmyadmin/config.inc.php")
            self.run_cmd(ssh, cmd_777F_2, f"chmod 777 to /usr/share/phpmyadmin/config.inc.php")
            self.run_cmd(ssh, cmd_echo2, f"Writing to /usr/share/phpmyadmin/config.inc.php")
            self.run_cmd(ssh, cmd_700F_2, f"chmod 700 to /usr/share/phpmyadmin/config.inc.php")
            self.run_cmd(ssh, cmd_700_2, f"chmod 700 to /usr/share")
            self.run_cmd(ssh, cmd_restart, f"restart apache2")
            self.update_json("phpmyadmin", {"secure_address" : f"http//:{self.ip}/{php_secure_address}/index.php"})
            ssh.close()

    def install_certbot(self):
        ssh = self.ssh(False)
        if ssh:
            cmd_snap = "sudo snap install --classic certbot"
            cmd_ln = "sudo ln -s /snap/bin/certbot /usr/bin/certbot"
            cmd_run = f"sudo certbot --apache --non-interactive --agree-tos -m {self.mail}"
            self.run_cmd(ssh, cmd_snap, f"Snap install Certbot")
            self.run_cmd(ssh, cmd_ln, f"ln Certbot")
            self.run_cmd(ssh, cmd_run, f"Run Certbot")

    def install_cockpit(self):
        pass

    #third degree methods
    def install_wordpress(self, domain):
        pass
    def install_django(self, domain):
        pass

    def generate_final_file_txt(self, obj: dict):
        text = ""
        for k,v in obj.items():
            text += f"{k}:\n{v}\n"
        os.system(f"echo \"{text}\" > \"secret_{self.ip}.txt\"")

    def generate_final_file_pdf(self, obj: dict):
        print("PDF option is not yet implemented")

for count, value in enumerate(SETTINGS["servers"]):
    Serve(value).make()


