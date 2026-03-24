미샵 SEO 생성기 UI 가독성 수정 패치

수정 내용
- 결과 입력창 상단 타이틀이 배경색과 겹쳐 안 보이던 문제 수정
- 결과 타이틀을 별도 라벨 박스로 강하게 표시
- 기존 UI 흐름 유지, 내용과 가시성만 보정

적용 방법
1) ZIP 압축 해제
2) 기존 레포 기준 apps/seo/app.py 덮어쓰기
3) Commit → Push → Streamlit Reboot
