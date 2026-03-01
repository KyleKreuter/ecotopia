#!/bin/bash
export HF_TOKEN=$(cat /root/.cache/huggingface/token)
export HUGGINGFACE_API_KEY=$HF_TOKEN
export EXTRACTION_ENDPOINT=https://ay7cysiozwv09su9.us-east-1.aws.endpoints.huggingface.cloud
export CITIZEN_ENDPOINT=https://ay7cysiozwv09su9.us-east-1.aws.endpoints.huggingface.cloud
cd /root/clawd/ecotopia/backend
./mvnw spring-boot:run -q &
JAVA_PID=$!
trap '' HUP
wait $JAVA_PID
