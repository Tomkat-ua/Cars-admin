service=Cars-admin
container=$service
img=tomkat/cars-admin:1

docker container stop $container
docker container rm $container 

docker run -dt \
    -p 8086:3001 \
    -e URL_TO_CLOUD=http://192.168.10.9:3000/run \
    -e DB_HOST=192.168.10.5 \
    -e DB_PATH=cars_dev \
    -e DB_USER=MONITOR \
    -e DB_PASSWORD=inwino \
    --name=$container \
    --env-file .env \
    -e TZ=Europe/Kyiv \
    --restart=always \
    $img
