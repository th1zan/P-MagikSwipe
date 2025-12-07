FROM nginx:alpine
COPY default.conf /etc/nginx/conf.d/default.conf
# Don't copy HTML files - they will be mounted via volume for hot reload
EXPOSE 80