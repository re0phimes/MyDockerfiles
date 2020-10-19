# -*- coding: utf-8 -*-  

import requests, json, datetime
from datetime import timedelta
import execjs
import pymongo
from pymongo.errors import DuplicateKeyError
from apscheduler.schedulers.blocking import BlockingScheduler
from settings import *
import logging


########## set up logging config###################
logger = logging.getLogger('hotrank_logger')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')
# 创建FileHandler对象
fh = logging.FileHandler('baidu_index_errors.log')
fh.setLevel(logging.WARNING)
fh.setFormatter(formatter)
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
sh.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(sh)




headers = {
    'Cookie': 'BIDUPSID=A064EBA49CA64964F88B52743806B495; PSTM=1596525581; BAIDUID=A064EBA49CA649644F4121BC8279A589:FG=1; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; BDUSS=Jqd0ZYV0U4cDVMaC1QN1hLYTMzNzVxMkNpT3BmcXZtLTNibEFqbkdUYnluMWhmRVFBQUFBJCQAAAAAAAAAAAEAAAAT0AIIw9XNxb79AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPISMV~yEjFfTG; CHKFORREG=596afd874a8833f0107889aefa40b953; bdindexid=td46en946rshbn1vlmbtjp3f61; Hm_lvt_d101ea4d2a5c67dab98251f0b5de24dc=1597043125,1597112693; delPer=0; PSINO=1; H_PS_PSSID=32288_1462_32438_32380_32357_32327_31253_32350_32046_32395_32407_32446_32116_31322_32496_32481; Hm_lpvt_d101ea4d2a5c67dab98251f0b5de24dc=1597115336; RT="sl=c&ss=kdpc6u90&tt=21dh&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf&z=1&dm=baidu.com&si=3vz00eht9ii&ld=11ngf"'
}



data_url_temp = 'http://index.baidu.com/api/SearchApi/index?area=0&word=[[%7B%22name%22:%22{}%22,%22wordType%22:1%7D]]&startDate={}&endDate={}' #dateformat as 2020-08-01

inform_url_temp = 'http://index.baidu.com/api/FeedSearchApi/getFeedIndex?area=0&word=[[%7B%22name%22:%22{}%22,%22wordType%22:1%7D]]&startDate={}&endDate={}' 


password_url = 'http://index.baidu.com/Interface/ptbk?uniqid={}'


# decodejs
baidu_decode = execjs.compile('''
   function decrypt(password, data){
    let arr = password.split('');
    let dataArr = data.split('');
    let objPass = {};
    let notInNames = [];
    for (let i = 0; i < arr.length / 2; i++) {
        objPass[arr[i]] = arr[arr.length / 2 + i];
    }
    // 数据解密转换
    for (let i = 0; i < data.length; i++) {
        notInNames.push(objPass[dataArr[i]]);
    }
    // alert(notInNames.join(''));
    return notInNames.join('');
    } 
'''
)

# -------------环境变量--------------

MONGO_HOST = '127.0.0.1'
MONGO_PORT = 27000
myclient = pymongo.MongoClient(REMOTE_MONGO_HOST,REMOTE_MONGO_PORT)
myclient.admin.authenticate('beihai','yaoduoxiang')
mydb= myclient['index']
# -------------计数统计--------------
days = datetime.datetime.now()
count = 0



# def get_list(search_word, startdate, enddata):





