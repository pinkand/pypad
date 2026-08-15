-- MySQL DDL Schema for PyPad
CREATE DATABASE IF NOT EXISTS pypad CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE pypad;

CREATE TABLE IF NOT EXISTS courses (
    id VARCHAR(64) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    cover_url VARCHAR(512),
    level VARCHAR(32) DEFAULT 'beginner',
    category VARCHAR(64) NOT NULL,
    sort_order INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS chapters (
    id VARCHAR(64) PRIMARY KEY,
    course_id VARCHAR(64) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    sort_order INT DEFAULT 0,
    INDEX idx_course_id (course_id),
    CONSTRAINT fk_chapters_course FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS sections (
    id VARCHAR(64) PRIMARY KEY,
    chapter_id VARCHAR(64) NOT NULL,
    title VARCHAR(255) NOT NULL,
    content_type VARCHAR(32) DEFAULT 'text',
    estimated_minutes INT DEFAULT 15,
    sort_order INT DEFAULT 0,
    INDEX idx_chapter_id (chapter_id),
    CONSTRAINT fk_sections_chapter FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS knowledge_nodes (
    id VARCHAR(64) PRIMARY KEY,
    code VARCHAR(64) UNIQUE,
    name VARCHAR(128) NOT NULL,
    description TEXT,
    category VARCHAR(64) NOT NULL,
    importance INT DEFAULT 5,
    course_id VARCHAR(64),
    chapter_id VARCHAR(64),
    section_id VARCHAR(64),
    parent_id VARCHAR(64),
    depth INT DEFAULT 0,
    pos_x FLOAT DEFAULT 0.0,
    pos_y FLOAT DEFAULT 0.0,
    pos_z FLOAT DEFAULT 0.0,
    ai_summary JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_section (section_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS knowledge_edges (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    source_id VARCHAR(64) NOT NULL,
    target_id VARCHAR(64) NOT NULL,
    relation_type VARCHAR(32) DEFAULT 'prerequisite',
    strength VARCHAR(16) DEFAULT 'hard',
    weight FLOAT DEFAULT 0.5,
    UNIQUE KEY uk_edge (source_id, target_id),
    INDEX idx_source (source_id),
    INDEX idx_target (target_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS projects (
    id VARCHAR(64) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    difficulty VARCHAR(32) DEFAULT 'easy',
    estimated_hours INT DEFAULT 2,
    init_code TEXT,
    readme_markdown LONGTEXT,
    test_cases JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS practices (
    id VARCHAR(64) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    type VARCHAR(32) NOT NULL DEFAULT 'fixed',
    difficulty VARCHAR(32) DEFAULT 'easy',
    knowledge_node_id VARCHAR(64) NOT NULL,
    project_id VARCHAR(64),
    prompt TEXT NOT NULL,
    starter_code TEXT,
    solution_code TEXT,
    test_cases JSON,
    ai_gen_params JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_practice_node (knowledge_node_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS learning_sessions (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    course_id VARCHAR(64),
    chapter_id VARCHAR(64),
    section_id VARCHAR(64),
    knowledge_node_id VARCHAR(64) NOT NULL,
    status VARCHAR(32) DEFAULT 'active',
    start_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_time DATETIME,
    total_duration_seconds INT DEFAULT 0,
    INDEX idx_user_session (user_id),
    INDEX idx_node_session (knowledge_node_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS session_event_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL,
    event_type VARCHAR(64) NOT NULL,
    payload JSON,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_session_events (session_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS workspace_runs (
    id VARCHAR(64) PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL,
    practice_id VARCHAR(64),
    code TEXT NOT NULL,
    language VARCHAR(32) DEFAULT 'python',
    status VARCHAR(32) NOT NULL,
    stdout LONGTEXT,
    stderr LONGTEXT,
    exit_code INT DEFAULT 0,
    runtime_ms INT DEFAULT 0,
    memory_bytes BIGINT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_run_session (session_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS code_reviews (
    id VARCHAR(64) PRIMARY KEY,
    workspace_run_id VARCHAR(64) UNIQUE NOT NULL,
    session_id VARCHAR(64) NOT NULL,
    overall_score INT NOT NULL DEFAULT 0,
    code_quality_score INT DEFAULT 0,
    logic_score INT DEFAULT 0,
    performance_score INT DEFAULT 0,
    ai_feedback TEXT,
    suggestions JSON,
    weakness_tags JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_review_session (session_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS user_mastery (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    knowledge_node_id VARCHAR(64) NOT NULL,
    mastery_score FLOAT DEFAULT 0.0,
    status VARCHAR(32) DEFAULT 'unlearned',
    last_studied_at DATETIME,
    UNIQUE KEY uk_user_node (user_id, knowledge_node_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS user_progress (
    user_id VARCHAR(64) PRIMARY KEY,
    current_course_id VARCHAR(64),
    current_session_id VARCHAR(64),
    overall_mastery FLOAT DEFAULT 0.0,
    study_streak_days INT DEFAULT 0,
    completed_projects_count INT DEFAULT 0,
    completed_practices_count INT DEFAULT 0,
    total_study_time_seconds BIGINT DEFAULT 0,
    weak_node_ids JSON,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
