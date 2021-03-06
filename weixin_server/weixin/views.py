# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.views.generic import  ListView
from django.views.decorators.csrf import csrf_exempt
from xml.etree import ElementTree
from time import time
import httplib, urllib ,urllib2
import json
import hashlib
import weixin_server.settings as SETTING
from weixin.models import *

class BaseMixin(object):
    def get_context_data(self, *args, **kwargs):
        context = super(BaseMixin, self).get_context_data(**kwargs)
        return context

class IndexView(BaseMixin, ListView):
    template_name = 'pc.html'

    def get_context_data(self, **kwargs):
        return super(IndexView, self).get_context_data(**kwargs)
    def get_queryset(self):
        pass
    def get(self, request, *args, **kwargs):
        print request,"get"
        return super(IndexView, self).get(request, *args, **kwargs)
        # response=HttpResponse(CheckSignature(request))
        # return response


    def post(self, request, *args, **kwargs):
        print request,"post"
        reply_msg = AutoReplyService(request)
        return reply_msg
        # mydict = {'matrix':""}
        # return HttpResponse(
        #     json.dumps(mydict),
        #     content_type="application/json"
        # )
        # return 'post'

@csrf_exempt
def Index(request):
    print "get Message ",request.method
    if request.method=='GET':
        response=HttpResponse(CheckSignature(request))
        return response

    elif request.method=='POST':
        print request,"post"
        # service
        reply_msg = AutoReplyService(request)
        return reply_msg
    else:
        return HttpResponse('Hello World')

def CheckSignature(request):
    signature=request.GET.get('signature',None)
    timestamp=request.GET.get('timestamp',None)
    nonce=request.GET.get('nonce',None)
    echostr=request.GET.get('echostr',None)

    token='tan'

    tmplist=[token,timestamp,nonce]
    tmplist.sort()
    tmpstr="%s%s%s"%tuple(tmplist)
    tmpstr=hashlib.sha1(tmpstr).hexdigest()
    if tmpstr==signature:
        return echostr
    else:
        return None

#检测MsgId是否重排
def CheckMsgID(MsgId):
    _msgid = MsgId
    if Message.objects.filter(msg_id = _msgid).exists():
        return False
    else:
        _message = Message(msg_id = _msgid)
        _message.save()
    return True

