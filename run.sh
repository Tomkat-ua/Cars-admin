service=Cars-admin
ver=`cat version`
container=$service
img=tomkat/cars-admin:$ver

docker container stop $container
docker container rm $container 

docker run -dt \
    -p 8086:3001 \
    --name=$container \
    --env-file .env \
    -e TZ=Europe/Kyiv \
    -e APP_VERSION=$ver \
    --restart=always \

    $img
