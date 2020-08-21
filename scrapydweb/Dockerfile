FROM python:3.7
ADD . /code
WORKDIR /code
RUN pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
CMD scrapydweb