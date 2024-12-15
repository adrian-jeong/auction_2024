import streamlit as st  
from datetime import datetime, timedelta  
import os  
import json  
from PIL import Image  # Pillow 라이브러리 임포트  
  
# 페이지를 와이드 레이아웃으로 설정  
st.set_page_config(layout="wide")  
  
# 이미지 경로 설정  
image_dir = './'  
  
# JSON 파일 경로 설정  
auction_data_file = 'auction_data.json'  
  
# 경매 종료 시간 설정 (12월 19일 15:00)  
auction_end_time = datetime(2024, 12, 19, 15, 0, 0)  
  
# 연장 시간 (5분)  
extend_time = timedelta(minutes=5)  
  
# 경매 데이터 로드 또는 초기화  
def load_auction_data():  
    if os.path.exists(auction_data_file):  
        with open(auction_data_file, 'r', encoding='utf-8') as f:  
            data_loaded = json.load(f)  
            data = {'auction_items': []}  
            for item in data_loaded['auction_items']:  
                item_copy = item.copy()  
                item_copy['end_time'] = datetime.strptime(item_copy['end_time'], '%Y-%m-%d %H:%M:%S')  
                item_copy['bids'] = []  
                for bid in item['bids']:  
                    bid_copy = bid.copy()  
                    bid_copy['timestamp'] = datetime.strptime(bid_copy['timestamp'], '%Y-%m-%d %H:%M:%S')  
                    item_copy['bids'].append(bid_copy)  
                data['auction_items'].append(item_copy)  
            return data  
    else:  
        # 파일이 없으면 기본 데이터로 초기화  
        filenames = [  
            '1. 목련이 있는 정물.jpeg',  
            '2. 미델하르니스의 가로수길.jpeg',  
            '3. 아네모네와 튤립.jpeg',  
            '4. 에트르타의 거대한 바다.jpeg',  
            '5. 기사(베토벤 프리즈의 일부).jpeg',  
            '6. 분홍장미.jpeg',  
            '7. 햇빛 속의 포플러.jpeg',  
            '8. 무거운 빨강.jpeg',  
            '9. 해바라기가 있는 정원.jpeg',  
            '10. Behold, He Standeth behind Our Wall.jpeg',  
            '11. 사과나무.jpeg'  
        ]  
        auction_items = []  
        for filename in filenames:  
            # 파일명에서 번호와 이름 추출  
            name_with_extension = os.path.basename(filename)  
            name_without_extension = os.path.splitext(name_with_extension)[0]  
            # 번호와 이름 분리  
            if '. ' in name_without_extension:  
                number, name = name_without_extension.split('. ', 1)  
            else:  
                name = name_without_extension  
            item = {  
                "name": f"{number}. {name}",  
                "image": os.path.join(image_dir, filename),  
                "current_bid": 30000,  # 최소 금액 3만원으로 설정  
                "end_time": auction_end_time,  
                "bids": [],  # 입찰 기록을 저장하는 리스트  
            }  
            auction_items.append(item)  
        data = {'auction_items': auction_items}  
        # 기본 데이터를 저장  
        save_auction_data(data)  
        return data  
  
def save_auction_data(data):  
    # 저장할 데이터를 복사본으로 생성  
    data_to_save = {'auction_items': []}  
    for item in data['auction_items']:  
        item_copy = item.copy()  
        item_copy['end_time'] = item['end_time'].strftime('%Y-%m-%d %H:%M:%S')  
        item_copy['bids'] = []  
        for bid in item['bids']:  
            bid_copy = bid.copy()  
            bid_copy['timestamp'] = bid['timestamp'].strftime('%Y-%m-%d %H:%M:%S')  
            item_copy['bids'].append(bid_copy)  
        data_to_save['auction_items'].append(item_copy)  
  
    # 데이터를 JSON 파일로 저장  
    with open(auction_data_file, 'w', encoding='utf-8') as f:  
        json.dump(data_to_save, f, ensure_ascii=False, indent=4)  
  
# 경매 데이터 불러오기  
auction_data = load_auction_data()  
  
# 세션 상태에서 선택된 아이템 관리  
if 'selected_item_index' not in st.session_state:  
    st.session_state['selected_item_index'] = None  
  
# 사이드바에 LG 로고를 클릭 가능한 링크로 추가 (옵션)  
svg_image_url = "https://www.lge.co.kr/lg5-common/images/header/lg_logo_new.svg"  
st.sidebar.markdown(  
    f'<a href="#" onclick="window.location.reload();"><img src="{svg_image_url}" width="150"></a>',  
    unsafe_allow_html=True,  
)  
  
# 사이드바에 아이템 이름 리스트 표시  
item_names = ['[Home]', '[전체 경매 현황]']  
item_names += [item['name'] for item in auction_data['auction_items']]  
  
