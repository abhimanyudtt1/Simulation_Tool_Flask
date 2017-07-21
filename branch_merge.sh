#!/bin/bash

echo $1
#selecting the repo
if [ $1 == DriverBackend ]
then
    cd /usr/local/projects/DriverBackend
elif [ $1 == ShuttlAdmin ]
then
    cd /usr/local/projects/ShuttlAdmin
elif [ $1 == VMS ]
then
   cd /usr/local/projects/VMS
elif [ $1 == RMS ]
then
   cd /usr/local/projects/RMS
else
   cd /usr/local/projects/Driver-java
fi

# going to master_rlease branch and updating it
git checkout master_release;git pull origin master_release
MASTER_RELEASE_CHECKOUT=$?

# going to master branch, merging master_release and pushing it
echo $MASTER_RELEASE_CHECKOUT
if [ $MASTER_RELEASE_CHECKOUT -eq 0 ]
then
   git checkout master;git merge master_release;git push origin master
   MASTER_CHECKOUT=$?
else
   echo "master_release pull failed" 
   MASTER_CHECKOUT=$?
fi

# going to master_release, merge dev branch and pushing it
echo $MASTER_CHECKOUT
if [ $MASTER_CHECKOUT -eq 0 ]
then
   git checkout master_release;git pull origin $2;git push origin master_release
   MASTER_RELEASE_PUSH=$?
else
   echo "master_release merge with master failed"
   MASTER_RELEASE_PUSH=$?
fi

echo $MASTER_RELEASE_PUSH
if [ $MASTER_RELEASE_PUSH -eq 0 ]
then
   echo "master and master_release merged and pushed"
else
   echo "merge of $1 with master_release failed"
fi
