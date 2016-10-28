import os
from traitlets import Unicode

from jupyterhub.spawner import LocalProcessSpawner


class AutoUserLocalProcessSpawner(LocalProcessSpawner):
    """
    A version of LocalProcessSpawner that doesn't require users to exist on
    the system beforehand.

    Note: DO NOT USE THIS FOR PRODUCTION USE CASES! It is very insecure, and
    provides absolutely no isolation between different users!
    """

    home_path_template = Unicode(
        '/tmp/{userid}',
        config=True,
        help='Template to expand to set the user home. {userid} and {username} are expanded'
    )
    
    execute_after_mkdir = Unicode(
        '',
        config=True,
        help='Path to a script to execute. The script will receive the destination path as current directory'
    )


    @property
    def home_path(self):
        return self.home_path_template.format(
            userid=self.user.id,
            username=self.user.name
        )

    def make_preexec_fn(self, name):
        home = self.home_path
        execute_after_mkdir = self.execute_after_mkdir
        def preexec():
            self.log.debug("Preexec!")
            do_execute = False
            try:
                self.log.debug("User home directory: {}".format(home))
                if not os.path.exists(home):
                   do_execute = True
                self.log.debug("Ensuring the directory exists")
                os.makedirs(home, 0o755, exist_ok=True)
                os.chdir(home)
                if do_execute and execute_after_mkdir:
                    self.log.debug("Executing: {!r}".format(execute_after_mkdir))
                    os.system(execute_after_mkdir)
            except e:
                print(e)
                self.log.debug("Exception: {}".format(e))
            shared_dir = os.path.join(self.home_path, "shared")
            if not os.path.exists(shared_dir):
                os.symlink("/home/anaconda/jupyterhub/shared", shared_dir)

        return preexec

    def user_env(self, env):
        env['USER'] = self.user.name
        env['HOME'] = self.home_path
        env['SHELL'] = '/bin/bash'
        env['http_proxy'] = os.environ['http_proxy']
        env['https_proxy'] = os.environ['https_proxy']
        env['no_proxy'] = os.environ['no_proxy']
        env['HADOOP_COMMON_HOME'] = os.environ['HADOOP_COMMON_HOME']
        env['HADOOP_COMMON_LIB_NATIVE_DIR'] = os.environ['HADOOP_COMMON_LIB_NATIVE_DIR']
        env['HADOOP_HDFS_HOME'] = os.environ['HADOOP_HDFS_HOME']
        env['HADOOP_INSTALL'] = os.environ['HADOOP_INSTALL']
        env['HADOOP_OPTS'] = os.environ['HADOOP_OPTS']
        env['HADOOP_VERSION'] = os.environ['HADOOP_VERSION']
        env['HADOOP_CONF_DIR'] = os.environ['HADOOP_CONF_DIR']
        env['HADOOP_DFS_HOST'] = os.environ['HADOOP_DFS_HOST']
        env['HADOOP_DFS_PORT'] = os.environ['HADOOP_DFS_PORT']
        env['JAVA_HOME'] = os.environ['JAVA_HOME']
        env['JAVA_OPTS'] = os.environ['JAVA_OPTS']
        env['JAVA_PROXY_OPTS'] = os.environ['JAVA_PROXY_OPTS']
        env['HADOOP_DFS_WEBHDFS_PORT'] = os.environ['HADOOP_DFS_WEBHDFS_PORT']
        env['SBT_OPTS'] = os.environ['SBT_OPTS']
        env['MAVEN_OPTS'] = os.environ['MAVEN_OPTS']
        env['SPARK_HOME'] = os.environ['SPARK_HOME']
        env['SPARK_MASTER'] = os.environ['SPARK_MASTER']
        env['SPARK_CLUSTER_OPTS'] = os.environ['SPARK_CLUSTER_OPTS']
        env['PYSPARK_SUBMIT_ARGS'] = os.environ['PYSPARK_SUBMIT_ARGS']
        if os.environ.get('LD_LIBRARY_PATH'):
            env['LB_LIBRARY_PATH'] = os.environ['LD_LIBRARY_PATH']

        return env