#st.sidebar.markdown('<p style="font-size:20px;"><b>아트옥션 경매 리스트</b></p>', unsafe_allow_html=True)  
  
# 아이템을 라디오 버튼으로 표시  
selected_item_name = st.sidebar.radio('', item_names, key='item_radio')  
  
# Determine what to show based on selected option  
if selected_item_name == '[Home]':  
    st.session_state['selected_item_index'] = None  
elif selected_item_name == '[전체 경매 현황]':  
    st.session_state['selected_item_index'] = 'overview'  
else:  
    index = item_names.index(selected_item_name) - 2  # Adjust index due to new "전체 경매 현황" option  
    st.session_state['selected_item_index'] = index  
  
# 선택된 아이템이 없으면 홈 화면 표시  
if st.session_state['selected_item_index'] is None:  
    # 페이지를 좌우로 분할  
    col1, col2 = st.columns([2, 3])  # 좌측 컬럼이 좁고 우측이 넓게 설정  
  
    with col1:  
        # 포스터 이미지 표시  
        poster_image_path = os.path.join(image_dir, '24년 아트옥션 포스터.jpg')  
        if os.path.exists(poster_image_path):  
            img = Image.open(poster_image_path)  
            st.image(img, use_container_width=True)  
        else:  
            st.write("포스터 이미지를 찾을 수 없습니다.")  
  
    with col2:  
        # 기존 홈 화면 내용  
        st.markdown("<h3> 고객가치혁신부문 아트옥션에 오신것을 환영합니다!</h3>", unsafe_allow_html=True)  
        st.markdown("""  
<div style="font-size: 16px;">  
    <h4>[참여방법]</h4>  
    <ol>  
        <li>왼쪽 Tab 에서 원하시는 작품을 선택하시고, <b>[입찰하기]</b>에 “담당” Click! “이름” 입력 해주세요.</li>  
        <li>입찰가를 <span style="color: red; font-weight: bold;">정확히!</span> 입력하고 아래 <b>[입찰하기]</b>를 눌러주세요. [<span style="color: red;">최소 변경 금액 : 1,000원</span>]</li>  
        <li>타인 대리접수는 <span style="color: red;">불가</span>합니다.</li>  
        <li>금액 오 입력 시, JB에게 문의해주세요. (<span style="color: red;">0 하나를 더 붙이지 않게 모두 조심!</span>)</li>  
    </ol>  
    <ul>  
        <li> 올해는 EP 게시판이 아닌 아래 URL을 통해서 참여하실 수 있습니다.</li>  
        <li> 최종 종료 일자는 <b>12월 19일 (목요일) 오후 3시</b>이며, 최종 입찰자가 입찰시 시간은 자동으로 <span style="color: red;">5분 연장</span>됩니다.</li>  
        (작년과 같이 초싸움이 되지 않도록 업그레이드하였습니다. 연장된 시간에 추가로 입찰하고 싶으신 분께서는 추가 등록하셔도 됩니다.)
        <li> 입찰하고 지우지 못하도록 EP게시판이 아닌 새로운 방법을 정했습니다! 혹시라도 오입력인 경우에만 삭제 도움드리겠습니다.</li>  
        <li> 기본 시작가를 모두 3만원으로 정하였습니다.</li>  
    </ul>  
</div>  
""", unsafe_allow_html=True)    
  
 
# Show overall auction status if "전체 경매 현황" is selected  
elif st.session_state['selected_item_index'] == 'overview':  
    st.markdown("<h1>전체 경매 현황</h1>", unsafe_allow_html=True)  
      
    # Display auction items in a 4-column grid  
    container = st.container()  
    num_items = len(auction_data['auction_items'])  
    items_per_row = 6  # Number of items per row  
    for i in range(0, num_items, items_per_row):  
        cols = container.columns(items_per_row)  
        for idx, item in enumerate(auction_data['auction_items'][i:i+items_per_row]):  
            with cols[idx]:  
                st.markdown(f"###### {item['name']}")  
                st.markdown(f"**현재 입찰가:** {item['current_bid']:,} 원")  
                if os.path.exists(item["image"]):  
                    img = Image.open(item["image"])  
                    img = img.rotate(-90, expand=True)  
                    st.image(img, use_container_width=True, width=200)  
                else:  
                    st.write("이미지를 찾을 수 없습니다.")  
