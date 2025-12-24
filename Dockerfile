# Use the official Node.js image
FROM node:18
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install --production
COPY . /app
RUN npm run build || true
CMD ["node", "dist/server.js"]
