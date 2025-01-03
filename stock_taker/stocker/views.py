from django.shortcuts import render, redirect
from .models import User, Location, Item, Storage, Storage, Activity, Icategory, Lcategory, Notifications
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.db import connection,  IntegrityError
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password  # check_password 임포트 추가
from django.http import JsonResponse  # JsonResponse를 임포트합니다.
from datetime import date
from django.db.models import Sum, Count, Q  # Sum을 임포트합니다.
import json  # json 모듈 임포트
from django.core.mail import send_mail

#=================================================================
#=================================================================
#로그인, 로그아웃, 관리자 계정 접속 관련 코드 
#=================================================================
#=================================================================
#로그인
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        # 데이터베이스에서 사용자 정보 확인
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM user WHERE user_name = %s", [username]
            )
            user = cursor.fetchone()  # 사용자 정보를 가져옴

        if user is not None:
            stored_password = user[2]  # 비밀번호는 3번째 컬럼에 위치
            if check_password(password, stored_password):  # 해시된 비밀번호 확인
                # 세션에 사용자 정보 저장
                request.session['user_id'] = user[0]  # 사용자 ID 저장
                request.session['username'] = user[1]  # 사용자 이름 저장
                request.session['email'] = user[3]
                request.session['role'] = user[4]
                return redirect('index')  # 로그인 후 이동할 페이지

            messages.error(request, '사용자 이름 또는 비밀번호가 잘못되었습니다.')
        else:
            messages.error(request, '페이지에 없는 계정입니다.')

    return render(request, 'login.html')

#로그인하고 다음 페이지 들고오기
def index_view(request):
    # 세션에서 사용자 정보 가져오기
    items = Item.objects.all()  # 아이템 목록 가져오기
    locations = Location.objects.all()  # 위치 목록 가져오기
    storages = Storage.objects.all()  # 저장된 아이템 목록 가져오기 (추가)
    username = request.session.get('username')  # 세션에서 사용자 이름 가져오기
    role = request.session.get('role')  # 세션에서 사용자 역할 가져오기
    categories = Lcategory.objects.all()
    icategories = Icategory.objects.all()
    if username:
        return render(request, 'index.html', {
            'items': items,
            'locations': locations,
            'storages': storages,  # storages 추가
            'username': username,
            'role': role,
            'categories' : categories,
            'icategories': icategories,
        })
    else:
        return redirect('login')  # 로그인하지 않은 경우 로그인 페이지로 리다이렉트

#로그아웃
def logout_view(request):
    # 세션 데이터 삭제
    request.session.flush()  # 모든 세션 데이터 삭제
    return redirect('login')  # 로그인 페이지로 리다이렉트

#회원가입하기
def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        role = request.POST.get('role', 'nor')  # 기본값으로 'nor' 설정
        
        # 비밀번호 해싱
        hashed_password = make_password(password)

        try:
            # SQL 쿼리 실행
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO user (user_name, password, email, role) VALUES (%s, %s, %s, %s)",
                    [username, hashed_password, email, role]
                )
            messages.success(request, '회원가입이 완료되었습니다. 로그인 해주세요.')
            return redirect('login')  # 회원가입 후 로그인 페이지로 이동
        except IntegrityError:
            messages.error(request, '이미 사용 중인 사용자 이름 또는 이메일입니다. 다른 값을 입력해주세요.')
        except Exception as e:
            messages.error(request, '회원가입 중 오류가 발생했습니다. 다시 시도해주세요.')
    
    return render(request, 'signup.html')

