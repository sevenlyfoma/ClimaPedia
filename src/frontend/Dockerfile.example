# Stage 1: Build the assets
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Serve them with Nginx
FROM nginx:stable-alpine
# Copy built files from Stage 1 to Nginx's HTML folder
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]