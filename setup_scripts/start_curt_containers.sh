source /root/.bashrc
cd ${CURT_PATH}
rm -f .env
touch .env
echo "USERNAME=$USER" >> .env
docker-compose up --force-recreate