def add_adm(request):
    # 관리자 페이지 로직을 여기에 추가
    username = request.session.get('username')  # 세션에서 사용자 이름 가져오기
    user_id = request.session.get('user_id')  # 세션에서 사용자 이름 가져오기
    icategories = Icategory.objects.all()  # 모든 카테고리를 가져옵니다.
    lcategories = Lcategory.objects.all()  # 모든 카테고리를 가져옵니다.
    activities = Activity.objects.all()
    items = Item.objects.all()
    locations = Location.objects.all()
    notifications = Notifications.objects.all()
    users = User.objects.all()
    return render(request, 'addADM.html', { 'items': items, 'locations':locations, 'icategories': icategories, 'lcategories': lcategories, 'username' : username, 'user_id' : user_id, 'activities': activities, 'notifications': notifications, 'users': users})


#=================================================================
#=================================================================
#관리자 페이지에서 관리하는 DB 입력하는 것. icategory, pcategory, item, position 
#=================================================================
#=================================================================
@csrf_exempt
def add_icategory(request):
    username = request.session.get('username')  # 세션에서 사용자 이름 가져오기
    if request.method == 'POST':
        icategory_name = request.POST.get('icategory_name')  # 변수 이름 수정
        iicategory_des = request.POST.get('iicategory_des')  # 변수 이름 수정
        
        # SQL 쿼리 문을 사용하여 카테고리 추가
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO icategory (icategory_name, icategory_des) VALUES (%s, %s)",  # 열 이름 수정
                    [icategory_name, iicategory_des]  # 변수 이름 수정
                )
            messages.success(request, '아이템 카테고리가 성공적으로 추가되었습니다.')
            icategories = Icategory.objects.all()  # 모든 카테고리를 가져옵니다.
            lcategories = Lcategory.objects.all()  # 모든 카테고리를 가져옵니다.
            return render(request, 'addADM.html', {'icategories': icategories, 'lcategories': lcategories, 'username' : username})

        except IntegrityError:
            # IntegrityError는 주로 중복된 프라이머리 키로 인해 발생
            messages.error(request, '이미 존재하는 카테고리입니다.')
            return redirect('add_adm')

        except Exception as e:
            # 다른 예외 처리
            messages.error(request, '카테고리 추가 중 오류가 발생했습니다: {}'.format(str(e)))
            return redirect('add_adm')

    return JsonResponse({"error": "잘못된 요청입니다."}, status=400)

@csrf_exempt
def add_lcategory(request):
    username = request.session.get('username')  # 세션에서 사용자 이름 가져오기
    if request.method == 'POST':
        lcategory_name = request.POST.get('lcategory_name')  # 변수 이름 수정
        lcategory_des = request.POST.get('lcategory_des')  # 변수 이름 수정
        
        # SQL 쿼리 문을 사용하여 카테고리 추가
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO lcategory (lcategory_name, lcategory_des) VALUES (%s, %s)",  # 열 이름 수정
                    [lcategory_name, lcategory_des]  # 변수 이름 수정
                )
            messages.success(request, '위치 카테고리가 성공적으로 추가되었습니다.')
            icategories = Icategory.objects.all()  # 모든 카테고리를 가져옵니다.
            lcategories = Lcategory.objects.all()  # 모든 카테고리를 가져옵니다.
            return render(request, 'addADM.html', {'icategories': icategories, 'lcategories': lcategories, 'username' : username})

        except IntegrityError:
            # IntegrityError는 주로 중복된 프라이머리 키로 인해 발생
            messages.error(request, '이미 존재하는 카테고리입니다.')
            return redirect('add_adm')

        except Exception as e:
            # 다른 예외 처리
            messages.error(request, '카테고리 추가 중 오류가 발생했습니다: {}'.format(str(e)))
            return redirect('add_adm')
    return JsonResponse({"error": "잘못된 요청입니다."}, status=400)

