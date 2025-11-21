#!/usr/bin/env python3
"""
User Activity Analytics for CodeXam Platform

This module provides comprehensive user activity tracking and analytics:
- User behavior pattern analysis
- Session tracking and duration analysis
- Feature usage statistics
- Performance impact analysis
- Conversion funnel tracking

Version: 2.0.0
Author: CodeXam Development Team
"""

import sqlite3
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import hashlib
import threading

logger = logging.getLogger(__name__)


@dataclass
class UserSession:
    """User session information."""
    session_id: str
    user_id: str
    start_time: float
    end_time: Optional[float]
    page_views: int
    actions: int
    duration: Optional[float]
    entry_page: str
    exit_page: Optional[str]
    user_agent: str
    ip_address: str


@dataclass
class PageAnalytics:
    """Page-specific analytics."""
    page: str
    views: int
    unique_visitors: int
    avg_time_on_page: float
    bounce_rate: float
    exit_rate: float


@dataclass
class UserBehaviorPattern:
    """User behavior pattern analysis."""
    pattern_id: str
    pattern_type: str
    frequency: int
    avg_duration: float
    success_rate: float
    common_paths: List[str]


class UserAnalytics:
    """User activity analytics system."""
    
    def __init__(self, db_path: str = 'monitoring.db'):
        self.db_path = db_path
        self.lock = threading.RLock()
        
        # Initialize analytics database
        self._init_analytics_db()
        
        logger.info("User analytics system initialized")
    
    def _init_analytics_db(self):
        """Initialize analytics database tables."""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # User sessions table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    start_time REAL NOT NULL,
                    end_time REAL,
                    page_views INTEGER DEFAULT 0,
                    actions INTEGER DEFAULT 0,
                    duration REAL,
                    entry_page TEXT,
                    exit_page TEXT,
                    user_agent TEXT,
                    ip_address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Page analytics table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS page_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    page TEXT NOT NULL,
                    date TEXT NOT NULL,
                    views INTEGER DEFAULT 0,
                    unique_visitors INTEGER DEFAULT 0,
                    total_time REAL DEFAULT 0,
                    bounces INTEGER DEFAULT 0,
                    exits INTEGER DEFAULT 0,
                    UNIQUE(page, date)
                )
            ''')
            
            # User behavior patterns table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS behavior_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_id TEXT NOT NULL,
                    pattern_type TEXT NOT NULL,
                    user_id TEXT,
                    session_id TEXT,
                    sequence TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    duration REAL,
                    success BOOLEAN DEFAULT FALSE
                )
            ''')
            
            # Feature usage table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS feature_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    feature_name TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    usage_count INTEGER DEFAULT 1,
                    total_time REAL DEFAULT 0,
                    success_count INTEGER DEFAULT 0,
                    error_count INTEGER DEFAULT 0,
                    timestamp REAL NOT NULL
                )
            ''')
            
            # Create indexes
            conn.execute('CREATE INDEX IF NOT EXISTS idx_sessions_user ON user_sessions(user_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_sessions_start ON user_sessions(start_time)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_page_analytics_date ON page_analytics(date)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_patterns_user ON behavior_patterns(user_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_feature_usage_feature ON feature_usage(feature_name)')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to initialize analytics database: {e}")
    
    def start_session(self, session_id: str, user_id: str, entry_page: str,
                     user_agent: str = '', ip_address: str = '') -> None:
        """Start tracking a user session."""
        try:
            conn = sqlite3.connect(self.db_path)
            
            conn.execute('''
                INSERT OR REPLACE INTO user_sessions 
                (session_id, user_id, start_time, entry_page, user_agent, ip_address, page_views, actions)
                VALUES (?, ?, ?, ?, ?, ?, 1, 0)
            ''', (session_id, user_id, time.time(), entry_page, user_agent, ip_address))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to start session: {e}")
    
    def end_session(self, session_id: str, exit_page: str) -> None:
        """End a user session."""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get session start time
            cursor = conn.execute(
                'SELECT start_time FROM user_sessions WHERE session_id = ?',
                (session_id,)
            )
            result = cursor.fetchone()
            
            if result:
                start_time = result[0]
                end_time = time.time()
                duration = end_time - start_time
                
                conn.execute('''
                    UPDATE user_sessions 
                    SET end_time = ?, duration = ?, exit_page = ?
                    WHERE session_id = ?
                ''', (end_time, duration, exit_page, session_id))
                
                conn.commit()
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to end session: {e}")
    
    def track_page_view(self, session_id: str, page: str, time_on_page: float = 0) -> None:
        """Track a page view."""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Update session page views
            conn.execute('''
                UPDATE user_sessions 
                SET page_views = page_views + 1
                WHERE session_id = ?
            ''', (session_id,))
            
            # Update daily page analytics
            today = datetime.now().strftime('%Y-%m-%d')
            
            conn.execute('''
                INSERT OR IGNORE INTO page_analytics (page, date, views, unique_visitors, total_time)
                VALUES (?, ?, 0, 0, 0)
            ''', (page, today))
            
            conn.execute('''
                UPDATE page_analytics 
                SET views = views + 1, total_time = total_time + ?
                WHERE page = ? AND date = ?
            ''', (time_on_page, page, today))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to track page view: {e}")
    
    def track_user_action(self, session_id: str, action: str, feature: str = '',
                         duration: float = 0, success: bool = True) -> None:
        """Track a user action."""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Update session actions
            conn.execute('''
                UPDATE user_sessions 
                SET actions = actions + 1
                WHERE session_id = ?
            ''', (session_id,))
            
            # Track feature usage if specified
            if feature:
                # Get user_id from session
                cursor = conn.execute(
                    'SELECT user_id FROM user_sessions WHERE session_id = ?',
                    (session_id,)
                )
                result = cursor.fetchone()
                
                if result:
                    user_id = result[0]
                    
                    conn.execute('''
                        INSERT INTO feature_usage 
                        (feature_name, user_id, session_id, total_time, success_count, error_count, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(feature_name, user_id, session_id) DO UPDATE SET
                        usage_count = usage_count + 1,
                        total_time = total_time + ?,
                        success_count = success_count + ?,
                        error_count = error_count + ?
                    ''', (
                        feature, user_id, session_id, duration,
                        1 if success else 0, 0 if success else 1, time.time(),
                        duration, 1 if success else 0, 0 if success else 1
                    ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to track user action: {e}")
    
    def track_behavior_pattern(self, user_id: str, session_id: str, 
                              pattern_type: str, sequence: List[str],
                              duration: float = 0, success: bool = False) -> None:
        """Track user behavior patterns."""
        try:
            pattern_id = hashlib.md5(
                f"{pattern_type}:{':'.join(sequence)}".encode()
            ).hexdigest()[:8]
            
            conn = sqlite3.connect(self.db_path)
            
            conn.execute('''
                INSERT INTO behavior_patterns 
                (pattern_id, pattern_type, user_id, session_id, sequence, timestamp, duration, success)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                pattern_id, pattern_type, user_id, session_id,
                json.dumps(sequence), time.time(), duration, success
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to track behavior pattern: {e}")
    
    def get_user_sessions(self, user_id: str = None, hours: int = 24) -> List[UserSession]:
        """Get user sessions within the specified time period."""
        cutoff_time = time.time() - (hours * 3600)
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            if user_id:
                cursor = conn.execute('''
                    SELECT session_id, user_id, start_time, end_time, page_views, actions,
                           duration, entry_page, exit_page, user_agent, ip_address
                    FROM user_sessions
                    WHERE user_id = ? AND start_time > ?
                    ORDER BY start_time DESC
                ''', (user_id, cutoff_time))
            else:
                cursor = conn.execute('''
                    SELECT session_id, user_id, start_time, end_time, page_views, actions,
                           duration, entry_page, exit_page, user_agent, ip_address
                    FROM user_sessions
                    WHERE start_time > ?
                    ORDER BY start_time DESC
                ''', (cutoff_time,))
            
            sessions = []
            for row in cursor.fetchall():
                sessions.append(UserSession(
                    session_id=row[0],
                    user_id=row[1],
                    start_time=row[2],
                    end_time=row[3],
                    page_views=row[4],
                    actions=row[5],
                    duration=row[6],
                    entry_page=row[7],
                    exit_page=row[8],
                    user_agent=row[9],
                    ip_address=row[10]
                ))
            
            conn.close()
            return sessions
            
        except Exception as e:
            logger.error(f"Failed to get user sessions: {e}")
            return []
    
    def get_page_analytics(self, days: int = 7) -> List[PageAnalytics]:
        """Get page analytics for the specified number of days."""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            cursor = conn.execute('''
                SELECT page, SUM(views) as total_views, 
                       COUNT(DISTINCT date) as days_active,
                       SUM(total_time) as total_time,
                       SUM(bounces) as total_bounces,
                       SUM(exits) as total_exits
                FROM page_analytics
                WHERE date >= ? AND date <= ?
                GROUP BY page
                ORDER BY total_views DESC
            ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
            
            analytics = []
            for row in cursor.fetchall():
                page, views, days_active, total_time, bounces, exits = row
                
                # Calculate metrics
                avg_time_on_page = (total_time / views) if views > 0 else 0
                bounce_rate = (bounces / views * 100) if views > 0 else 0
                exit_rate = (exits / views * 100) if views > 0 else 0
                
                # Estimate unique visitors (simplified)
                unique_visitors = max(1, int(views * 0.7))  # Rough estimate
                
                analytics.append(PageAnalytics(
                    page=page,
                    views=views,
                    unique_visitors=unique_visitors,
                    avg_time_on_page=avg_time_on_page,
                    bounce_rate=bounce_rate,
                    exit_rate=exit_rate
                ))
            
            conn.close()
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get page analytics: {e}")
            return []
    
    def get_behavior_patterns(self, pattern_type: str = None, days: int = 7) -> List[UserBehaviorPattern]:
        """Get user behavior patterns."""
        cutoff_time = time.time() - (days * 24 * 3600)
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            if pattern_type:
                cursor = conn.execute('''
                    SELECT pattern_id, pattern_type, COUNT(*) as frequency,
                           AVG(duration) as avg_duration, 
                           SUM(CASE WHEN success THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as success_rate,
                           GROUP_CONCAT(sequence) as sequences
                    FROM behavior_patterns
                    WHERE pattern_type = ? AND timestamp > ?
                    GROUP BY pattern_id, pattern_type
                    ORDER BY frequency DESC
                ''', (pattern_type, cutoff_time))
            else:
                cursor = conn.execute('''
                    SELECT pattern_id, pattern_type, COUNT(*) as frequency,
                           AVG(duration) as avg_duration,
                           SUM(CASE WHEN success THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as success_rate,
                           GROUP_CONCAT(sequence) as sequences
                    FROM behavior_patterns
                    WHERE timestamp > ?
                    GROUP BY pattern_id, pattern_type
                    ORDER BY frequency DESC
                ''', (cutoff_time,))
            
            patterns = []
            for row in cursor.fetchall():
                pattern_id, ptype, frequency, avg_duration, success_rate, sequences = row
                
                # Extract common paths from sequences
                common_paths = []
                if sequences:
                    sequence_list = sequences.split(',')
                    path_counter = Counter()
                    for seq in sequence_list[:10]:  # Limit to first 10
                        try:
                            path = json.loads(seq)
                            path_counter[' -> '.join(path)] += 1
                        except:
                            continue
                    common_paths = [path for path, count in path_counter.most_common(3)]
                
                patterns.append(UserBehaviorPattern(
                    pattern_id=pattern_id,
                    pattern_type=ptype,
                    frequency=frequency,
                    avg_duration=avg_duration or 0,
                    success_rate=success_rate or 0,
                    common_paths=common_paths
                ))
            
            conn.close()
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to get behavior patterns: {e}")
            return []
    
    def get_feature_usage_stats(self, days: int = 7) -> Dict[str, Any]:
        """Get feature usage statistics."""
        cutoff_time = time.time() - (days * 24 * 3600)
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Feature usage summary
            cursor = conn.execute('''
                SELECT feature_name, 
                       COUNT(DISTINCT user_id) as unique_users,
                       SUM(usage_count) as total_usage,
                       AVG(total_time) as avg_time_per_use,
                       SUM(success_count) as total_success,
                       SUM(error_count) as total_errors
                FROM feature_usage
                WHERE timestamp > ?
                GROUP BY feature_name
                ORDER BY total_usage DESC
            ''', (cutoff_time,))
            
            feature_stats = []
            for row in cursor.fetchall():
                feature, unique_users, total_usage, avg_time, success, errors = row
                
                success_rate = (success / (success + errors) * 100) if (success + errors) > 0 else 0
                
                feature_stats.append({
                    'feature': feature,
                    'unique_users': unique_users,
                    'total_usage': total_usage,
                    'avg_time_per_use': avg_time or 0,
                    'success_rate': success_rate,
                    'total_errors': errors
                })
            
            # Most active users
            cursor = conn.execute('''
                SELECT user_id, COUNT(DISTINCT feature_name) as features_used,
                       SUM(usage_count) as total_actions
                FROM feature_usage
                WHERE timestamp > ?
                GROUP BY user_id
                ORDER BY total_actions DESC
                LIMIT 10
            ''', (cutoff_time,))
            
            active_users = [
                {
                    'user_id': row[0],
                    'features_used': row[1],
                    'total_actions': row[2]
                }
                for row in cursor.fetchall()
            ]
            
            conn.close()
            
            return {
                'feature_stats': feature_stats,
                'active_users': active_users,
                'period_days': days
            }
            
        except Exception as e:
            logger.error(f"Failed to get feature usage stats: {e}")
            return {}
    
    def get_conversion_funnel(self, funnel_steps: List[str], days: int = 7) -> Dict[str, Any]:
        """Analyze conversion funnel for specified steps."""
        cutoff_time = time.time() - (days * 24 * 3600)
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            funnel_data = {}
            total_users = 0
            
            for i, step in enumerate(funnel_steps):
                if i == 0:
                    # First step - count all users who performed this action
                    cursor = conn.execute('''
                        SELECT COUNT(DISTINCT user_id) as user_count
                        FROM user_activities
                        WHERE action = ? AND timestamp > ?
                    ''', (step, cutoff_time))
                    
                    result = cursor.fetchone()
                    user_count = result[0] if result else 0
                    total_users = user_count
                    
                else:
                    # Subsequent steps - count users who performed previous step AND this step
                    prev_step = funnel_steps[i-1]
                    
                    cursor = conn.execute('''
                        SELECT COUNT(DISTINCT u1.user_id) as user_count
                        FROM user_activities u1
                        INNER JOIN user_activities u2 ON u1.user_id = u2.user_id
                        WHERE u1.action = ? AND u2.action = ? 
                        AND u1.timestamp > ? AND u2.timestamp > u1.timestamp
                    ''', (prev_step, step, cutoff_time))
                    
                    result = cursor.fetchone()
                    user_count = result[0] if result else 0
                
                conversion_rate = (user_count / total_users * 100) if total_users > 0 else 0
                
                funnel_data[step] = {
                    'users': user_count,
                    'conversion_rate': conversion_rate,
                    'step_number': i + 1
                }
            
            conn.close()
            
            return {
                'funnel_steps': funnel_data,
                'total_users': total_users,
                'final_conversion_rate': funnel_data[funnel_steps[-1]]['conversion_rate'] if funnel_steps else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze conversion funnel: {e}")
            return {}
    
    def get_analytics_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get comprehensive analytics summary."""
        cutoff_time = time.time() - (days * 24 * 3600)
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Basic metrics
            cursor = conn.execute('''
                SELECT COUNT(DISTINCT user_id) as unique_users,
                       COUNT(*) as total_sessions,
                       AVG(duration) as avg_session_duration,
                       AVG(page_views) as avg_page_views,
                       AVG(actions) as avg_actions
                FROM user_sessions
                WHERE start_time > ?
            ''', (cutoff_time,))
            
            basic_metrics = cursor.fetchone()
            
            # Top pages
            cursor = conn.execute('''
                SELECT page, SUM(views) as total_views
                FROM page_analytics
                WHERE date >= date('now', '-{} days')
                GROUP BY page
                ORDER BY total_views DESC
                LIMIT 5
            '''.format(days))
            
            top_pages = [{'page': row[0], 'views': row[1]} for row in cursor.fetchall()]
            
            # Device/browser stats (simplified)
            cursor = conn.execute('''
                SELECT CASE 
                    WHEN user_agent LIKE '%Mobile%' THEN 'Mobile'
                    WHEN user_agent LIKE '%Tablet%' THEN 'Tablet'
                    ELSE 'Desktop'
                END as device_type,
                COUNT(*) as count
                FROM user_sessions
                WHERE start_time > ?
                GROUP BY device_type
            ''', (cutoff_time,))
            
            device_stats = [{'device': row[0], 'count': row[1]} for row in cursor.fetchall()]
            
            conn.close()
            
            return {
                'period_days': days,
                'unique_users': basic_metrics[0] if basic_metrics else 0,
                'total_sessions': basic_metrics[1] if basic_metrics else 0,
                'avg_session_duration': basic_metrics[2] if basic_metrics else 0,
                'avg_page_views': basic_metrics[3] if basic_metrics else 0,
                'avg_actions': basic_metrics[4] if basic_metrics else 0,
                'top_pages': top_pages,
                'device_stats': device_stats
            }
            
        except Exception as e:
            logger.error(f"Failed to get analytics summary: {e}")
            return {}


# Global analytics instance
_user_analytics = None
_analytics_lock = threading.Lock()


def get_user_analytics() -> UserAnalytics:
    """Get the global user analytics instance."""
    global _user_analytics
    
    if _user_analytics is None:
        with _analytics_lock:
            if _user_analytics is None:
                _user_analytics = UserAnalytics()
    
    return _user_analytics


if __name__ == '__main__':
    # Example usage and testing
    analytics = UserAnalytics()
    
    # Simulate user activity
    session_id = 'test_session_123'
    user_id = 'test_user_456'
    
    # Start session
    analytics.start_session(session_id, user_id, '/home')
    
    # Track some activity
    analytics.track_page_view(session_id, '/problems', 30.0)
    analytics.track_user_action(session_id, 'view_problem', 'problem_viewer', 15.0, True)
    analytics.track_page_view(session_id, '/problem/1', 120.0)
    analytics.track_user_action(session_id, 'submit_code', 'code_editor', 45.0, True)
    
    # Track behavior pattern
    analytics.track_behavior_pattern(
        user_id, session_id, 'problem_solving',
        ['/problems', '/problem/1', 'submit_code'], 180.0, True
    )
    
    # End session
    analytics.end_session(session_id, '/submissions')
    
    # Get analytics
    summary = analytics.get_analytics_summary(1)
    print(f"Analytics Summary: {json.dumps(summary, indent=2, default=str)}")
    
    feature_stats = analytics.get_feature_usage_stats(1)
    print(f"Feature Usage: {json.dumps(feature_stats, indent=2, default=str)}")
    
    print("User analytics test completed!")