#!/bin/bash
# This script creates the root user in Accounts table for initial login of RIO UI.
# Make sure to install Bash 3+ and MySQL CLI.

# help session
function help () {
	echo "./createRoot.sh -m metadata_address -e root_email -p root_password"
	exit 1
}

# get arguments from command line
while getopts "hm:e:p:" FLAG; do
	case $FLAG in
		h)
			help
			;;
		m)
			metadata_address=$OPTARG
			echo "metadata_address: $OPTARG"
			;;
		e)
			root_email=$OPTARG
			echo "root_email: $OPTARG"
			;;
		p)
			root_password=$OPTARG
			echo "root_password: $OPTARG"
			;;
		\?)
			echo "Invalid option: -$OPTARG"
			exit 1
			;;
		:)
			echo "Option -$OPTARG requires an argument."
			exit 1
			;;
	esac
done

# validate arguments
if [ -z $metadata_address ]
then
	echo "Missing metadata_address, expected syntax:"
	help
fi

if [ -z $root_email ]
then
	echo "Missing root_email, expected syntax:"
	help
fi

email_regex="^[a-z0-9!#\$%&'*+/=?^_\`{|}~-]+(\.[a-z0-9!#$%&'*+/=?^_\`{|}~-]+)*@([a-z0-9]([a-z0-9-]*[a-z0-9])?\.)+[a-z0-9]([a-z0-9-]*[a-z0-9])?\$"
if [[ ! ($root_email =~ $email_regex) ]]
then
	echo "Invalid email address."
	exit 1
fi

if [ -z $root_password ]
then
	echo "Missing root_password, expected syntax:"
	help
fi

password_regex1="^.{6,20}$"
password_regex2=".*[A-Z].*"
password_regex3=".*[a-z].*"
if [[ ! ($root_password =~ $password_regex1 && $root_password =~ $password_regex2 && $root_password =~ $password_regex3) ]]
then
	echo "Password must be 6-20 characters long and containing uppercase & lowercase."
	exit 1
fi

# generate random salt
salt=`cat /dev/urandom | tr -dc 'a-zA-Z@#$' | fold -w 10 | head -n 1`

# passwordDigest = md5(password + salt + md5(password))
intermediateDigest=`echo -n $root_password | md5sum | awk -F " " '{print $1}'`
passwordDigest=`echo -n $root_password$salt$intermediateDigest | md5sum | awk -F " " '{print $1}'`

# get current time in UTC
now=`date -u +"%Y-%m-%d %H:%M:%S"`

# insert root entry into Accounts table
# specify ID although it's AUTO_INCREMENT, so as to avoid creating root twice. root ID must be 1
if mysql --connect-timeout 5 -h $metadata_address -P 3306 -u root -e  "INSERT INTO Accounts (UserName, Email, FullName, PasswordDigest, Salt, Role, Status, Created, LastModified) VALUES ('root', '$root_email', 'Root', '$passwordDigest', '$salt', 2, 1, '$now', '$now');" riodev
then
	echo "Success! Inserted root entry into Accounts table."
fi
