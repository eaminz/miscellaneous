#!/bin/bash
# This script dumps all the objects in a given S3 bucket

if [ -z $1 ] || [ -z $2 ]
then
	echo "Missing arguments, expected syntax:"
	echo "./dumpBucket.sh <bucket URL> <filename prefix>"
	exit 1
fi

listBucketResult=`curl -s -S -XGET $1`
isTruncated=`echo $listBucketResult | sed 's/.*<IsTruncated>\(.*\)<\/IsTruncated>.*/\1/'`
fileNum=1
echo $listBucketResult > $2$fileNum
echo "File $2$fileNum written."
while [[ "$isTruncated" == "true" ]]; do
	nextMarker=`echo $listBucketResult | sed 's/.*<NextMarker>\(.*\)<\/NextMarker>.*/\1/'`
	listBucketResult=`curl -s -S -XGET $1"?marker="$nextMarker`
	isTruncated=`echo $listBucketResult | sed 's/.*<IsTruncated>\(.*\)<\/IsTruncated>.*/\1/'`
	fileNum=$((fileNum+1))
	echo $listBucketResult > $2$fileNum
	echo "File $2$fileNum written."
done
echo "Bucket $1 dumping completed."
