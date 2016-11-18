# About the Watchdog

This is a set of tools that are intended to run as cronjobs on a server hosting a digital repository conforming to the stickshift repository system. 

It uses the livePremis environment to do the following

1. perform regular fixity checks
2. add new premis records to the livePremis environment when new material is added to longTermStorage

Step 1 can be run with the following command

python live_premis_addition.py /home/test/longTermStorage /home/test/livePremis 

This will find all premis records in /home/test/longTermStorage that are not in /home/test/livePremis and copy the files into /home/test/livePremis while preserving the full file relative to /home/test/longTermStorage/. 


Step 2 can be run

python corruption_check.py /home/test/livePremis 10

This will read 10 records in /home/test/livePremis and check the stored contentLocation to verify that the md5 message digest of the file matches the md5 stored in the premis record.

or 

python corruption_check.py -b 1000000 10


This will read 10 records or 1000000 blocks read (whichever limit is reached first) in /home/test/livePremis and check the stored contentLocation to verify that the md5 message digest of the file matches the md5 stored in the premis record.

