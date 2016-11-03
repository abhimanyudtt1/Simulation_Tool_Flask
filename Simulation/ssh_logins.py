import paramiko


class node(object):
    def __init__(self,ip,user='admin',password='admin@123'):
        self.ip = ip
        self.user = user
        self.password = password
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(
            paramiko.AutoAddPolicy())
    def login(self):
        self.ssh.connect(self.ip,username=self.user,password=self.password)

    def shellCmd(self,cmd):
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        stdin.write("%s\n" % self.password)
        stdin.flush()
        print type(stdin),type(stderr),type(stdout)
        stdout = stdout.readlines()
        stderr = stderr.readlines()

        print stdout,stderr


#node = node('52.77.205.226',user='ad1214',password='admin@123')

#node.login()
#node.shellCmd('sudo ps -ef')
