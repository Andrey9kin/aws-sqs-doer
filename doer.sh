while [ /bin/true ]; do
  msg=$( \
    aws sqs receive-message \
     --queue-url ${IN_QUEUE_URL} \
     --wait-time-seconds 20 \
     --max-number-of-messages 1 \
     --output text \
     --query Messages[0].[Body,ReceiptHandle]
  )

  if [ -z "${msg}" -o "${msg}" = "None" ]; then
      echo "No messages left. Retry."
  else
      log=$(mktemp)
      eval "${msg}" | tee -a ${log} 
      receipt_handle=$(echo "${msg}" | cut -f2 --)
      aws sqs delete-message \
       --queue-url ${IN_QUEUE_URL} \
       --receipt-handle ${receipt_handle}
      # Send last 255000 bytes since sqs message limit is 256 kb
      aws sqs send-message \
	--queue-url ${OUT_QUEUE_URL} \
	--message-body $(cat ${log} | tail -c 255000 )
  fi
done
