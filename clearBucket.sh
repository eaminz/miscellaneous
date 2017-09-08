#!/usr/bin/python
# This script clears all the objects in a given S3 bucket

if [ -z $1 ]
then
	echo "Missing bucket URL, expected syntax:"
	echo "./clearBucket.sh <bucket URL>"
	exit 1
fi

listBucketResult=`curl -s -S -XGET $1`
while [[ "$listBucketResult" == *"<Key>"* ]]; do
	while [[ "$listBucketResult" == *"<Key>"* ]]; do
		key=`echo $listBucketResult | sed 's/.*<Key>\(.*\)<\/Key>.*/\1/'`
		curl -s -S -XDELETE $1"/"$key
#		echo "Deleted "$key
		listBucketResult="${listBucketResult/<Key>$key<\/Key>/}"
	done
	listBucketResult=`curl -s -S -XGET $1`
done
echo "Bucket $1 cleared."
