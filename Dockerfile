FROM amazonlinux:2017.03

# Install jq, needed to parse the SQS messages
RUN yum install -y jq

ENV AWS_DEFAULT_REGION us-east-1

COPY doer.sh /usr/local/bin/doer.sh
CMD /usr/local/bin/doer.sh