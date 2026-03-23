FROM node:22-alpine3.21
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 1111
CMD ["npm", "run", "dev"]