def AutoReplyService(request):
    print "Message In FengXiong "
    # change to etree method
    message_str =  request.read()
    print 'in service',message_str
    root = ElementTree.fromstring(message_str)
    print 11
    form_user_name = root.find('FromUserName').text
    to_user_name = root.find('ToUserName').text
    # message_type = root.find('MsgType').text
    message_type = root.find('MsgType').text
    MsgId = root.find('MsgId').text

    if CheckMsgID(MsgId) is False:
        return ''


    context = {'to_user_name':form_user_name,'from_user_name':to_user_name}


    if message_type == 'text':
        text_content = root.find('Content').text
        print message_type
        text_img_xml = '''
            <xml>
            <ToUserName><![CDATA[%s]]></ToUserName>
            <FromUserName><![CDATA[%s]]></FromUserName>
            <CreateTime>%s</CreateTime>
            <MsgType><![CDATA[%s]]></MsgType>

            <Content><![CDATA[%s]]></Content>
            </xml>
        '''
        message_type = 'text'
        create_time = int(time())
        if len(text_content) < 4:
            _content = "'" + text_content[:3] + "...'" + u"的信息接收啦~~还想要长一点的^_^"
        else:
            _content = "'" + text_content[:3] + "...'" + u"的idear已接收，丰兄正在努力整理"
        text_img = {
            'to_user_name':context['to_user_name'],
            'from_user_name':context['from_user_name'],
            'create_time':create_time,
            'message_type':message_type,

            #字符画
            "content": _content
        }
        text_reply_xml = text_img_xml % (
            text_img['to_user_name'],text_img['from_user_name'],text_img['create_time'],text_img['message_type']
            ,text_img['content'] #返回文字

        )
        response = HttpResponse(text_reply_xml,content_type='application/xml; charset=utf-8')
        return response

    if message_type == 'event':

        print message_type
        text_img_xml = '''
            <xml>
            <ToUserName><![CDATA[%s]]></ToUserName>
            <FromUserName><![CDATA[%s]]></FromUserName>
            <CreateTime>%s</CreateTime>
            <MsgType><![CDATA[%s]]></MsgType>

            <ArticleCount>1</ArticleCount>
            <Articles>

            <item>
            <Title><![CDATA[%s]]></Title>
            <Description><![CDATA[%s]]></Description>
            <PicUrl><![CDATA[%s]]></PicUrl>
            <Url><![CDATA[%s]]></Url>
            </item>

            </Articles>
            </xml>
        '''

        message_type = 'news'
        create_time = int(time())
        text_img = {
            'to_user_name':context['to_user_name'],
            'from_user_name':context['from_user_name'],
            'create_time':create_time,
            'message_type':message_type,

            #字符画
            'title_str':u'听说你想学画画，不懂从哪里开始?',
            'description':u'召唤·丰兄',
            'pic_url':'http://7xsark.com1.z0.glb.clouddn.com/img/20160821145626.png',
            'url':'http://mp.weixin.qq.com/s?__biz=MzIxMzQwOTIzOA==&mid=2247483759&idx=1&sn=0cfa42b744697ffa37b611ca91f4339c#rd',


        }
        text_reply_xml = text_img_xml % (
            text_img['to_user_name'],text_img['from_user_name'],text_img['create_time'],text_img['message_type']
            ,text_img['title_str'],text_img['description'],text_img['pic_url'],text_img['url'] #显示单页字符画

        )


        response = HttpResponse(text_reply_xml,content_type='application/xml; charset=utf-8')

        return response



    if message_type == 'image':
        image_url = root.find('PicUrl').text

        # text_xml = '''
        #     <xml>
        #     <ToUserName><![CDATA[%s]]></ToUserName>
        #     <FromUserName><![CDATA[%s]]></FromUserName>
        #     <CreateTime>%s</CreateTime>
        #     <MsgType><![CDATA[%s]]></MsgType>
        #     <Content><![CDATA[%s]]></Content>
        #     </xml>
        # '''

        text_img_xml = '''
            <xml>
            <ToUserName><![CDATA[%s]]></ToUserName>
            <FromUserName><![CDATA[%s]]></FromUserName>
            <CreateTime>%s</CreateTime>
            <MsgType><![CDATA[%s]]></MsgType>

            <ArticleCount>2</ArticleCount>
            <Articles>

            <item>
            <Title><![CDATA[%s]]></Title>
            <Description><![CDATA[description1]]></Description>
            <PicUrl><![CDATA[%s]]></PicUrl>
            <Url><![CDATA[%s]]></Url>
            </item>

            <item>
            <Title><![CDATA[%s]]></Title>
            <Description></Description>
            <PicUrl></PicUrl>
            <Url><![CDATA[%s]]></Url>
            </item>



            </Articles>
            </xml>
        '''
          # <item>
          #   <Title><![CDATA[%s]]></Title>
          #   <Description></Description>
          #   <PicUrl></PicUrl>
          #   <Url><![CDATA[%s]]></Url>
          #   </item>
          #
          #   <item>
          #   <Title><![CDATA[%s]]></Title>
          #   <Description></Description>
          #   <PicUrl></PicUrl>
          #   <Url><![CDATA[%s]]></Url>
          #   </item>

        message_type = 'news'

        # url process img to str
        #Post 获取 json 对象
        def PostServer(url,data):
            req = urllib2.Request(url)
            data = urllib.urlencode(data)
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
            response = opener.open(req, data)
            res = response.read()
            obj = json.loads(res)
            return obj

        #post 获取 reponse 字符串
        def PostResponse(url,data):
            req = urllib2.Request(url)
            data = urllib.urlencode(data)
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
            response = opener.open(req, data)
            res = response.read()
            return res

        #img转字符画，附带游戏圆圈数据
        # url = SETTING.API_GAME
        #img转字符画服务
        url = SETTING.API_IMG_STR
        data  = {  "img_url":image_url}
        _res = PostResponse(url,data)  #数据字符串,同为stage_data
        _res_json = json.loads(_res)   #数据json对象
        _str_url = _res_json['str_url'] #字符画地址
        _img_url = _res_json['img_url']  #原图地址
        _sketch_url = _res_json['sketch_url']  #原图地址
        #微信跳转链接
        # _paw_url = "http://bushitan.pythonanywhere.com/art/show/?url=" + _str_url   #pythonanywhere 的链接
        # _paw_url = "http://120.27.97.33:82/blog/artwork/show/?str_img="+_str_url + "&origin_img="+ _img_url + "&sketch_img=" + _sketch_url +"&open_id=" + context['to_user_name'] #阿里云的链接 需要图片名称，用户open_id


        #添加游戏数据
        game_add_url = SETTING.GAME_ADD
        stage_data  = {'stage_data':_res}
        _res = PostResponse(game_add_url,stage_data)
        _game_id = json.loads(_res)["game_id"]
        _game_play_url = SETTING.GAME_PLAY + str(_game_id)

        #添加作品，
        blog_artwork_url = SETTING.BLOG_ARTWORK
        blog_data = {
            "open_id":context['to_user_name'],
            "img_url": _img_url,
            "char_img_url": _str_url,
            "sketch_url": _sketch_url

        }
        _res = PostResponse(blog_artwork_url,blog_data)  #增加作品
        _res_json = json.loads(_res)
        #添加artwork show 的跳转
        _gallery_id = _res_json['gallery_id']
        _paw_url =  SETTING.BLOG_ARTWORK_SHOW + "?gallery_id=" + str(_gallery_id)
        print 'paw_url:',_paw_url

        #跳转画廊链接
        #查看历史记录，根据用户的openid
        _gallery_url = SETTING.BLOG_ARTWORK_GALLERY + '?open_id='+context['to_user_name']

        #专家模式的链接地址
        _artwork_hard = SETTING.BLOG_ARTWORK_HARD + "?bg_img_url=" + _img_url

        create_time = int(time())

        text_img = {
            'to_user_name':context['to_user_name'],
            'from_user_name':context['from_user_name'],
            'create_time':create_time,
            'message_type':message_type,

            #字符画
            'title_str':u'明和暗',
            'pic_url':_str_url,
            'url':_paw_url,

            #s私密画廊
            'title_history':u'过程画廊',
            # 'des_history':u'(点"继续访问"，看历史记录)',
            'gallery_url':_gallery_url,

            #小游戏
            'title_game':u'小游戏',
            'game_play_url':_game_play_url, #游戏跳转链接

            #专家模式，局部分析
            'artwork_hard_title':u'局部分析模式',
            "artwork_hard_url" :  _artwork_hard
        }

        # text_reply_xml = text_xml % (c['to_user_name'],c['from_user_name'],c['create_time'],c['message_type'],c['content'])
        text_reply_xml = text_img_xml % (
            text_img['to_user_name'],text_img['from_user_name'],text_img['create_time'],text_img['message_type']
            ,text_img['title_str'],text_img['pic_url'],text_img['url'] #显示单页字符画
            ,text_img['title_history'] ,text_img['gallery_url'] #链接画廊
            # ,text_img['title_game'] ,text_img['game_play_url']#链接至游戏
            # ,text_img['artwork_hard_title'] ,text_img['artwork_hard_url']#链接至专家模式
        )


        response = HttpResponse(text_reply_xml,content_type='application/xml; charset=utf-8')

        return response