def add_item(request):
    username = request.session.get('username')  # 세션에서 사용자 이름 가져오기
    if request.method == 'POST':
        item_name = request.POST.get('item_name')
        icategory_id = request.POST.get('icategory_id')
        item_quantity = 0
        notifibool = request.POST.get('notifibool') == 'on'

        # SQL 쿼리 문을 사용하여 카테고리 추가
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO item (item_name, icategory_id, item_quantity, notifibool ) VALUES (%s, %s, %s, %s)",  # 열 이름 수정
                    [item_name, icategory_id, item_quantity, notifibool]  # 변수 이름 수정
                )
            messages.success(request, '아이템이 성공적으로 추가되었습니다.')
            return redirect('add_adm')

        except IntegrityError:
            # IntegrityError는 주로 중복된 프라이머리 키로 인해 발생
            messages.error(request, '이미 존재하는 아이템입니다.')
            return redirect('add_adm')

        except Exception as e:
            # 다른 예외 처리
            messages.error(request, '아이템 추가 중 오류가 발생했습니다: {}'.format(str(e)))
            return redirect('add_adm')


    icategories = ICategory.objects.all()
    return JsonResponse({"icategories": list(icategories.values())})

def add_location(request):
    if request.method == 'POST':
        location_name = request.POST.get('location_name')
        x = request.POST.get('X')
        y = request.POST.get('Y')
        z = request.POST.get('Z')
        lcategory_id = request.POST.get('lcategory_id')
        E_N_H = request.POST.get('E_N_H')
        
        # SQL 쿼리 문을 사용하여 카테고리 추가
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO location (location_name, x, y, z, E_N_H, lcategory_id ) VALUES (%s, %s, %s, %s, %s, %s)",  # 열 이름 수정
                    [location_name, x, y, z, E_N_H, lcategory_id ]  # 변수 이름 수정
                )
            messages.success(request, '위치가 성공적으로 추가되었습니다.')
            return redirect('add_adm')

        except IntegrityError:
            # IntegrityError는 주로 중복된 프라이머리 키로 인해 발생
            messages.error(request, '이미 존재하는 위치입니다.')
            return redirect('add_adm')

        except Exception as e:
            # 다른 예외 처리
            messages.error(request, '아이템 추가 중 오류가 발생했습니다: {}'.format(str(e)))
            return redirect('add_adm')

        return JsonResponse({"message": "위치가 성공적으로 추가되었습니다."})

    lcategories = LCategory.objects.all()
    return JsonResponse({"lcategories": list(lcategories.values())})

@csrf_exempt
def delete_icategory(request):
    username = request.session.get('username')  # 세션에서 사용자 이름 가져오기
    if request.method == 'POST':
        icategory_id = request.POST.get('icategory_id')  # 드롭다운에서 선택된 아이템 카테고리 ID 가져오기
        if icategory_id:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM icategory WHERE icategory_id = %s", [icategory_id]
                    )
                messages.success(request, '아이템 카테고리가 성공적으로 삭제되었습니다.')
            except IntegrityError:
                messages.error(request, '이미 사용 중인 아이템 카테고리입니다. 삭제할 수 없습니다.')
            except Exception as e:
                messages.error(request, '카테고리 삭제 중 오류가 발생했습니다: {}'.format(str(e)))

        # 카테고리 목록을 다시 로드
        icategories = Icategory.objects.all()
        lcategories = Lcategory.objects.all()
        return redirect('add_adm')

    return JsonResponse({"error": "잘못된 요청입니다."}, status=400)

@csrf_exempt
def delete_lcategory(request):
    username = request.session.get('username')  # 세션에서 사용자 이름 가져오기
    if request.method == 'POST':
        lcategory_id = request.POST.get('lcategory_id')  # 드롭다운에서 선택된 위치 카테고리 ID 가져오기
        if lcategory_id:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM lcategory WHERE lcategory_id = %s", [lcategory_id]
                    )
                messages.success(request, '위치 카테고리가 성공적으로 삭제되었습니다.')
            except IntegrityError:
                messages.error(request, '이미 사용 중인 위치 카테고리입니다. 삭제할 수 없습니다.')
            except Exception as e:
                messages.error(request, '카테고리 삭제 중 오류가 발생했습니다: {}'.format(str(e)))

        # 카테고리 목록을 다시 로드
        icategories = Icategory.objects.all()
        lcategories = Lcategory.objects.all()
        return redirect('add_adm')

    return JsonResponse({"error": "잘못된 요청입니다."}, status=400)

