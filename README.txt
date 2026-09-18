분양노크 OpenChat Funnel FINAL

포함 기능
- 카카오톡/Open Graph 링크 미리보기
- 1200x630 대표 이미지
- 분양노크 랜딩페이지
- 카카오 오픈채팅 연결
- 유입코드별 방문/클릭/전환율
- 캠페인 생성
- 오늘/7일/30일 통계
- CSV 다운로드
- 관리자 비밀번호 로그인
- Render 설정

배포 전 Render Environment에 ADMIN_PASSWORD를 반드시 설정하세요.
COOKIE_SECRET도 Render 환경변수로 설정하거나 render.yaml generateValue를 사용하세요.

기존 GitHub 저장소에서 이전 앱 파일을 이 패키지 내용으로 교체한 뒤 main에 push하면 됩니다.
주의: Render 무료 인스턴스의 로컬 SQLite 파일은 영구 저장을 보장하지 않습니다. 장기 운영 통계는 추후 Postgres로 이전하는 것을 권장합니다.
카카오톡은 링크 미리보기를 캐시할 수 있습니다. 배포 후 테스트할 때 /go/test-날짜처럼 새 URL을 사용하면 새 카드 확인이 쉽습니다.
