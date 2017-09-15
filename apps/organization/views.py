# coding: utf-8
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

from .models import CityDict, CourseOrg, Teacher
from .forms import UserAskForm
from courses.models import Course
from operation.models import UserFavorite
from Lighten.settings import PAGINATION_SETTINGS


class OrgView(View):
    """
        课程机构列表功能
    """

    def get(self, request):
        # 取出城市、类别、排序参数
        city_id = request.GET.get('city', '')
        category = request.GET.get('ct', '')
        sort = request.GET.get('sort', '')

        # 机构排名
        hot_orgs = CourseOrg.objects.order_by('-click_nums')[:3]
        # 城市
        all_cities = CityDict.objects.all()

        # 课程搜索功能
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_organizations = CourseOrg.objects.filter(Q(name__icontains=search_keywords) |
                                                         Q(desc__icontains=search_keywords) |
                                                         Q(category__icontains=search_keywords) |
                                                         Q(address__icontains=search_keywords))
        else:
            all_organizations = CourseOrg.objects.all()

        # 根据城市筛选课程机构
        if city_id:
            all_organizations = all_organizations.filter(city_id=int(city_id))

        # 根据类别筛选课程机构
        if category:
            all_organizations = all_organizations.filter(category=category)

        # 根据sort: 'students' or 'courses'进行排序
        if sort:
            sort_dict = {'students': '-student_nums',
                         'courses': '-course_nums'}
            all_organizations = all_organizations.order_by(sort_dict[sort])

        # 对课程机构进行分页
        per_page = PAGINATION_SETTINGS.get('ORGANIZATION_NUM_PER_PAGE', '5')
        paginator = Paginator(all_organizations, per_page=per_page, request=request)
        try:
            page_num = int(request.GET.get('page', 1))
        except PageNotAnInteger:
            page_num = 1
        # 分页后的课程机构
        org_paginator = paginator.page(page_num)

        return render(request, 'org-list.html',
                      {'org_paginator': org_paginator,
                       'all_cities': all_cities,
                       'org_nums': all_organizations.count(),
                       'cur_city_id': city_id,
                       'category': category,
                       'hot_orgs': hot_orgs,
                       'sort': sort})


class AddUserAskView(View):
    """处理用户'我要学习'表单"""

    def post(self, request):
        user_ask_form = UserAskForm(request.POST)
        if user_ask_form.is_valid():
            user_ask_form.save(commit=True)
            return HttpResponse('{"status": "success"}', content_type='application/json')
        else:
            return HttpResponse('{"status": "fail", "msg": "添加出错"}', content_type='application/json')


class OrgDetailHomepageView(View):
    """首页->课程机构->机构首页"""

    def get(self, request, org_id):
        course_org = CourseOrg.objects.get(id=int(org_id))
        # 用户为登录状态时显示收藏状态
        has_fav = True if request.user.is_authenticated() and UserFavorite.objects.filter(user=request.user,
                                                                                          fav_id=course_org.id,
                                                                                          fav_type=2) else False

        all_courses = course_org.course_set.order_by('-students').all()[:3]
        all_teachers = course_org.teacher_set.all()[:1]
        return render(request, 'org-detail-homepage.html', {'course_org': course_org,
                                                            'all_courses': all_courses,
                                                            'all_teachers': all_teachers,
                                                            # 用于org_detail_base.html中确定标签的active
                                                            'current_page': 'homepage',
                                                            'has_fav': has_fav})


class OrgDetailCourseView(View):
    """首页->课程机构->机构课程"""

    def get(self, request, org_id):
        course_org = CourseOrg.objects.get(id=int(org_id))
        # 用户为登录状态时显示收藏状态
        has_fav = True if request.user.is_authenticated() and UserFavorite.objects.filter(user=request.user,
                                                                                          fav_id=course_org.id,
                                                                                          fav_type=2) else False

        all_courses = course_org.course_set.all()

        # 对课程进行分页
        per_page = PAGINATION_SETTINGS.get('COURSE_NUM_PER_PAGE', 6)
        paginator = Paginator(all_courses, per_page=per_page, request=request)
        try:
            page_num = int(request.GET.get('page', 1))
        except PageNotAnInteger:
            page_num = 1
        # 分页后的课程
        course_paginator = paginator.page(page_num)

        return render(request, 'org-detail-course.html', {'course_org': course_org,
                                                          'course_paginator': course_paginator,
                                                          'current_page': 'courses',
                                                          'has_fav': has_fav})


class OrgDetailDescView(View):
    """首页->课程机构->机构介绍"""

    def get(self, request, org_id):
        course_org = CourseOrg.objects.get(id=int(org_id))
        # 用户为登录状态时显示收藏状态
        has_fav = True if request.user.is_authenticated() and UserFavorite.objects.filter(user=request.user,
                                                                                          fav_id=course_org.id,
                                                                                          fav_type=2) else False
        return render(request, 'org-detail-desc.html', {'course_org': course_org,
                                                        'current_page': 'desc',
                                                        'has_fav': has_fav})


