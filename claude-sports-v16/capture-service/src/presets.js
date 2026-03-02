'use strict';

/**
 * capture_id → 캡처 설정 매핑 (20개 프리셋)
 *
 * Phase 1: 모든 프리셋은 해당 페이지 전체 뷰포트 캡처 (1080x1920)
 * Phase 2 (추후): DOM 확인 후 CSS 셀렉터 기반 엘리먼트 캡처로 전환
 *
 * @type {Object.<string, {path: string, description: string, waitFor?: string}>}
 */
const PRESETS = {
  // === 홈 페이지 (/) ===
  home_full_page: {
    path: '/',
    description: '홈 페이지 전체',
  },
  home_live_scores: {
    path: '/',
    description: '홈 실시간 스코어 영역',
  },
  home_popular_matches: {
    path: '/',
    description: '홈 인기 경기 영역',
  },
  home_banner: {
    path: '/',
    description: '홈 배너 영역',
  },
  home_schedule: {
    path: '/',
    description: '홈 경기 일정 영역',
  },

  // === 분석 페이지 (/analysis) ===
  analysis_full_page: {
    path: '/analysis',
    description: '분석 페이지 전체',
  },
  analysis_stats: {
    path: '/analysis',
    description: '분석 통계 영역',
  },
  analysis_prediction: {
    path: '/analysis',
    description: '분석 예측 영역',
  },
  analysis_form_guide: {
    path: '/analysis',
    description: '분석 폼 가이드 영역',
  },
  analysis_head_to_head: {
    path: '/analysis',
    description: '분석 상대전적 영역',
  },

  // === 프로토 페이지 (/proto) ===
  proto_full_page: {
    path: '/proto',
    description: '프로토 페이지 전체',
  },
  proto_picks: {
    path: '/proto',
    description: '프로토 픽 목록 영역',
  },
  proto_odds: {
    path: '/proto',
    description: '프로토 배당률 영역',
  },
  proto_results: {
    path: '/proto',
    description: '프로토 결과 영역',
  },
  proto_trending: {
    path: '/proto',
    description: '프로토 트렌딩 영역',
  },

  // === 커뮤니티 페이지 (/community) ===
  community_full_page: {
    path: '/community',
    description: '커뮤니티 페이지 전체',
  },
  community_hot_posts: {
    path: '/community',
    description: '커뮤니티 인기 게시물 영역',
  },
  community_free_board: {
    path: '/community',
    description: '커뮤니티 자유게시판 영역',
  },
  community_tips: {
    path: '/community',
    description: '커뮤니티 팁 게시판 영역',
  },
  community_events: {
    path: '/community',
    description: '커뮤니티 이벤트 영역',
  },
};

/**
 * capture_id로 프리셋 설정을 가져옴
 * @param {string} captureId - 프리셋 ID
 * @returns {Object|null} 프리셋 설정 또는 null
 */
function getPreset(captureId) {
  return PRESETS[captureId] || null;
}

/**
 * 모든 프리셋 ID 목록 반환
 * @returns {string[]}
 */
function listPresetIds() {
  return Object.keys(PRESETS);
}

module.exports = { PRESETS, getPreset, listPresetIds };
