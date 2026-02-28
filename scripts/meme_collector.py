#!/usr/bin/env python3
"""
온카스터디 밈 자동 수집 v2 (GIPHY API)
- GIPHY API로 한국 정서 맞는 움직이는 밈(mp4) 다운로드
- MinIO에 자동 업로드
- MEME_CATALOG 업데이트용 코드 자동 생성
"""

import os
import json
import time
import hashlib
import requests
from pathlib import Path
from urllib.parse import quote

# ============================================================
# 설정
# ============================================================

GIPHY_API_KEY = os.environ.get('GIPHY_API_KEY', '')
MINIO_ENDPOINT = '76.13.182.180:9000'
MINIO_ACCESS_KEY = 'admin'
MINIO_SECRET_KEY = 'NcaMin10S3cure!'
MINIO_BUCKET = 'memes'
MINIO_BASE_URL = f'http://{MINIO_ENDPOINT}/{MINIO_BUCKET}'

DOWNLOAD_DIR = Path('./meme_downloads')
DOWNLOAD_DIR.mkdir(exist_ok=True)

# ============================================================
# 수집 계획: mood별 검색 키워드 (한국 정서 + 글로벌 밈)
# ============================================================

MEME_SEARCH_PLAN = {
    # ===== 부족한 카테고리 (현재 1~4개) =====
    'snacking': {
        'current': 1, 'target': 6,
        'queries': ['eating popcorn reaction', 'snacking watching', 'mukbang reaction', 'eating chips drama', 'popcorn movie watching'],
    },
    'smoking': {
        'current': 1, 'target': 5,
        'queries': ['stressed smoking', 'thinking smoking', 'anime smoking cool', 'tired smoking reaction'],
    },
    'disappointed': {
        'current': 2, 'target': 7,
        'queries': ['disappointed reaction', 'facepalm reaction', 'shaking head no', 'so disappointed', 'sigh disappointed'],
    },
    'thumbsup': {
        'current': 2, 'target': 6,
        'queries': ['thumbs up reaction', 'good job approve', 'nice thumbsup', 'ok great reaction'],
    },
    'crying': {
        'current': 4, 'target': 8,
        'queries': ['crying reaction funny', 'sobbing sad', 'tears streaming reaction', 'ugly crying funny'],
    },
    'desperate': {
        'current': 4, 'target': 8,
        'queries': ['desperate panic', 'everything is fine fire', 'stressed panic reaction', 'mental breakdown funny'],
    },
    'bored': {
        'current': 3, 'target': 7,
        'queries': ['bored reaction', 'so bored yawn', 'waiting bored reaction', 'boring sigh'],
    },

    # ===== 중간 카테고리 mp4 보강 =====
    'speechless': {
        'current': 6, 'target': 9,
        'queries': ['speechless shocked', 'no words reaction', 'jaw drop shocked'],
    },
    'money': {
        'current': 8, 'target': 11,
        'queries': ['money rain rich', 'make it rain money', 'counting money reaction'],
    },
    'suspicious': {
        'current': 8, 'target': 11,
        'queries': ['suspicious look reaction', 'side eye suspicious', 'squinting suspicious'],
    },
    'celebrating': {
        'current': 7, 'target': 10,
        'queries': ['celebration dance', 'party celebrating', 'victory celebration reaction'],
    },

    # ===== 새 mood 카테고리 =====
    'laughing': {
        'current': 0, 'target': 8,
        'queries': ['laughing hard reaction', 'dying laughing', 'wheeze laugh', 'cant stop laughing', 'LOL reaction funny', 'laughing crying'],
    },
    'confident': {
        'current': 0, 'target': 6,
        'queries': ['confident walk boss', 'like a boss swagger', 'cool entrance reaction', 'confidence walk'],
    },
    'scared': {
        'current': 0, 'target': 6,
        'queries': ['scared reaction funny', 'terrified running away', 'horror scared', 'screaming scared reaction'],
    },
}


