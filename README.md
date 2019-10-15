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

Make sure you are in the base directory for the repo and run

```
$ sudo ./install.sh
```

This will install all necessary packages and create the config.yaml in /dags/config/

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

You now need to copy the Twitter API keys into
the config so Twitter can verify.

**MAKE SURE TO NOT PUBLICLY RELAESE THESE KEYS**

The config.yaml is listed in the .gitignore to prevent this.