else:  
    # 선택된 아이템 가져오기  
    selected_item_index = st.session_state['selected_item_index']  
    item = auction_data['auction_items'][selected_item_index]  
  
    # 페이지 레이아웃 설정 (두 개의 열로 분할)  
    col1, col2 = st.columns([1, 1])  # 왼쪽과 오른쪽 열의 너비를 동일하게 설정  
  
    with col1:  
        # 페이지 제목  
        st.title(f"{item['name']}")  
  
        # 아이템 이미지 표시  
        if os.path.exists(item["image"]):  
            # 이미지를 PIL로 열기  
            img = Image.open(item["image"])  
            # 이미지를 90도 회전  
            img = img.rotate(-90, expand=True)  
            # 필요한 경우 이미지 회전 등 처리  
            st.image(img, use_container_width=True)  
        else:  
            st.write("이미지를 찾을 수 없습니다.")  
  
    with col2:  
        # 현재 시간 가져오기  
        now = datetime.now()  
  
        # 현재 입찰가 및 경매 종료 시간 표시  
        st.header("경매 정보")  
        st.write(f"**현재 입찰가:** {item['current_bid']:,} 원")  # 천 단위 구분기호 추가  
        st.write(f"**경매 종료 시간:** {item['end_time'].strftime('%Y-%m-%d %H시 %M분 %S초')}")  
        time_remaining = item['end_time'] - now  
        if time_remaining > timedelta(0):  
            days = time_remaining.days  
            hours, remainder = divmod(time_remaining.seconds, 3600)  
            minutes, seconds = divmod(remainder, 60)  
            st.write(f"**남은 시간:** {days}일 {hours}시간 {minutes}분 {seconds}초")  
        else:  
            st.write("**남은 시간:** 경매 종료")  
  
        # 경매 진행 여부 확인  
        auction_active = now < item['end_time']  
  
        if auction_active:  
            st.subheader("입찰하기")  
  
            # 담당 선택  
            departments = [  
                "고객가치혁신담당",  
                "고객가치혁신CS전략담당",  
                "고객가치혁신CS역량개발담당",  
                "고객가치혁신한국서비스담당",  
                "고객가치혁신한국수도권담당",  
                "고객가치혁신한국중부담당",  
                "고객가치혁신한국서남부담당",  
                "고객가치혁신강원서비스실",  
                "고객가치해외서비스지원담당",  
                "고객가치혁신경영관리담당",  
                "고객가치혁신HR담당",  
                "고객접점개선추진실",  
                "고객가치혁신서비스부품지원실",  
                "고객가치혁신정도경영팀",  
            ]  
  
            with st.form("bid_form"):  
                department = st.selectbox("담당", departments)  
                name = st.text_input("이름")  
  
                min_bid = max(30000, item['current_bid'] + 1000)  # 최소 금액 3만원, 입찰 단위 천원  
                new_bid = st.number_input(  
                    "입찰가 입력 (천원 단위)",  
                    min_value=int(min_bid),  
                    step=1000,  
                    format="%d",  
                    help="플러스(+)나 마이너스(-) 버튼을 사용하여 금액을 조정하세요."  
                )  
  
                submit_button = st.form_submit_button("입찰하기")  
  
            if submit_button:  
                if department and name:  
                    # 입찰 정보를 session_state에 저장  
                    st.session_state['pending_bid'] = {  
                        'department': department,  
                        'name': name,  
                        'new_bid': new_bid  
                    }  
                else:  
                    st.error("담당과 이름을 모두 입력해주세요.")  
  
            # pending_bid가 있는지 확인  
            if 'pending_bid' in st.session_state:  
                pending_bid = st.session_state['pending_bid']  
                department = pending_bid['department']  
                name = pending_bid['name']  
                new_bid = pending_bid['new_bid']  
  
                # 확인 메시지 표시  
                confirmation_message = (  
                    f"담당: {department}\n"  
                    f"이름: {name}\n"  
                    f"입찰 금액: {new_bid:,} 원\n\n"  
                    "위의 내용이 정확한지 다시 한 번 확인해주세요."  
                )  
                st.warning(confirmation_message)  
  
                col_confirm, col_cancel = st.columns(2)  
                with col_confirm:  
                    if st.button("✅ 확인"):  
                        now = datetime.now()  # 현재 시간 갱신  
                        # 경매가 아직 진행 중인지 확인  
                        if now >= item['end_time']:  
                            st.error("경매가 종료되었습니다.")  
                        # 현재 입찰가보다 높은지 확인  
                        elif new_bid >= item['current_bid'] + 1000:  
                            # 입찰 기록 추가  
                            bid = {  
                                "department": department,  
                                "name": name,  
                                "amount": new_bid,  
                                "timestamp": now  
                            }  
                            item['bids'].append(bid)  
                            item['current_bid'] = new_bid  
  
                            # 남은 시간이 5분 미만인 경우 종료 시간 연장  
                            time_remaining = item['end_time'] - now  
                            if time_remaining <= timedelta(minutes=5):  
                                item['end_time'] += extend_time  
                                st.write(f"경매 종료 시간이 연장되었습니다: {item['end_time'].strftime('%Y-%m-%d %H시 %M분 %S초')}")  
                            # 경매 데이터 저장  
                            save_auction_data(auction_data)  
                            st.success(f"{item['name']}에 대한 입찰이 성공적으로 이루어졌습니다.")  
                            # pending_bid 제거  
                            del st.session_state['pending_bid']  
                        else:  
                            st.error(f"현재 입찰가보다 높은 금액을 입찰해야 합니다. 현재 입찰가: {item['current_bid']:,} 원")  
                            # pending_bid 제거  
                            del st.session_state['pending_bid']  
                with col_cancel:  
                    if st.button("❌ 취소"):  
                        st.info("입찰이 취소되었습니다.")  
                        del st.session_state['pending_bid']  
  
            else:  
                st.error("담당과 이름을 모두 입력해주세요.")  
  
        else:  
            st.warning("경매가 종료되었습니다.")  
  
        # 입찰 기록 표시  
        if item['bids']:  
            st.subheader("입찰 기록")  
            # 입찰 기록을 시간 순서대로 정렬 (최근 것이 위로)  
            sorted_bids = sorted(item['bids'], key=lambda x: x['timestamp'], reverse=True)  
            for bid in sorted_bids:  
                # 날짜 및 시간 포맷팅  
                bid_time = bid['timestamp'].strftime('%m월 %d일 %H시 %M분')  
                # 이름을 굵게 처리하고 입찰 금액에 천 단위 구분기호 추가  
                st.write(f"[{bid_time}] {bid['department']} **{bid['name']}** {bid['amount']:,}원")  
        else:  
            st.write("아직 입찰 내역이 없습니다.")  
  
  