@csrf_exempt
def delete_item(request):
    username = request.session.get('username')  # 세션에서 사용자 이름 가져오기
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM item WHERE item_id = %s", [item_id])
            messages.success(request, '아이템이 성공적으로 삭제되었습니다.')
        except IntegrityError:
            messages.error(request, '이 아이템은 다른 곳에서 사용 중입니다. 삭제할 수 없습니다.')
        except Exception as e:
            messages.error(request, '아이템 삭제 중 오류가 발생했습니다: {}'.format(str(e)))

        items = Item.objects.all()
        locations = Location.objects.all()
        return redirect('add_adm')

    return JsonResponse({"error": "잘못된 요청입니다."}, status=400)

@csrf_exempt
def delete_location(request):
    username = request.session.get('username')  # 세션에서 사용자 이름 가져오기
    if request.method == 'POST':
        location_id = request.POST.get('location_id')

        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM location WHERE location_id = %s", [location_id])
            messages.success(request, '위치가 성공적으로 삭제되었습니다.')
        except IntegrityError:
            messages.error(request, '이 위치는 다른 곳에서 사용 중입니다. 삭제할 수 없습니다.')
        except Exception as e:
            messages.error(request, '위치 삭제 중 오류가 발생했습니다: {}'.format(str(e)))

        items = Item.objects.all()
        locations = Location.objects.all()
        return redirect('add_adm')

    return JsonResponse({"error": "잘못된 요청입니다."}, status=400)
 

