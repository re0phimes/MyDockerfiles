定义了远程访问百度scrapydweb的密码
```
('','','180.76.153.244','6800','baidu_server')

USERNAME = 'phi'
PASSWORD = 'fourspeedforward'
```

```
 docker run -itd --name scrapydweb_phi -p 5000:5000 -v scrapydweb_data:/code phimecho/scrapydweb
```