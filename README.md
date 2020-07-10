# parse_web_blocks: WIP

## Intro:
This is a small app which crawls and scrapes a webpage and parses the text from it in an structure manner. When extracting text it doesn't mixes up all the text in one blob and maintains the separation according to how the text appears on the webpage. Although completely functional, It is a work in progress and doesn't work too well on long webpages. 
Although the scripts are completely functional by themselves but the whole thing has been made such that it works as standalone app. MongoDB is not necessary for functioning of the scripts. 


## Setup:
	Setup the CentOS server for Crawling
	
	1. Install Python 3.6.x on CentOS
		a. Add the repository to your Yum install.
		       sudo yum install -y https://centos7.iuscommunity.org/ius-release.rpm
		b. Update Yum to finish adding the repository.
		       sudo yum update
		c. Download and install Python.
		       sudo yum install -y python36u python36u-libs python36u-devel python36u-pip
		d. Create a symbolic link, if not already done.
		       sudo ln ~/bin/python3.6 ~/bin/python3
		       sudo ln ~/bin/pip3.6 ~/bin/pip3
		e. Check Python
		       python3.6 -V or python3 -V
		f. Upgrade pip
		       sudo pip3 install --upgrade pip
		f. Install the requirements
		       pip3 -r install requirements.txt
	
	2. Install MongoDB on CentOS
		a. Add the MongoDB Repository :
		        Create a new file, `/etc/yum.repos.d/mongodb-org-3.2.repo`, so that you can install the latest release 
		        using yum. Add the following contents to the file:

		                    [mongodb-org-3.2]
		                    name=MongoDB Repository
		                    baseurl=https://repo.mongodb.org/yum/redhat/$releasever/mongodb-org/3.2/x86_64/
		                    gpgcheck=1
		                    enabled=1
		                    gpgkey=https://www.mongodb.org/static/pgp/server-3.2.asc
		b . Install MongoDB
		         sudo yum install mongodb-org

		         This command installs mongodb-org, a meta-package that includes the following:
		            mongodb-org-server - The standard MongoDB daemon, and relevant init scripts and configurations
		            mongodb-org-mongos - The MongoDB Shard daemon
		            mongodb-org-shell - The MongoDB shell, used to interact with MongoDB via the command line
		            mongodb-org-tools - Contains a few basic tools to restore, import, and export data, as well as 
		            other diverse functions.
		c. Configure MongoDB
		        Follow this link : https://www.linode.com/docs/databases/mongodb/install-mongodb-on-centos-7/#configure-mongodb
