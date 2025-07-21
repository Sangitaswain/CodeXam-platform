"""
CodeXam Database Models
Provides database model classes for problems, submissions, and users
"""

import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from database import get_db, DatabaseError, dict_to_json, json_to_dict, validate_difficulty, validate_language, validate_result


class Problem:
    """
    Problem model class for managing coding problems.
    
    Handles problem creation, validation, storage, and retrieval.
    Supports multiple programming languages with function signatures.
    """
    
    def __init__(self, id: Optional[int] = None, title: str = "", description: str = "", 
                 difficulty: str = "Easy", function_signatures: Optional[Dict[str, str]] = None,
                 test_cases: Optional[List[Dict[str, Any]]] = None, sample_input: str = "",
                 sample_output: str = "", created_at: Optional[str] = None, 
                 updated_at: Optional[str] = None):
        """Initialize Problem instance."""
        self.id = id
        self.title = title.strip()
        self.description = description.strip()
        self.difficulty = difficulty
        self.function_signatures = function_signatures or {}
        self.test_cases = test_cases or []
        self.sample_input = sample_input.strip()
        self.sample_output = sample_output.strip()
        self.created_at = created_at
        self.updated_at = updated_at
    
    def validate(self) -> bool:
        """Validate problem data."""
        if not self.title or len(self.title.strip()) == 0:
            raise ValueError("Problem title cannot be empty")
        
        if len(self.title) > 100:
            raise ValueError("Problem title cannot exceed 100 characters")
        
        if not self.description or len(self.description.strip()) == 0:
            raise ValueError("Problem description cannot be empty")
        
        if not validate_difficulty(self.difficulty):
            raise ValueError(f"Invalid difficulty: {self.difficulty}")
        
        if not self.function_signatures:
            raise ValueError("At least one function signature is required")
        
        if not self.test_cases:
            raise ValueError("At least one test case is required")
        
        return True
    
    @classmethod
    def create(cls, title: str, description: str, difficulty: str,
               function_signatures: Dict[str, str], test_cases: List[Dict[str, Any]],
               sample_input: str = "", sample_output: str = "") -> 'Problem':
        """Create and save a new problem."""
        problem = cls(
            title=title,
            description=description,
            difficulty=difficulty,
            function_signatures=function_signatures,
            test_cases=test_cases,
            sample_input=sample_input,
            sample_output=sample_output
        )
        return problem.save()
    
    def save(self) -> 'Problem':
        """Save problem to database."""
        self.validate()
        db = get_db()
        
        try:
            if self.id is None:
                query = """
                INSERT INTO problems (title, description, difficulty, function_signatures, 
                                    test_cases, sample_input, sample_output)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                params = (
                    self.title, self.description, self.difficulty,
                    dict_to_json(self.function_signatures),
                    dict_to_json(self.test_cases),
                    self.sample_input, self.sample_output
                )
                self.id = db.execute_insert(query, params)
            else:
                query = """
                UPDATE problems 
                SET title = ?, description = ?, difficulty = ?, function_signatures = ?,
                    test_cases = ?, sample_input = ?, sample_output = ?
                WHERE id = ?
                """
                params = (
                    self.title, self.description, self.difficulty,
                    dict_to_json(self.function_signatures),
                    dict_to_json(self.test_cases),
                    self.sample_input, self.sample_output, self.id
                )
                db.execute_update(query, params)
            
            return self
        except Exception as e:
            raise DatabaseError(f"Failed to save problem: {e}")
    
    @classmethod
    def get_by_id(cls, problem_id: int) -> Optional['Problem']:
        """Get problem by ID."""
        db = get_db()
        try:
            query = "SELECT * FROM problems WHERE id = ?"
            row = db.execute_single(query, (problem_id,))
            if row:
                return cls.from_row(row)
            return None
        except Exception as e:
            raise DatabaseError(f"Failed to get problem: {e}")
    
    @classmethod
    def get_all(cls, difficulty: Optional[str] = None) -> List['Problem']:
        """Get all problems with optional difficulty filter."""
        db = get_db()
        try:
            if difficulty and validate_difficulty(difficulty):
                query = "SELECT * FROM problems WHERE difficulty = ? ORDER BY title"
                rows = db.execute_query(query, (difficulty,))
            else:
                query = "SELECT * FROM problems ORDER BY difficulty, title"
                rows = db.execute_query(query)
            
            return [cls.from_row(row) for row in rows]
        except Exception as e:
            raise DatabaseError(f"Failed to get problems: {e}")
    
    @classmethod
    def from_row(cls, row) -> 'Problem':
        """Create Problem instance from database row."""
        return cls(
            id=row['id'],
            title=row['title'],
            description=row['description'],
            difficulty=row['difficulty'],
            function_signatures=json_to_dict(row['function_signatures']),
            test_cases=json_to_dict(row['test_cases']),
            sample_input=row['sample_input'] or '',
            sample_output=row['sample_output'] or '',
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    def __str__(self) -> str:
        return f"Problem(id={self.id}, title='{self.title}', difficulty='{self.difficulty}')"


class Submission:
    """
    Submission model class for managing code submissions.
    """
    
    def __init__(self, id: Optional[int] = None, problem_id: int = 0, user_name: str = "",
                 language: str = "", code: str = "", result: str = "PENDING",
                 execution_time: float = 0.0, memory_used: int = 0, 
                 error_message: str = "", submitted_at: Optional[str] = None):
        """Initialize Submission instance."""
        self.id = id
        self.problem_id = problem_id
        self.user_name = user_name.strip()
        self.language = language.lower()
        self.code = code
        self.result = result
        self.execution_time = execution_time
        self.memory_used = memory_used
        self.error_message = error_message
        self.submitted_at = submitted_at
    
    def validate(self) -> bool:
        """Validate submission data."""
        if self.problem_id <= 0:
            raise ValueError("Problem ID must be positive")
        
        if not self.user_name or len(self.user_name.strip()) == 0:
            raise ValueError("User name cannot be empty")
        
        if not validate_language(self.language):
            raise ValueError(f"Unsupported language: {self.language}")
        
        if not self.code or len(self.code.strip()) == 0:
            raise ValueError("Code cannot be empty")
        
        if not validate_result(self.result):
            raise ValueError(f"Invalid result: {self.result}")
        
        return True
    
    @classmethod
    def create(cls, problem_id: int, user_name: str, language: str, code: str,
               result: str = "PENDING", execution_time: float = 0.0, 
               memory_used: int = 0, error_message: str = "") -> 'Submission':
        """Create and save a new submission."""
        submission = cls(
            problem_id=problem_id, user_name=user_name, language=language,
            code=code, result=result, execution_time=execution_time,
            memory_used=memory_used, error_message=error_message
        )
        return submission.save()
    
    def save(self) -> 'Submission':
        """Save submission to database."""
        self.validate()
        db = get_db()
        
        try:
            if self.id is None:
                query = """
                INSERT INTO submissions (problem_id, user_name, language, code, result,
                                       execution_time, memory_used, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """
                params = (
                    self.problem_id, self.user_name, self.language, self.code,
                    self.result, self.execution_time, self.memory_used, self.error_message
                )
                self.id = db.execute_insert(query, params)
            else:
                query = """
                UPDATE submissions 
                SET problem_id = ?, user_name = ?, language = ?, code = ?, result = ?,
                    execution_time = ?, memory_used = ?, error_message = ?
                WHERE id = ?
                """
                params = (
                    self.problem_id, self.user_name, self.language, self.code,
                    self.result, self.execution_time, self.memory_used, 
                    self.error_message, self.id
                )
                db.execute_update(query, params)
            
            return self
        except Exception as e:
            raise DatabaseError(f"Failed to save submission: {e}")
    
    @classmethod
    def get_by_id(cls, submission_id: int) -> Optional['Submission']:
        """Get submission by ID."""
        db = get_db()
        try:
            query = "SELECT * FROM submissions WHERE id = ?"
            row = db.execute_single(query, (submission_id,))
            if row:
                return cls.from_row(row)
            return None
        except Exception as e:
            raise DatabaseError(f"Failed to get submission: {e}")
    
    @classmethod
    def get_by_user(cls, user_name: str, limit: Optional[int] = None) -> List['Submission']:
        """Get submissions by user."""
        db = get_db()
        try:
            query = "SELECT * FROM submissions WHERE user_name = ? ORDER BY submitted_at DESC"
            params = [user_name]
            
            if limit:
                query += " LIMIT ?"
                params.append(limit)
            
            rows = db.execute_query(query, tuple(params))
            return [cls.from_row(row) for row in rows]
        except Exception as e:
            raise DatabaseError(f"Failed to get user submissions: {e}")
    
    @classmethod
    def get_leaderboard(cls, limit: int = 50) -> List[Dict[str, Any]]:
        """Get leaderboard data based on problems solved."""
        db = get_db()
        try:
            query = """
            SELECT 
                user_name,
                COUNT(DISTINCT CASE WHEN result = 'PASS' THEN problem_id END) as problems_solved,
                COUNT(*) as total_submissions
            FROM submissions 
            GROUP BY user_name
            ORDER BY problems_solved DESC, total_submissions ASC
            LIMIT ?
            """
            
            rows = db.execute_query(query, (limit,))
            leaderboard = []
            for i, row in enumerate(rows):
                leaderboard.append({
                    'rank': i + 1,
                    'user_name': row['user_name'],
                    'problems_solved': row['problems_solved'],
                    'total_submissions': row['total_submissions']
                })
            
            return leaderboard
        except Exception as e:
            raise DatabaseError(f"Failed to get leaderboard: {e}")
    
    @classmethod
    def from_row(cls, row) -> 'Submission':
        """Create Submission instance from database row."""
        return cls(
            id=row['id'],
            problem_id=row['problem_id'],
            user_name=row['user_name'],
            language=row['language'],
            code=row['code'],
            result=row['result'],
            execution_time=row['execution_time'] or 0.0,
            memory_used=row['memory_used'] or 0,
            error_message=row['error_message'] or '',
            submitted_at=row['submitted_at']
        )
    
    def __str__(self) -> str:
        return (f"Submission(id={self.id}, problem_id={self.problem_id}, "
                f"user='{self.user_name}', result='{self.result}')")


# Testing function
if __name__ == "__main__":
    print("🧪 Testing models...")
    try:
        # Test basic functionality
        print("✅ Models loaded successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")