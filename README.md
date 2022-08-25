# JFrog Artifactory Instance CLI Manager

This project allows a user to interact with their artifactory instance provided by JFrog using a simple command line interface. This project
is an example created as a part of the JFrog interview process in order to demonstrate the interviewees skills. 

## Prerequisites
Built and tested with Python 3.9.2. Python 3.9 or greater is therefore strongly recommended. All required modules can be installed
using included `requirements.txt` by running command `pip install -r requirements.txt` from the root directory. 

Due to usage of the `getpass` module to take password inputs from user, a tty input stream is required where echo input can be disabled. 

**Author's Note**: Most standard terminal interfaces will match the tty requirement, but I had an issue with GitBash on my Windows machine. Powershell worked just fine.

## Set-up

Using the CLI requires first logging in to the dummy account used for this assignment. In order to log in use the `--sign-in` command

```
$ python ./jartifactory.py --sign-in
```

When prompted, enter the provided credentials:

Username: testuser
Password: NotAllWhoWanderAre@Lost98

The above credentials are valid for the default host used by `jartifactory`. `jartifactory` can be directed towards other artifactory hosts using 
the `--set-default-host` command. If this is done, then credentials that are valid for that instance of artifactory will have to be used instead. 

## Usage and Command Options

There are a great many options that can be specified by `jartifactory` in order to interact with Artifactory hosts by using the Artifactory REST API. 
If you ever want to quickly check the available options, use the `--help` or `-h` flag to see all possible arguments. 

### --sign-in 

