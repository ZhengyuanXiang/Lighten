# coding: utf-8

from django.conf.urls import url

from .views import UserInfoView, UploadImageView, UpdatePasswordView, SendEmailCodeView, UpdateEmailView

urlpatterns = [
    # 用户信息
    url(r'^info/$', UserInfoView.as_view(), name='user_info'),

    # 处理用户头像上传
    url(r'^image/upload/$', UploadImageView.as_view(), name='upload_image'),

    # 用户个人中心修改密码
    url(r'^update/pwd/$', UpdatePasswordView.as_view(), name='update_pwd'),

    # 发送邮箱验证码(用户更改绑定邮箱时)
    url(r'^send_email_code/$', SendEmailCodeView.as_view(), name='send_email_code'),

    # 修改邮箱
    url(r'^update_email/$', UpdateEmailView.as_view(), name='update_email')
]