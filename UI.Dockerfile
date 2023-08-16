# Use the official Node.js image as the base image
FROM node:14 AS build

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the app's source code
COPY ./qa-app .

# Build the app
RUN npm run build

# Use a smaller image for production
FROM nginx:alpine

# Copy the built app from the previous stage
COPY --from=build /app/build /usr/share/nginx/html

# Expose port 80
EXPOSE 80


# Start the nginx server
CMD ["nginx", "-g", "daemon off;"]