
run_date=`date`
num_files = 1000
mail_to_address = "me@test.com"

python corruption_check $num_files 2>/tmp/LDR_CORRUPTION_ERRORS

echo "On $run_date a fixity check was performed on $num_files in the repository and the following were found corrupted. If there are no files listed that means no files were found to be corrupt." >> /tmp/LDR_CORRUPTION_MESSAGE

cat /tmp/LDR_CORRUPTION_ERRORS >> /tmp/LDR_CORRUPTION_MESSAGE

mail -s "ldr file corruption test" $mail_to_address < /tmp/LDR_CORRUPTION_MESSAGE

rm /tmp/LDR_CORRUPTION_ERRORS
rm /tmp/LDR_CORRUPTION_MESSAGE