def getBaiduIndex(search_word, startdate, enddata):
    '''
    获取百度指数
    :param search_word: 字符串
    :param startdate: 2020-08-01
    :param enddata: 2020-09-01
    :return:
    '''
    data_url = data_url_temp.format(search_word,startdate,enddata)
    # print(url)
    data_response = requests.get(data_url, headers=headers)
    raw_data = json.loads(data_response.text)

    # ---------获取趋势信息----------------
    final_trends = {}
    if raw_data['status'] != 0:
        logger.error("status code error, status code" + raw_data['status'])
    else:
        data = raw_data['data']['userIndexes'][0]
        uniqid = raw_data['data']['uniqid']
        pwd_resposne = requests.get(password_url.format(uniqid),headers=headers)
        decode_pwd = json.loads(pwd_resposne.text)['data']
        # ----------- time_list---------
        enddate = data['all']['endDate']
        startdate = data['all']['startDate']
        et = str_to_date(enddate)
        st = str_to_date(startdate)
        final_trends['dtlist'] = get_datelist(st,et)
        # ---------starting decode data
        baidu_index = {}
        alldata = data['all']['data']
        pcdata = data['pc']['data']
        wisedata = data['wise']['data']
        # ------
        raw_all_trend = baidu_decode.call('decrypt', decode_pwd, alldata)
        final_trends['all_trend_list'] = raw_all_trend.split(',')
        # ------
        raw_pc_trend = baidu_decode.call('decrypt', decode_pwd, pcdata)
        final_trends['pc_trend_list'] = raw_pc_trend.split(',')
        # ------
        raw_wise_trend = baidu_decode.call('decrypt', decode_pwd, wisedata)
        final_trends['wise_trend_list'] = raw_wise_trend.split(',')
    #------获取资讯数据信息----------
    inform_url = inform_url_temp.format(search_word,startdate,enddata)
    # print(url)
    inform_data_response = requests.get(inform_url, headers=headers)
    inform_raw_data = json.loads(inform_data_response.text)
    if inform_raw_data['status'] != 0:
        logger.error('status error')
    else:
        inform_data = inform_raw_data['data']['index'][0]['data']
        inform_uniqid = inform_raw_data['data']['uniqid']
        inform_pwd_resposne = requests.get(password_url.format(inform_uniqid),headers=headers)
        inform_decode_pwd = json.loads(inform_pwd_resposne.text)['data']
        raw_inform_trend = baidu_decode.call('decrypt', inform_decode_pwd, inform_data)
        final_trends['inform_trend_list'] = raw_inform_trend.split(',')
        # print(final_trends)
    #---------------save 
    for i in range(len(final_trends['dtlist'])):
        try:
            mydb[search_word].insert_one({"_id":final_trends['dtlist'][i], "all_trend":final_trends['all_trend_list'][i], "pc_trend":final_trends['pc_trend_list'][i],"wise_trend":final_trends['wise_trend_list'][i],"inform_trend":final_trends['inform_trend_list'][i]})
        except DuplicateKeyError as e:
            pass
    return final_trends

def str_to_date(dt):
    '''
    转换日志格式，用于分析方法中，
    '''
    real_dt = datetime.datetime.strptime(dt, "%Y-%m-%d")
    return real_dt


def get_datelist(st, et):
    '''
    给定一个起始和结束时间，用于
    '''
    dtlist = []
    while st <= et:
        dtlist.append(st)
        st += datetime.timedelta(days=+1)
    dtlist = list(map(lambda dt: datetime.datetime.strftime(dt,'%Y-%m-%d'),dtlist))
    # print(dtlist)
    return dtlist


def daily_update_func():
    today = datetime.datetime.strftime(datetime.date.today(),'%Y-%m-%d')
    temp_yesterday = datetime.date.today() + timedelta(days=-1)
    yesterday = datetime.datetime.strftime(temp_yesterday,'%Y-%m-%d')
    for search_word in search_list:
        searchdata = getBaiduIndex(search_word, yesterday, today)
    count += 1
    logging.info(today + " 数据已下载，明日同时刻再次运行。")
#注意第一次爬取需要使用一个长时间跨度，从此之后每次增加一天。


# set up scheduler
scheduler = BlockingScheduler()

# today = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d')
today = datetime.datetime.strftime(datetime.date.today(),'%Y-%m-%d')
temp_yesterday = datetime.date.today() + timedelta(days=-1)
yesterday = datetime.datetime.strftime(temp_yesterday,'%Y-%m-%d')
for search_word in search_list: 
    baidu_data = getBaiduIndex(search_word, '2020-02-01', today) # 第一次
    logger.info('data of search_word'.format(search_word))
    print('{} baidu index data of {} has downloaded'.format(today, search_word))
    # logger.info('已运行{}次'.format(count))
scheduler.add_job(daily_update_func, 'interval', hours=1)
logger.info('开始定期下载')
scheduler.start()
# baidu_data = getBaiduIndex('北京疫情', yesterday, today)
# save_to_mongo(baidu_data)



