#coding: utf-8
from scrapyd_api import ScrapydAPI
import time

import sys
from importlib import reload
reload(sys)
sys.setdefaultencoding('utf-8')
import gevent
#由于切换是在IO操作时自动完成，所以gevent需要修改Python自带的一些标准库，这一过程在启动时通过monkey patch完成：
from gevent import monkey; monkey.patch_all()

def schedule():
    scrapyd = ScrapydAPI("http://localhost:6800")
    projects = scrapyd.list_projects()
    print( projects)

    list_start = []
    list_end = []
    while(True):
        print ('start')
        jobids = {}

        for project in projects:
            list_start.append(gevent.spawn(start, scrapyd, project))
        donelist = gevent.joinall(list_start)

        [jobids.update(i.value) for i in donelist]
        print ('wait')
        time.sleep(120)
        print ('cancal')
        for project,job in jobids.items():
            list_end.append(gevent.spawn(end, scrapyd, project, job))
        time.sleep(300)
        print ('restart')


def start(scrapyd, project):
    print (project+"爬虫开始运行")
    jobid = scrapyd.schedule(project=project, spider=project+'Spider')
    return {project:jobid}


def end(scrapyd,project,job):
    print (project + "爬虫关闭")
    scrapyd.cancel(project=project, job=job)


def debug():
    scrapyd = ScrapydAPI("http://localhost:6800")
    job = scrapyd.schedule(project='sougouHotList', spider= 'sougouHotListSpider')
    #job = scrapyd.schedule(project='baiduHotList', spider='baiduHotListSpider')
    time.sleep(120)
    print ('开始关闭爬虫')
    scrapyd.cancel(project='sougouHotList', job=job)
    time.sleep(300)
    print ('关闭爬虫')


if __name__ == '__main__':
    schedule()
    #debug()
    '''scrapyd = ScrapydAPI("http://localhost:6800")
    print scrapyd.cancel(project='baiduNews', job='a6b4fc9c243811e98e4a309c23cf3a0b')
    '''