As detailed in the [Set-up](#set-up) section, this option allows the user to sign in. It is required to authenticate all other `jartifactory` actions agains the host. 

Utilizes Artifactory REST API functions 
- [Get API Key](https://www.jfrog.com/confluence/display/JFROG/Artifactory+REST+API#ArtifactoryRESTAPI-GetAPIKey)
- [Create API Key](https://www.jfrog.com/confluence/display/JFROG/Artifactory+REST+API#ArtifactoryRESTAPI-CreateAPIKey)
- [Create Token](https://www.jfrog.com/confluence/display/JFROG/Artifactory+REST+API#ArtifactoryRESTAPI-CreateToken)

### --set-default-host \[HOST\]

Sets the host url where `jartifactory` will carry out its API operations. Given this is a toy project, this need not be used, but it would allow one to point the tool
to another Artifactory instance. By default the tool will point to https://wmartinassignment.jfrog.io/artifactory even if this command is never used. 

### --ping

Sends a ping to the Artifactory host and prints the response. Can also be shortened to `-p`. 

```
$ python jartifactory.py --ping
200 OK
```

Utilizes Artifactory REST API function [System Health Ping](https://www.jfrog.com/confluence/display/JFROG/Artifactory+REST+API#ArtifactoryRESTAPI-SystemHealthPing).

### --version
Gets the version information of the instance of Artifactory at the default host (https://wmartinassignment.jfrog.io/artifactory unless changed by `--set-default-host`). 
Can also be shortened to `-v`. 
```
$ python jartifactory.py --version
Artifactory Version 7.41.6 - revision 74106900
```

Utilizes Artifactory REST API function 
[Version and Add-ons information](https://www.jfrog.com/confluence/display/JFROG/Artifactory+REST+API#ArtifactoryRESTAPI-VersionandAdd-onsinformation).

### --create-user
Creates a new Artifactory user. Prompts the user for details on the user to be created. The email, username, and password are requested before user creation. 
```
$ python jartifactory.py --create-user
Email: [Enter email of new user, then press return]
Username (default same as email): [Enter username for new user, or leave empty to set username to value of email]
Password: [Enter password for the new user]
Created user [Given username]
```

Utilizes Artifactory REST API function 
[Create or Replace User](https://www.jfrog.com/confluence/display/JFROG/Artifactory+REST+API#ArtifactoryRESTAPI-CreateorReplaceUser).

**Note**: Passwords must meet requirements of having at least 1 uppercase and 1 lowercase letter, at least 1 digit, at least 1 special character, and have a length >= 8. 

### --delete-user \[USERNAME\]
Deletes an Artifactory user. Takes one argument which is the username of the user to be deleted. For example, to delete a user `testuser123`
```
$ python jartifactory.py --delete-user testuser123
The user: 'testuser123' has been removed successfully. 
```

Utilizes Artifactory REST API function 
[Delete User](https://www.jfrog.com/confluence/display/JFROG/Artifactory+REST+API#ArtifactoryRESTAPI-DeleteUser).


### --get-storage-info
Returns storage sumamry information regarding binaries, file store, and repositories. Data is returned a json. See example for format. 
```
$ python jartifactory.py --get-storage-info 
 {'binariesCount': '0', 'binariesSize': '0 bytes', 'artifactsSize': '0 bytes', 'optimization': 'N/A', 'itemsCount': '0', 'artifactsCount': '0'}, 'fileStoreSummary': {'storageType': 's3-storage-v3-direct', 'storageDirectory': 'Artifactory Cloud'}, 'repositoriesSummaryList': [{'repoKey': 'example-repo-local', 'repoType': 'LOCAL', 'foldersCount': 0, 'filesCount': 0, 'usedSpace': '0 bytes', 'usedSpaceInBytes': 0, 'itemsCount': 0, 'packageType': 'Generic', 'projectKey': 'default', 'percentage': 'N/A'}, {'repoKey': 'auto-trashcan', 'repoType': 'NA', 'foldersCount': 0, 'filesCount': 0, 'usedSpace': '0 bytes', 'usedSpaceInBytes': 0, 'itemsCount': 0, 'packageType': 'NA', 'projectKey': 'default', 'percentage': 'N/A'}, {'repoKey': 'artifactory-build-info', 'repoType': 'LOCAL', 'foldersCount': 0, 'filesCount': 0, 'usedSpace': '0 bytes', 'usedSpaceInBytes': 0, 'itemsCount': 0, 'packageType': 'BuildInfo', 'projectKey': 'default', 'percentage': 'N/A'}, {'repoKey': 'TOTAL', 'repoType': 'NA', 'foldersCount': 0, 'filesCount': 0, 'usedSpace': '0 bytes', 'usedSpaceInBytes': 0, 'itemsCount': 0}]}
```

Utilizes Artifactory REST API function 
[Get Storage Summary Info](https://www.jfrog.com/confluence/display/JFROG/Artifactory+REST+API#ArtifactoryRESTAPI-GetStorageSummaryInfo).

### --create-repository \[REPOSITORY_TYPE\]

Creates a repository of the given type. Type options are `local`, `virtual`, and `remote`. Depending on the type of repository may prompt for additional information.
For all repository types, will prompt for the repository key to be set for the created repository. Command can also be shortened to `--create-repo`. 

#### Create local repository
Local repositories do not require any information beyond the repository key. 

Ex1. creating local repository named `local1`. 
```
$ python jartifactory.py --create-repository local
Enter repo name/key: local1
Successfuly created repository `local1`.
```
#### Create virtual repository 
Virtual repositories must have a package type specified. User will be prompted to specify the package type. 
Leave empty to create a virtual repository of the `generic` package type. 

Supported package types are: 
 - alpine
 - cargo
 - composer 
 - bower
 - chef
 - cocoapods
 - conan
 - cran
 - debian
 - docker
 - helm
 - gems
 - gitlfs
 - go
 - gradle
 - ivy
 - maven
 - npm
 - nuget
 - opkg
 - pub
 - puppet
 - pypi
 - rpm
 - sbt
 - swift
 - terraform
 - vagrant
 - yum
 - generic

Ex2. Creating a virtual repository named `virtual-docker-repo` of package type `docker`. 
```
$ python jartifactory.py --create-repo virtual
Enter repo name/key: virtual-docker-repo
Please specify package type for virtual repository (default generic): docker
Succesfully created repository 'virtual-docker-repo'.
```

#### Create remote repository 
Remote repositories must specify the url where the remote repository is located. User will be prompted for this information.
The user will also be asked whether external dependencies should be enabled, but this is only relevant for docker repositories. 

Ex3. Creating a remote repository with url `https://www.example.com` with external dependencies disabled and named `remote1`. 
```
$ python jartifactory.py --create-repository remote
Enter repo name/key: remote1
Enter url for remote repository: https://www.example.com
External dependencies enabled? Enter Y/N (Default N):
Successfully created repository 'remote1'. 
```

Utilizes Artifactory REST API function 
[Create Repository](https://www.jfrog.com/confluence/display/JFROG/Artifactory+REST+API#ArtifactoryRESTAPI-CreateRepository).

### --delete-repository \[REPOSITORY_KEY\]
Deletes the repository with the given repository key. Can be shortened to `--delete-repo`. 
```
$ python jartifactory.py --delete-repository local1
Successfully deleted repository 'local1'. 
```

Utilizes Artifactory REST API function 
[Delete Repository](https://www.jfrog.com/confluence/display/JFROG/Artifactory+REST+API#ArtifactoryRESTAPI-DeleteRepository).

## Editorial
Overall I enjoyed this project, but it ended up being a bit more time consuming than I anticipated. Although I am happy with what I
have created, there are many improvements that I can already see could be made. In this editorial I will discuss a bit about why I made
some of the design decisions I made that may not be as obvious, things I would do differently if I had the chance, and some of the 
challenges of I faced during the project creation. 

### argparse
I decided to use the default python package `argparse` in an effort to simplify the effort of parsing arguments passed to my utility. This
has limitations in terms of the flexibility of what kinds of information can be obtained from the user directly via `argparse` and results 
in vaguely repetitive commands needing to be entered when compared to a long-running Python script that allows for multiple interactions 
one at a time. Given the nature of this project being a toy project, I felt it was worth using `argparse` to simplify argument handling. 
Additionally, this type of utility is a bit simpler for one-off commands only used every once in a while rather than long sessions with 
multiple interactions made. I envisioned the tool as more akin to a standard linux utility than a utility with a full interface such as 
what one might use to run SQL commands on a database. No need to "enter" and "exit" the utility on each use. 

### Authentication
It was important that the tool did not require logging in for every action. In order to accomplish this, I initially chose to use tokens with
short expiration times (24 hours) that would be stored in a `.env` file. As I continued work on the project, I found that the token did not 
allow me to interact with certain API endpoints. Specifically, it seemed any endpoint requiring admin privileges gave me 403 forbidden responses
when using the token. I then switched to using an API key rather than a token. This key is also stored in the `.env`. The `.env` solution is 
almost certainly a fairly insecure one, but I'm not actually sure what the best method for storing senstive information like tokens would be. 
I'm of the opinion that it was possibly acceptable when using a temporary access method such as a token, but for a long-term access method like
an API key, a better solution is necessary. Still, for the purpose of this toy project, a simple solution that automates things for the user is
desirable, and security is of little importance. I ultimately left both authentication methods in the tool. I needed to use the API key, but I 
was happy with what I had done with the token, and didn't want to remove. In a real project, having a consistent authentication method is more 
desirable, but for demonstration purposes I left the two in since I went to the trouble of implementing both. I'm very interested to learn how 
tools like the `aws cli` manage temporary login access tokens, as that knowledge would have really helped me here. 

### Extensibility 
In retrospect, there are some design changes I would like to have made. The biggest change would be to separate taking user input and making API 
requests. I would like to write a driver class (perhaps in a separate python module) that exposes methods for reaching all the API endpoints I 
needed for the project. Then the main `jartifactory.py` file would simply instantiate a driver and make calls via the driver. This would really 
clean up the code and the driver would have a lot of reusability for future functions. 

Overall the design the code I wrote is very poor in terms of reusability of code. I would like to have written more function. The driver described 
above would help with this greatly. I noticed many times I had to repeat lines of code related to checking for the existance of the API key and 
sending an appropriate error message if the key was missing. I probably could have avoided this. 

At the very least, the design is simple with argparse and a long series of elif blocks. This makes it simple enough to add more features, though
it is quite messy. I would prefer the elif blocks to call functions rather than contain long code segments. This would clear up the elif chain a 
lot and be much prettier. 

To my credit, I did include the option of changing the default host which would potentially be important in a real project. I also think adding 
a --host argument would be a good add in a real release of a tool like this. 

### Challenges
I did have a bit of a lack of domain knowledge when it comes to exactly how Artifactory is used. This made it difficult for me to anticipate the 
needs of a potential user. I have limtied experience with Artifactory itself. This is especially evident when it comes to the `--create-repo` 
feature of my application. A repository config has numerous elements and I was unsure as to which config elements would be especially important.
I configured the tool to take only the minimum required elements. Given more time it may have been very useful to allow this feature to take a 
user-specified config file when creating the repository. 

When it came to displaying the storage info, my lack of domain knowledge (and time) again caused problems. There is a good bit of info in the 
json response from the REST API, and I wasn't sure which info would be the most important to share with the user. It would be nice to pull the 
crucial details, format it nicely, and then display that information. Spitting out a json in one line isn't useful for much other than writing 
that json somewhere else for further processing. I seriously considered just removing this feature entirely given how ugly the final product 
ended up being, but I figured that in the end *something* is better than nothing. 

### Final Thoughts
When I learned the details of the challenge I was pretty pleased as I've done work like this many times before so I expected it to be a breeze. 
It was a bit more difficult than I thought and I definitely made some mistakes along the way. In my efforts to make something that could stand 
up to harsh critique, I realized it seems there is always more to improve upon. In the short time frame, sometimes one just has to cut losses 
and accept what is. I think for a toy project, I've done something I can be proud of. Although maybe I put in more time than it was worth :sweat_smile:. 
No matter how things work out as far as my interview process is concerned, I am glad to have had the opportunity to do this work. Thank you Jfrog!