def delete_notifications(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            notification_ids = data.get("notification_ids", [])
            
            # 알림 삭제
            if notification_ids:
                with connection.cursor() as cursor:
                    # SQL IN 절을 사용하여 여러 알림 삭제
                    format_strings = ','.join(['%s'] * len(notification_ids))
                    cursor.execute(f"DELETE FROM notifications WHERE notification_id IN ({format_strings})", notification_ids)
                
                messages.success(request, '알림이 성공적으로 삭제되었습니다.')
                return JsonResponse({'success': True, 'success': '삭제하였습니다'})
            else:
                return JsonResponse({'success': False, 'error': '삭제할 알림 ID가 없습니다.'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request'})

def email_notifications(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            notification_ids = data.get("notification_ids", [])
            user_id = data.get("user_id")  # 요청에서 사용자 ID 가져오기
            
            # 알림이 존재하는 경우
            if notification_ids and user_id:
                with connection.cursor() as cursor:
                    # SQL IN 절을 사용하여 여러 알림의 상태를 SENT로 변경
                    format_strings = ','.join(['%s'] * len(notification_ids))
                    cursor.execute(f"UPDATE notifications SET notification_status = 'SENT' WHERE notification_id IN ({format_strings})", notification_ids)

                # 해당 알림들의 메시지 가져오기
                notifications = Notifications.objects.filter(notification_id__in=notification_ids)
                notification_messages = [notif.notification_message for notif in notifications]

                # 요청받은 사용자 ID에 해당하는 사용자 찾기
                recipient_user = User.objects.filter(user_id=user_id).first()
                
                if recipient_user and recipient_user.email:  # 사용자 존재 및 이메일이 있는지 확인
                    # 삭제된 알림 메시지를 문자열로 변환
                    notification_messages_str = ', '.join(notification_messages)
                    email_subject = '[재고 관리기 알림] 재고에 문제가 생겼습니다.'
                    email_body = f'다음 재고에 문제가 발생하였습니다: {notification_messages_str}'

                    # 이메일 발송
                    send_mail(
                        email_subject,
                        email_body,
                        'panda_g02@naver.com',  # 발신자 이메일 주소
                        [recipient_user.email],  # 수신자 이메일 주소
                        fail_silently=False,
                    )

                    messages.success(request, '선택한 사용자에게 이메일이 발송되었습니다.')
                    return JsonResponse({'success': True, 'message': '이메일을 발송하였습니다.'})
                else:
                    return JsonResponse({'success': False, 'error': '유효한 사용자 또는 이메일이 없습니다.'})

            else:
                return JsonResponse({'success': False, 'error': '보낼 알림 ID 또는 사용자 ID가 없습니다.'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request'})

def delete_activities(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            activity_ids = data.get("activity_ids", [])
            
            # 활동 기록 삭제
            if activity_ids:
                with connection.cursor() as cursor:
                    # SQL IN 절을 사용하여 여러 활동 기록 삭제
                    format_strings = ','.join(['%s'] * len(activity_ids))
                    cursor.execute(f"DELETE FROM activity WHERE activity_id IN ({format_strings})", activity_ids)
                
                messages.success(request, '사용 기록이 성공적으로 삭제되었습니다.')
                return JsonResponse({'success': True, 'message': '삭제하였습니다'})
            else:
                return JsonResponse({'success': False, 'error': '삭제할 활동 ID가 없습니다.'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request'})

#=================================================================
#=================================================================
#index.html에서 사용할 것.
#=================================================================
#=================================================================
@csrf_exempt
def store_item(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        location_id = request.POST.get('location_id')
        expired_date = request.POST.get('expired_date')
        state = request.POST.get('state')
        quantity_stored = request.POST.get('quantity_stored')
        user_id = request.session.get('user_id')
        stored_date = date.today() #입력 날짜를 기준으로 저장된 날짜를 넣음. 
        
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "CALL combine_quantity_procedure(%s, %s, %s, %s, %s, %s, %s)",
                    [item_id, location_id, quantity_stored, state, stored_date, expired_date, user_id]  # 변수 이름 수정
                )
            messages.success(request, '저장 되었습니다.')
            return redirect('index')

        except IntegrityError:
            # IntegrityError는 주로 중복된 프라이머리 키로 인해 발생
            messages.error(request, '이미 존재하는 데이터 입니다.')
            return redirect('index')

        except Exception as e:
            print(f"Error occurred: {e}")  # 또는 logging.error(f"Error occurred: {e}")
            messages.error(request, '아이템 추가 중 오류가 발생했습니다: {}'.format(str(e)))
            return redirect('index')
        
        return JsonResponse({"message": "저장 되었습니다."})
    

    items = Item.objects.all()
    locations = Location.objects.all()
    return render(request, 'index', {'items': items, 'locations': locations})

def use_item(request):
    if request.method == 'POST':
        storage_id = request.POST.get('storage_id')
        quantity_activity = request.POST.get('quantity_activity')
        date_used = date.today()  # 사용된 날짜를 저장
        user_id = request.session.get('user_id')
        
        
       
        try:
             # storage_id로 Storage 객체를 가져옴
            storage = Storage.objects.get(storage_id=storage_id)
            
            # storage 정보를 텍스트로 변환
            storage_text = f"아이템 종류: {storage.item.icategory.icategory_name}의 {storage.item.item_name}, 위치: {storage.location.lcategory.lcategory_name}의 {storage.location.location_name}, 기존 수량: {storage.quantity_stored}"
            
            with connection.cursor() as cursor:
                cursor.execute(
                    "CALL combine_quantity_activity_procedure(%s, %s, %s, %s, %s)",
                    [user_id, storage_text, quantity_activity, date_used, storage_id]
                )
            messages.success(request, '아이템이 성공적으로 사용되었습니다.')
            return redirect('index')

        except IntegrityError:
            messages.error(request, '잘못된 요청입니다. 다시 시도하세요.')
            return redirect('index')

        except Exception as e:
            messages.error(request, f'오류 발생: {e}')
            return redirect('index')

    # 카테고리, 아이템, 저장된 아이템 정보 불러오기
    icategories = Icategory.objects.all()
    items = Item.objects.all()
    storages = Storage.objects.select_related('item', 'location').all()

    return render(request, 'use_item.html', {
        'icategories': icategories,
        'items': items,
        'storages': storages
    })
     
def recommend_storage(request):
    if request.method == 'GET':
        item_name = request.GET.get('item_name')
        item_size_x = float(request.GET.get('item_size_x'))
        item_size_y = float(request.GET.get('item_size_y'))
        item_size_z = float(request.GET.get('item_size_z'))
        
        # 아이템 이름이 일치하는 것이 있는지 확인
        item_exists = Item.objects.filter(item_name=item_name).exists()  # item_name 필드를 사용합니다.

        if not item_exists:
            # 아이템이 존재하지 않을 경우 알림 메시지 추가
            messages.error(request, "아이템이 존재하지 않습니다.")
            # 리다이렉트할 URL을 지정합니다. 예를 들어, 'index'라는 이름의 URL로 리다이렉트
            return redirect('index')  # 'index'는 실제 리다이렉트할 URL의 이름으로 변경해야 합니다.

        # 같은 이름의 아이템이 가장 많이 저장된 위치를 찾기
        most_common_location = (
            Storage.objects
            .filter(item__item_name=item_name)  # 아이템 이름으로 필터링
            .annotate(item_count=Count('item_id'))  # 각 위치에 저장된 아이템 수를 계산
            .order_by('-item_count')  # 아이템 수가 많은 순서로 정렬
            .first()  # 가장 많은 아이템이 저장된 위치를 가져옴
        )
        
        if most_common_location:
            location_id_many = most_common_location.location.location_name
            location_name_many= most_common_location.location.lcategory.lcategory_name
        else:
            location_id_many = "없음"
            

        # 아이템 크기와 가장 유사한 저장 공간 찾기
        similar_locations = (
            Location.objects
            .annotate(
                size_difference=(
                    Q(x__gte=item_size_x) & Q(y__gte=item_size_y) & Q(z__gte=item_size_z)
                )
            )
            .filter(size_difference=True)  # 크기가 충분한 저장 공간 필터링
        )
        if similar_locations.exists():
            # 크기 차이를 계산하여 정렬
            sorted_locations = sorted(
                similar_locations,
                key=lambda loc: (float(loc.x) - float(item_size_x)) ** 2 + (float(loc.y) - float(item_size_y)) ** 2 + (float(loc.z) - float(item_size_z)) ** 2
            )
            
            # 상위 3개 선택 (3개 이하일 경우 모두 선택)
            location_id_simil = [loc.location_name for loc in sorted_locations[:3]]
            location_cate_simil = [loc.lcategory.lcategory_name for loc in sorted_locations[:3]]
            

            # 리스트를 문장으로 변환
            if location_id_simil:
                # lcategory_name과 location_name을 조합하여 문장 생성
                location_sentence = ", ".join(f"{cate}의 {name}" for cate, name in zip(location_cate_simil, location_id_simil))
            else:
                location_sentence = "추천 위치가 없습니다."
        else:
            location_sentence = "추천 위치가 없습니다."

        
        # 추천 결과를 템플릿에 전달합니다.
        messages.success(request, f"가장 많이 저장된 위치:{location_name_many}의 {location_id_many}, 들어갈 수 있는 위치: {location_sentence}")
        return redirect('index')

    # GET 요청이 아닐 경우, 기본 템플릿을 반환합니다.
    return redirect('index')

def get_items_and_locations(request):
    category_id = request.GET.get('category_id')
    items = Item.objects.filter(category_id=category_id).values('item_id', 'item_name')
    locations = Location.objects.filter(lcategory_id=category_id).values('location_id', 'location_name', 'lcategory__lcategory_name')

    return JsonResponse({
        'items': list(items),
        'locations': list(locations),
    })