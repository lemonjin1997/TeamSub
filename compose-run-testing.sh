docker network create selenium_network || echo selenium_network exists

docker-compose -f docker-compose.yml -f docker-compose.test.yml -f docker-compose.selenium.yml down

docker-compose -f docker-compose.yml -f docker-compose.test.yml -f docker-compose.selenium.yml up --build -d 

docker image prune -a -f