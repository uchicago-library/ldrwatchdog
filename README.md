# Setup Instructions

1. create a virtual environment for the program
2. activate the virtual environment
3. cd into the ldrwatchdog directory
4. run python setup.py install
5. add the bin directory for the virtual environment to your PATH
6. run one of two scripts

```
fixitycheck /home/test/livePremis 1000
```

This will run a fixity check on 1000 files with PREMIS records stored in /home/test/livePremis.

```
postarchive /home/test/longTermStorage /home/test/livePremis
```

This will run postarchive which will find all new premis records in /home/test/longTermStorage and copy them into /home/test/livePremis.

```
updatecollections /home/test/apistorage/records collection
```

This will run updatecollections which will find all accession hierarchical records in /home/test/apistorage and create new collection records from the collection title in accession record that are not already stored in collection hierarchical records.