# 관리자 모드 활성화  
admin_mode = st.sidebar.checkbox("관리자 모드")  
  
if admin_mode:  
    admin_password = st.sidebar.text_input("관리자 비밀번호", type="password")  
    if admin_password == "lge2025!":  # 실제 비밀번호로 변경  
        st.sidebar.success("관리자 모드 활성화됨")  
  
        # 관리자 기능 추가  
        st.header("관리자 기능")  
        # 여기에서 입찰 기록 수정, 삭제 기능 구현  
    else:  
        st.sidebar.error("비밀번호가 올바르지 않습니다.")  
  
# 관리자 모드에서 입찰 기록 관리  
if admin_mode and admin_password == "lge2025!":  
    st.header("입찰 기록 관리")  
  
    for idx, item in enumerate(auction_data['auction_items']):  
        st.subheader(f"아이템: {item['name']}")  
        if item['bids']:  
            for bid_idx, bid in enumerate(item['bids']):  
                bid_time = bid['timestamp'].strftime('%Y-%m-%d %H:%M:%S')  
                st.write(f"{bid_idx + 1}. [{bid_time}] {bid['department']} - {bid['name']} : {bid['amount']:,}원")  
  
                # 수정 및 삭제 버튼  
                col_edit, col_delete = st.columns(2)  
                with col_edit:  
                    if st.button("수정", key=f"edit_{idx}_{bid_idx}"):  
                        # 수정 기능 구현  
                        # 새로운 정보를 입력받아 업데이트  
                        new_department = st.text_input("새로운 담당", value=bid['department'], key=f"dept_{idx}_{bid_idx}")  
                        new_name = st.text_input("새로운 이름", value=bid['name'], key=f"name_{idx}_{bid_idx}")  
                        new_amount = st.number_input("새로운 입찰 금액", min_value=30000, value=bid['amount'], step=1000, key=f"amount_{idx}_{bid_idx}")  
                        if st.button("수정 확인", key=f"confirm_edit_{idx}_{bid_idx}"):  
                            bid['department'] = new_department  
                            bid['name'] = new_name  
                            bid['amount'] = new_amount  
                            # current_bid 업데이트  
                            highest_bid = max(item['bids'], key=lambda x: x['amount'])  
                            item['current_bid'] = highest_bid['amount']  
                            # 데이터 저장  
                            save_auction_data(auction_data)  
                            st.success("입찰 기록이 수정되었습니다.")  
                with col_delete:  
                    if st.button("삭제", key=f"delete_{idx}_{bid_idx}"):  
                        # 해당 입찰 기록 삭제  
                        item['bids'].pop(bid_idx)  
                        st.success("입찰 기록이 삭제되었습니다.")  
                        # current_bid 업데이트 필요  
                        if item['bids']:  
                            highest_bid = max(item['bids'], key=lambda x: x['amount'])  
                            item['current_bid'] = highest_bid['amount']  
                        else:  
                            item['current_bid'] = 30000  # 최소 금액  
                        # 변경된 데이터 저장  
                        save_auction_data(auction_data)  
        else:  
            st.write("입찰 기록이 없습니다.")  
