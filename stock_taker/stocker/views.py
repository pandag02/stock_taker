from django.shortcuts import render, redirect
from .models import User, Location, Item, Storage, Storage, Activity, Icategory, Lcategory
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.db import connection,  IntegrityError
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password  # check_password 임포트 추가
from django.http import JsonResponse  # JsonResponse를 임포트합니다.
from datetime import date
from django.db.models import Sum  # Sum을 임포트합니다.
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
    return render(request, 'addADM.html', {'icategories': icategories, 'lcategories': lcategories, 'username' : username, 'user_id' : user_id, 'activities': activities})


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
        date_used = date.today() #입력 날짜를 기준으로 저장된 날짜를 넣음. 
        user_id = request.session.get('user_id')
        
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "CALL combine_quantity_activity_procedure(%s, %s, %s, %s)",
                    [user_id, storage_id, quantity_activity, date_used]  # 변수 이름 수정
                )
            messages.success(request, '사용 되었습니다.')
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

    storages = Storage.objects.all()
    return render(request, 'index', {'items': items, 'locations': locations})

def recommend_storage(request):
    if request.method == 'GET':
        item_name = request.GET.get('item_name')
        item_size_x = float(request.GET.get('item_size_x', 0))
        item_size_y = float(request.GET.get('item_size_y', 0))
        item_size_z = float(request.GET.get('item_size_z', 0))

        # 해당 이름의 아이템 찾기
        item = Item.objects.filter(item_name=item_name).first()

        if item is not None:  # item이 None이 아닐 경우에만 진행
            # 1순위: 해당 아이템이 가장 많이 있는 위치 찾기
            storage_data = Storage.objects.filter(item_id=item.item_id).values('location_id').annotate(total_quantity=Sum('quantity_stored')).order_by('-total_quantity')
            most_stored_location = None
            if storage_data:
                # 가장 많이 저장된 위치의 ID를 가져와서 Location 객체를 찾음
                most_stored_location_id = storage_data[0]['location_id']
                most_stored_location = Location.objects.get(pk=most_stored_location_id)

            # 2순위: 크기가 맞는 위치 찾기
            compatible_locations = Location.objects.filter(x__gte=item_size_x, y__gte=item_size_y, z__gte=item_size_z)

            return JsonResponse({
                "message": {
                    'item': item.item_name,
                    'most_stored_location': most_stored_location.location_name if most_stored_location else None,  # 필드 이름 수정
                    'compatible_locations': [location.location_name for location in compatible_locations],
                }
            })
        else:
            return JsonResponse({"message": "오류 발생: 아이템을 찾을 수 없습니다."})

    return JsonResponse({"message": "잘못된 요청입니다."})




def get_items_and_locations(request):
    category_id = request.GET.get('category_id')
    items = Item.objects.filter(category_id=category_id).values('item_id', 'item_name')
    locations = Location.objects.filter(lcategory_id=category_id).values('location_id', 'location_name', 'lcategory__lcategory_name')

    return JsonResponse({
        'items': list(items),
        'locations': list(locations),
    })