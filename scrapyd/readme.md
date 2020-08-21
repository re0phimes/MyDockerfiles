使用docker run scrayd镜像后，会产生一个twistd的文件。导致stop container再运行。会由于这个文件报错。所以必须删除掉。所以必须使用-v 把内部路径映射到宿主机上。方便删除twisted文件

```
docker run -itd --name scrapyd_phi -p 6800:6800 -v scrapyd_data:/code phimecho/scrapyd
```