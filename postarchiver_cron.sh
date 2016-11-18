
date=`date`
you = "me@test.com"

python live_premis_addition.py /home/test/longTermStorage /home/test/livePremis 1> /tmp/LDR_NEW_LIVE_PREMIS_ADDONS

num_new_premis = `cat /tmp/LDR_LIVE_PREMIS_ADDITIONS | wc -l`

echo "On $date, there were $num_new_premis premis record(s) added to the livePremis for the digital repository" > /tmp/LDR_NEWPREMIS_MESSAGE

mail -s "ldr new premis added" $mail_to_address < /tmp/LDR_NEWPREMIS_MESSAGE

rm /tmp/LDR_NEWPREMIS_MESSAGE

