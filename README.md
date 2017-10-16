# Center hub for Twitter Data collection

### Setting up environment
1. Get Twitter API Keys

To start with, you will need to have a Twitter account and obtain credentials (i.e. API key, API secret, Access token and Access token secret) on the Twitter developer site to access the Twitter API, following these steps:
  * Create a Twitter user account if you do not already have one.
  * Go to https://apps.twitter.com/ and log in with your Twitter user account. This step gives you a Twitter dev account under the same name as your user account.
  * Click “Create New App”
  *  Fill out the form, agree to the terms, and click “Create your Twitter application”
  * In the next page, click on “Keys and Access Tokens” tab, and copy your “API key” and “API secret”. Scroll down and click “Create my access token”, and copy your “Access token” and “Access token secret”.

2. Installing a Twitter library

We will be using a Python library called Python Twitter Tools to connect to Twitter API and downloading the data from
Twitter. There are many other libraries in various programming languages that let you use Twitter API. We choose the
Python Twitter Tools for this tutorial, because it is simple to use yet fully supports the Twitter API.
Download the Python Twitter tools at https://pypi.python.org/pypi/twitter.
Install the Python Twitter Tools package by typing in commands below while
in the directory of the installed Python Twitter tools:


```
$ python setup.py --help
$ python setup.py build
$ python setup.py install
```


*Note, if you get the error following error, you need to install the setuptools python module.*
```
Traceback (most recent call last):
  File "setup.py", line 1, in <module>
    from setuptools import setup, find_packages
ImportError: No module named setuptools
```
*This can be done by running the following commands*

*__On Linux:__*
```
$ sudo apt-get install python-setuptools
$ sudo apt-get install python3-setuptools
```

When running the `$ python setup.py install`
command, you may get the following error:
```
error: can't create or remove files in install directory
```
Don't worry, this just means that you need to add the sudo command:
```
$ sudo python setup.py install
```
