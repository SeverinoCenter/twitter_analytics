# Twitter Analytics

Twitter Analytics is a way for data scientists to automate data collection scripts
using Airflow running on Docker.


**This is currently in active development and subject to change**


## Table of Contents

 - [1. Installation](#installation)
 - [2. Usage](#usage)
 - [3. Support](#support)

## 1. Installation

### 1.1 Required Packages

To successfully get Data Collection started, you need to have the 
pandas, twitter, and ruamel.yaml python packages. You can install
them using pip3 as follows:

```
$ pip3 install pandas twitter ruamel.yaml
```

If you don't have pip3 installed, install it using

```
$ sudo apt-get install python3-pip
```

You also need Docker and Docker Compose.

Docker can be installed using Apt with the following command:

```
$ sudo apt install docker.io
```

Follow the instructions [here](https://docs.docker.com/compose/install/#install-compose)
to install Compose

### 1.2 Twitter API Access

To get access to the Twitter API, you first need to have a twitter account.
If you don't have an account, you can sign up [here](https://www.twitter.com/signup).

Follow the next steps to access your API Key, API Secret, Access Token, and Access Token Secret
which will be needed for the next step.

 - Go [here](https://apps.twitter.com) and log in with your Twitter account. This will give you a 
   developer account under the same username as your regular Twitter account.
 - Click 'Create New App'
 - Fill out the form, agree to the terms, and click 'Create Your Twitter Application'
 - Click on the 'Keys and Access Tokens' tab to view the needed keys

### 1.3 Setup

To begin using the Twitter collection, you first need to copy the dags/config/config.yaml.sample
to dags/config/config.yaml using the command

```
$ cp dags/config/config.yaml.sample dags/config/config.yaml
```

After you have a private config.yaml file, you need the copy the Twitter API keys into
the config so Twitter can verify.

**MAKE SURE TO NOT PUBLICLY RELAESE THESE KEYS**

The config.yaml is listed in the .gitignore to prevent this.

Docker is using port 8080 by default, so make sure to open it to successfully get Docker running.

## 2. Usage

Config setup, runtime commands


## 3. Support

Submit an issue [here](https://github.com/Kuberlytics/twitter_analytics/issues/new)
