FROM ruby:alpine3.13
WORKDIR /app/
ADD ./http_server/ /app/
RUN apk update && apk add curl && chmod +x /app/http_server.rb && adduser -S ruby
USER ruby
CMD ["ruby", "/app/http_server.rb"]
