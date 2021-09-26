FROM python:alpine
LABEL Author ToolmanP
EXPOSE 443
EXPOSE 80
EXPOSE 8080
RUN echo "http://mirrors.ustc.edu.cn/alpine/v3.5/main" >> /etc/apk/repositories
RUN apk add --no-cache libxml2  gcc  g++ libxslt-dev 
RUN pip --no-cache-dir install --upgrade pip
RUN pip --no-cache-dir install beautifulsoup4 pysjtu
COPY ./course_plus_data_fetcher /app/course_plus_data_fetcher
COPY ./json /app/json
WORKDIR /app
CMD python -m course_plus_data_fetcher