def search_giphy(query, limit=5):
    """GIPHY API로 GIF 검색. mp4 렌더링 URL 반환."""
    if not GIPHY_API_KEY:
        print(f"  ⚠️  GIPHY API 키 없음 - '{query}' 스킵")
        return []

    url = 'https://api.giphy.com/v1/gifs/search'
    params = {
        'api_key': GIPHY_API_KEY,
        'q': query,
        'limit': limit,
        'rating': 'pg-13',
        'lang': 'en',
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        results = []
        for item in data.get('data', []):
            images = item.get('images', {})
            # mp4 우선 (original_mp4 → looping → fixed_width_small)
            mp4_url = ''
            if 'original_mp4' in images and images['original_mp4'].get('mp4'):
                mp4_url = images['original_mp4']['mp4']
            elif 'looping' in images and images['looping'].get('mp4'):
                mp4_url = images['looping']['mp4']
            elif 'fixed_width' in images and images['fixed_width'].get('mp4'):
                mp4_url = images['fixed_width']['mp4']

            # gif fallback
            gif_url = ''
            if 'downsized' in images and images['downsized'].get('url'):
                gif_url = images['downsized']['url']
            elif 'original' in images and images['original'].get('url'):
                gif_url = images['original']['url']

            if mp4_url:
                results.append({'url': mp4_url, 'ext': 'mp4', 'id': item.get('id', '')})
            elif gif_url:
                results.append({'url': gif_url, 'ext': 'gif', 'id': item.get('id', '')})

        return results
    except Exception as e:
        print(f"  ❌ GIPHY 검색 실패 ({query}): {e}")
        return []


def download_file(url, save_path):
    """파일 다운로드"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, timeout=30, stream=True, headers=headers)
        resp.raise_for_status()
        with open(save_path, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        size_kb = os.path.getsize(save_path) // 1024
        # 너무 작은 파일(1KB 미만)이나 에러 페이지는 삭제
        if size_kb < 1:
            os.remove(save_path)
            return False
        print(f"    ✅ 저장: {save_path.name} ({size_kb}KB)")
        return True
    except Exception as e:
        print(f"    ❌ 다운로드 실패: {e}")
        return False


def upload_to_minio(local_path, remote_path):
    """MinIO에 업로드"""
    try:
        from minio import Minio
        client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=False
        )

        ext = str(local_path).rsplit('.', 1)[-1].lower()
        content_types = {'mp4': 'video/mp4', 'gif': 'image/gif', 'jpg': 'image/jpeg', 'png': 'image/png'}
        ct = content_types.get(ext, 'application/octet-stream')

        client.fput_object(MINIO_BUCKET, remote_path, str(local_path), content_type=ct)
        final_url = f'{MINIO_BASE_URL}/{quote(remote_path)}'
        return final_url
    except ImportError:
        print("    ⚠️  minio 패키지 없음. pip3 install minio")
        return None
    except Exception as e:
        print(f"    ❌ MinIO 업로드 실패: {e}")
        return None


def collect_all():
    """전체 수집 실행"""
    all_updates = {}
    seen_ids = set()  # GIPHY 중복 방지

    for mood, plan in MEME_SEARCH_PLAN.items():
        needed = plan['target'] - plan['current']
        if needed <= 0:
            continue

        print(f"\n{'='*50}")
        print(f"📁 {mood} | 현재 {plan['current']}개 → 목표 {plan['target']}개 | +{needed}개 수집")
        print(f"{'='*50}")

        mood_dir = DOWNLOAD_DIR / mood
        mood_dir.mkdir(exist_ok=True)
        collected = []

        for query in plan.get('queries', []):
            if len(collected) >= needed:
                break

            print(f"  🔍 검색: '{query}'")
            results = search_giphy(query, limit=4)

            for r in results:
                if len(collected) >= needed:
                    break
                if r['id'] in seen_ids:
                    continue
                seen_ids.add(r['id'])

                filename = f"meme_{mood}_{r['id'][:12]}.{r['ext']}"
                save_path = mood_dir / filename

                if save_path.exists():
                    collected.append(save_path)
                    continue

                if download_file(r['url'], save_path):
                    collected.append(save_path)

                time.sleep(0.3)

        # MinIO 업로드
        uploaded = []
        for f in collected:
            remote = f"{mood}/{f.name}"
            url = upload_to_minio(f, remote)
            if url:
                uploaded.append({'url': url, 'is_video': f.suffix == '.mp4'})
                print(f"    🚀 업로드: {url}")

        if uploaded:
            all_updates[mood] = uploaded

    return all_updates


def generate_catalog_update(updates):
    """MEME_CATALOG 업데이트 코드 + JSON 생성"""

    # 1) JS 코드 스니펫
    js_path = DOWNLOAD_DIR / 'meme_catalog_update.js'
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write("// ====================================================\n")
        f.write("// MEME_CATALOG 업데이트 (이미지 URL 추출 노드에 추가)\n")
        f.write(f"// 생성일: {time.strftime('%Y-%m-%d %H:%M')}\n")
        f.write("// ====================================================\n\n")

        new_moods = []
        existing_moods = []

        for mood, items in updates.items():
            if MEME_SEARCH_PLAN[mood]['current'] == 0:
                new_moods.append(mood)
            else:
                existing_moods.append(mood)

        if existing_moods:
            f.write("// === 기존 mood에 추가할 URL ===\n\n")
            for mood in existing_moods:
                f.write(f"// {mood}: +{len(updates[mood])}개 추가 (기존 배열 끝에 추가)\n")
                for item in updates[mood]:
                    f.write(f"    '{item['url']}',\n")
                f.write("\n")

        if new_moods:
            f.write("// === 새 mood 카테고리 (MEME_CATALOG에 새 키 추가) ===\n\n")
            for mood in new_moods:
                f.write(f"  {mood}: [\n")
                for item in updates[mood]:
                    f.write(f"    '{item['url']}',\n")
                f.write(f"  ],\n\n")

    # 2) JSON
    json_path = DOWNLOAD_DIR / 'meme_catalog_update.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(updates, f, ensure_ascii=False, indent=2)

    print(f"\n📄 JS 코드: {js_path}")
    print(f"📄 JSON: {json_path}")
    return js_path, json_path


def print_plan():
    """수집 계획 요약"""
    print("\n" + "="*60)
    print("📊 밈 수집 계획 (GIPHY API v2)")
    print("="*60)
    total = 0
    for mood, plan in MEME_SEARCH_PLAN.items():
        needed = max(0, plan['target'] - plan['current'])
        total += needed
        tag = "🆕 새 카테고리" if plan['current'] == 0 else f"보강 ({plan['current']}→{plan['target']})"
        print(f"  {mood:15s} | {tag:25s} | +{needed}개")
    print(f"\n  📦 총 {total}개 밈 수집 예정")
    print(f"  🔑 GIPHY API Key: {'설정됨 ✅' if GIPHY_API_KEY else '없음 ❌'}")
    print(f"  💾 MinIO: {MINIO_ENDPOINT}")
    print("="*60)


if __name__ == '__main__':
    print_plan()

    if not GIPHY_API_KEY:
        print("\n⚠️  GIPHY_API_KEY가 설정되지 않았습니다!")
        print("  export GIPHY_API_KEY='your-api-key'")
        print("  발급: https://developers.giphy.com/ → Create App → API 선택")
        exit(1)

    if not MINIO_ACCESS_KEY:
        print("\n⚠️  MinIO 접속 정보 필요!")
        print("  export MINIO_ACCESS_KEY='...'")
        print("  export MINIO_SECRET_KEY='...'")
        exit(1)

    updates = collect_all()

    if updates:
        js_path, json_path = generate_catalog_update(updates)
        total = sum(len(v) for v in updates.values())
        print(f"\n✅ 완료! {total}개 밈 수집/업로드됨")
        print(f"\n📌 다음 단계:")
        print(f"  1. meme_downloads/ 에서 밈 확인 (마음에 안 드는 건 삭제)")
        print(f"  2. {js_path} 코드를 MEME_CATALOG에 추가")
        print(f"  3. 콘텐츠 파싱 노드 VALID_MOODS에 새 mood 추가")
        print(f"  4. 프롬프트 생성 노드에 새 mood 추가")
    else:
        print("\n⚠️  수집된 밈 없음")
