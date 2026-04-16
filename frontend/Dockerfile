FROM node:22-bullseye
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 1111
CMD ["npm", "run", "dev"]
