#!/bin/bash
# 밈 라이브러리 셋업 스크립트 - NCA 서버에서 실행
# MinIO에 밈/리액션 영상을 다운로드, 변환, 업로드

set -e

PEXELS_API_KEY="5JeFfq1nm45j2LesuborcGtbs6wGkagLvY0t9lLmWkNxkHInVxXLCIvi"
MINIO_ALIAS="local"
MINIO_URL="http://localhost:9000"
MINIO_USER="admin"
MINIO_PASS="NcaMin10S3cure!"
BUCKET="memes"
WORK_DIR="/tmp/meme_setup"

# 카테고리별 검색 키워드 (Pexels Video API)
declare -A SEARCH_KEYWORDS
SEARCH_KEYWORDS=(
  ["thinking"]="thinking person,confused cat,curious dog"
  ["excited"]="happy dance,excited puppy,celebration jump"
  ["shocked"]="surprised face,shocked expression,amazed reaction"
  ["sad"]="sad puppy,lonely person,disappointed"
  ["angry"]="angry cat,frustrated person,annoyed"
  ["cool"]="cool sunglasses,confident walk,stylish"
  ["celebrating"]="confetti celebration,winner trophy,cheering crowd"
)

echo "=== 밈 라이브러리 셋업 시작 ==="

# 1. MinIO 설정
echo ""
echo "--- Step 1: MinIO 버킷 설정 ---"
docker exec minio mc alias set $MINIO_ALIAS $MINIO_URL $MINIO_USER $MINIO_PASS 2>/dev/null || true

# 버킷 생성 (이미 있으면 무시)
docker exec minio mc mb $MINIO_ALIAS/$BUCKET 2>/dev/null || echo "  버킷 이미 존재"

# 퍼블릭 다운로드 정책 설정
docker exec minio mc anonymous set download $MINIO_ALIAS/$BUCKET
echo "  MinIO 버킷 '$BUCKET' 퍼블릭 설정 완료"

# 2. 작업 디렉토리 준비
echo ""
echo "--- Step 2: 작업 디렉토리 준비 ---"
mkdir -p $WORK_DIR
cd $WORK_DIR

for category in thinking excited shocked sad angry cool celebrating; do
  mkdir -p $WORK_DIR/$category
done
echo "  카테고리 디렉토리 생성 완료"

# 3. Pexels Video API로 영상 다운로드 + FFmpeg 변환
echo ""
echo "--- Step 3: 밈 영상 다운로드 및 변환 ---"

download_count=0
fail_count=0

