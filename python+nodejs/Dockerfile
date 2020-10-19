FROM python:3.7
ADD node-v14.11.0-linux-x64.tar.xz /usr/local
ENV PATH=$PATH:/usr/local/node-v14.11.0-linux-x64.tar.xz/bin
ADD . /code
WORKDIR /code
RUN pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple &&\
    ln -s /usr/local/node-v14.11.0-linux-x64/bin/node /usr/bin/node
CMD python baidu_index.py

