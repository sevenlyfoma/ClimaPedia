docker build -t my-frontend-app .
docker run -d -p 8080:80 --name frontend-container my-frontend-app