for category in thinking excited shocked sad angry cool celebrating; do
  echo ""
  echo "  [$category] 처리 중..."

  IFS=',' read -ra keywords <<< "${SEARCH_KEYWORDS[$category]}"
  file_idx=1

  for keyword in "${keywords[@]}"; do
    keyword=$(echo "$keyword" | xargs)  # trim whitespace
    echo "    검색: '$keyword'"

    # Pexels Video API 호출
    response=$(curl -s -H "Authorization: $PEXELS_API_KEY" \
      "https://api.pexels.com/videos/search?query=$(echo $keyword | sed 's/ /%20/g')&per_page=1&orientation=portrait&size=small" 2>/dev/null)

    # 비디오 URL 추출 (가장 작은 해상도)
    video_url=$(echo "$response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    videos = data.get('videos', [])
    if videos:
        files = videos[0].get('video_files', [])
        # SD 해상도 우선, 없으면 첫번째
        best = None
        for f in files:
            if f.get('quality') == 'sd':
                best = f['link']
                break
        if not best and files:
            best = files[0]['link']
        print(best or '')
except:
    print('')
" 2>/dev/null)

    if [ -z "$video_url" ]; then
      echo "    [SKIP] 영상 없음: $keyword"
      fail_count=$((fail_count + 1))
      continue
    fi

    raw_file="$WORK_DIR/$category/raw_${file_idx}.mp4"
    out_file="$WORK_DIR/$category/meme_${category}_$(printf '%02d' $file_idx).mp4"

    # 다운로드
    echo "    다운로드 중..."
    curl -sL -o "$raw_file" "$video_url" 2>/dev/null

    if [ ! -s "$raw_file" ]; then
      echo "    [SKIP] 다운로드 실패"
      fail_count=$((fail_count + 1))
      continue
    fi

    # FFmpeg 변환 (1080x1920, 30fps, h264, 무음, 최대 4초)
    echo "    변환 중..."
    ffmpeg -y -i "$raw_file" \
      -c:v libx264 -pix_fmt yuv420p -r 30 \
      -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black" \
      -an -t 4 -movflags +faststart \
      "$out_file" 2>/dev/null

    if [ -s "$out_file" ]; then
      echo "    변환 완료: $(basename $out_file) ($(du -h $out_file | cut -f1))"

      # MinIO 업로드
      docker exec minio mc cp "/tmp/meme_setup/$category/$(basename $out_file)" \
        $MINIO_ALIAS/$BUCKET/$category/$(basename $out_file) 2>/dev/null || \
      echo "    [WARN] mc cp 실패, 직접 업로드 시도"

      download_count=$((download_count + 1))
    else
      echo "    [SKIP] 변환 실패"
      fail_count=$((fail_count + 1))
    fi

    # raw 파일 삭제
    rm -f "$raw_file"

    file_idx=$((file_idx + 1))

    # API 속도 제한 방지
    sleep 1
  done
done

echo ""
echo "--- Step 4: MinIO 업로드 ---"

# MinIO 컨테이너에서 직접 접근 불가할 수 있으므로 curl S3 API 사용
for category in thinking excited shocked sad angry cool celebrating; do
  for file in $WORK_DIR/$category/meme_*.mp4; do
    [ -f "$file" ] || continue
    fname=$(basename "$file")

    # MinIO에 직접 PUT (pre-signed 없이 public bucket이므로)
    # mc를 호스트에서 사용할 수 없으므로 docker exec + volume mount 필요
    # /tmp는 컨테이너와 공유되지 않을 수 있음 → 파이프로 전송
    cat "$file" | docker exec -i minio mc pipe $MINIO_ALIAS/$BUCKET/$category/$fname 2>/dev/null

    if [ $? -eq 0 ]; then
      echo "  업로드: $category/$fname"
    else
      echo "  [WARN] 업로드 실패: $category/$fname - curl 방식 시도"
      # curl S3 PUT 대안
      curl -s -X PUT \
        -H "Content-Type: video/mp4" \
        --data-binary @"$file" \
        "http://localhost:9000/$BUCKET/$category/$fname" 2>/dev/null || echo "  [ERROR] curl PUT도 실패"
    fi
  done
done

echo ""
echo "--- Step 5: 접근 확인 ---"

# 업로드된 파일 목록
echo "  MinIO 파일 목록:"
docker exec minio mc ls --recursive $MINIO_ALIAS/$BUCKET/ 2>/dev/null

echo ""
echo "  접근 테스트:"
# 첫 번째 파일로 curl 테스트
test_file=$(docker exec minio mc ls --recursive $MINIO_ALIAS/$BUCKET/ 2>/dev/null | head -1 | awk '{print $NF}')
if [ -n "$test_file" ]; then
  status=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:9000/$BUCKET/$test_file")
  echo "  curl http://localhost:9000/$BUCKET/$test_file → HTTP $status"

  # 외부 접근 테스트
  ext_status=$(curl -s -o /dev/null -w "%{http_code}" "http://76.13.182.180:9000/$BUCKET/$test_file" 2>/dev/null || echo "timeout")
  echo "  외부 접근: http://76.13.182.180:9000/$BUCKET/$test_file → HTTP $ext_status"
fi

echo ""
echo "=== 밈 라이브러리 셋업 완료 ==="
echo "  다운로드: $download_count개"
echo "  실패: $fail_count개"
echo "  URL 형식: http://76.13.182.180:9000/memes/{category}/{filename}.mp4"

# 정리
rm -rf $WORK_DIR
echo "  작업 디렉토리 정리 완료"