class OrgDetailTeacherView(View):
    """首页->课程机构->机构讲师"""

    def get(self, request, org_id):
        course_org = CourseOrg.objects.get(id=int(org_id))
        # 用户为登录状态时显示收藏状态
        has_fav = True if request.user.is_authenticated() and UserFavorite.objects.filter(user=request.user,
                                                                                          fav_id=course_org.id,
                                                                                          fav_type=2) else False
        all_teachers = course_org.teacher_set.all()
        return render(request, 'org-detail-teachers.html', {'course_org': course_org,
                                                            'all_teachers': all_teachers,
                                                            'current_page': 'teachers',
                                                            'has_fav': has_fav})


class AddFavView(View):
    """用户收藏、取消收藏"""

    def post(self, request):
        fav_id = int(request.POST.get('fav_id', 0))
        fav_type = int(request.POST.get('fav_type', 0))

        # 用于记录用户操作 获取用户收藏的对象name(课程名称、机构名称或讲师名字)
        fav_types = {1: (Course, '课程'), 2: (CourseOrg, '课程机构'), 3: (Teacher, '讲师')}
        obj_name = fav_types[fav_type][0].objects.get(id=fav_id).name
        obj_type = fav_types[fav_type][1]

        # 用户必须为登录状态
        if not request.user.is_authenticated():
            return HttpResponse('{"status": "fail", "msg": "用户未登录"}',
                                content_type='application/json')

        exist_records = UserFavorite.objects.filter(user=request.user, fav_id=fav_id, fav_type=fav_type)
        if exist_records:
            # 记录已存在, 表示用户取消收藏
            exist_records.delete()
            # 记录用户操作
            request.user.log('取消了收藏({type}): {name}'.format(type=obj_type, name=obj_name))
            return HttpResponse('{"status": "success", "msg": "收藏"}',
                                content_type='application/json')
        else:
            # 添加用户收藏
            user_fav = UserFavorite()
            if fav_id > 0 and fav_type > 0:
                user_fav.user = request.user
                user_fav.fav_id = fav_id
                user_fav.fav_type = fav_type
                user_fav.save()

                # 记录用户操作
                request.user.log('收藏了{type}: {name}'.format(type=obj_type, name=obj_name))
                return HttpResponse('{"status": "success", "msg": "已收藏"}',
                                    content_type='application/json')
            else:
                return HttpResponse('{"status": "fail", "msg": "收藏失败"}',
                                    content_type='application/json')


class TeacherListView(View):
    """
        课程讲师列表页
    """

    def get(self, request):

        # 是否排序
        sort = request.GET.get('sort', '')
        if sort == 'hot':
            all_teachers = Teacher.objects.order_by('-click_nums')
        else:
            all_teachers = Teacher.objects.all()

        # 课程搜索功能
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_teachers = all_teachers.filter(Q(name__icontains=search_keywords) |
                                               Q(academic_degree__icontains=search_keywords) |
                                               Q(work_company__icontains=search_keywords) |
                                               Q(work_position__icontains=search_keywords) |
                                               Q(org__name__icontains=search_keywords))

        # 分页
        per_page = PAGINATION_SETTINGS.get('TEACHER_NUM_PER_PAGE', 10)
        paginator = Paginator(all_teachers.all(), per_page, request=request)
        try:
            page_index = int(request.GET.get('page', 1))
        except PageNotAnInteger:
            page_index = 1
        teacher_paginator = paginator.page(page_index)

        # 讲师排行榜
        hot_teachers = Teacher.objects.order_by('-fav_nums')[:5]

        return render(request, 'teachers-list.html', {'teacher_paginator': teacher_paginator,
                                                      'teacher_nums': all_teachers.count(),
                                                      'hot_teachers': hot_teachers,
                                                      'sort': sort})


class TeacherDetailView(View):
    """
        讲师详情页
    """

    def get(self, request, teacher_id):
        teacher = Teacher.objects.get(id=teacher_id)
        teacher_has_fav = True if request.user.is_authenticated() and UserFavorite.objects.filter(user=request.user,
                                                                                                  fav_id=teacher_id,
                                                                                                  # 3为教师类型
                                                                                                  fav_type=3) else False
        org_has_fav = True if request.user.is_authenticated() and UserFavorite.objects.filter(user=request.user,
                                                                                              fav_id=teacher.org.id,
                                                                                              # 2为课程机构
                                                                                              fav_type=2) else False
        # 讲师排行榜
        hot_teachers = Teacher.objects.order_by('-fav_nums')[:5]

        # 全部课程(按照学习人数排序)
        teacher_courses = Course.objects.filter(teacher=teacher).order_by('-students')

        return render(request, 'teacher-detail.html', {'teacher': teacher,
                                                       'teacher_has_fav': teacher_has_fav,
                                                       'org_has_fav': org_has_fav,
                                                       'teacher_courses': teacher_courses,
                                                       'typical_courses': teacher_courses[:2],
                                                       'hot_teachers': hot_teachers})
